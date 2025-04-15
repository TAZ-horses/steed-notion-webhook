import os
import sys
import json
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables (from .env locally or GitHub Actions env)
load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))

def fetch_notion_data(database_id):
    try:
        results = notion.databases.query(database_id=database_id)["results"]
        grouped = {}
        for page in results:
            # Safely access the page properties
            props = page.get("properties", {})
            category = props.get("Category", {}).get("select", {}).get("name", "uncategorised")
            entry = {
                "service": props.get("Service", {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                "username": props.get("Username", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                "password": props.get("Password", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                "notes": props.get("Notes", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                "description": props.get("Description", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
            }
            # Optionally skip entries with no service, so as not to pollute the JSON:
            if entry["service"]:
                grouped.setdefault(category, []).append(entry)
            else:
                print(f"[⚠️] Skipping page {page.get('id')} because it has no service name.")
        return grouped
    except Exception as e:
        print(f"[❌] Notion fetch error: {e}")
        return {}

def save_json(data, path="docs/mindmap_data.json"):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[✅] mindmap_data.json successfully written to: {path}")
    except Exception as e:
        print(f"[❌] Failed to write JSON: {e}")

if __name__ == "__main__":
    db_id = os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        print("[❌] NOTION_DATABASE_ID not set in environment variables.")
        sys.exit(1)

    output_path = "docs/mindmap_data.json"
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    data = fetch_notion_data(db_id)
    save_json(data, output_path)
