import os
import sys
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))

def fetch_notion_data(database_id):
    try:
        results = notion.databases.query(database_id=database_id)["results"]
        grouped = {}
        for page in results:
            props = page["properties"]
            category = props.get("Category", {}).get("select", {}).get("name", "uncategorised")
            entry = {
                "service": props.get("Service", {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                "username": props.get("Username", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                "password": props.get("Password", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                "notes": props.get("Notes", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                "description": props.get("Description", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
            }
            grouped.setdefault(category, []).append(entry)
        return grouped
    except Exception as e:
        print(f"[❌] Notion fetch error: {e}")
        return {}

def save_json(data, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[✅] Saved to {path}")
    except Exception as e:
        print(f"[❌] Failed to write file: {e}")

if __name__ == "__main__":
    db_id = os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        print("[❌] NOTION_DATABASE_ID not set.")
        exit(1)

    output_file = "docs/mindmap_data.json"
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    data = fetch_notion_data(db_id)
    save_json(data, output_file)
