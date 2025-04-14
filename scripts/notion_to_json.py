import os
import sys
import json
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def fetch_notion_data(database_id):
    try:
        results = notion.databases.query(database_id=database_id)["results"]
        grouped = {}

        for page in results:
            try:
                props = page.get("properties", {})
                category = props.get("Category", {}).get("select", {}).get("name", "uncategorised")

                service = props.get("Service", {}).get("title", [{}])[0].get("text", {}).get("content", "")
                username = props.get("Username", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
                password = props.get("Password", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
                notes = props.get("Notes", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
                description = props.get("Description", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")

                # Only include if there's at least a service name
                if not service:
                    print(f"[⚠️] Skipping entry with no service name: {page.get('id')}")
                    continue

                entry = {
                    "service": service,
                    "username": username,
                    "password": password,
                    "notes": notes,
                    "description": description
                }

                grouped.setdefault(category, []).append(entry)

            except Exception as entry_error:
                print(f"[⚠️] Skipped invalid entry due to error: {entry_error}")
                continue

        return grouped

    except Exception as e:
        print(f"[❌] Notion fetch error: {e}")
        return {}

def save_json(data, path="docs/mindmap_data.json"):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[✅] mindmap_data.json updated at {path}")
    except Exception as e:
        print(f"[❌] Failed to write JSON: {e}")

if __name__ == "__main__":
    db_id = os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        print("[❌] NOTION_DATABASE_ID is not set in environment variables.")
        exit(1)

    output_file = "docs/mindmap_data.json"
    if "--output" in sys.argv:
        i = sys.argv.index("--output")
        if i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]

    data = fetch_notion_data(db_id)
    save_json(data, path=output_file)
