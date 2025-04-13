iimport os
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
print(json.dumps(data, indent=2))
import sys

output_file = "docs/mindmap_data.json"
if "--output" in sys.argv:
    i = sys.argv.index("--output")
    if i + 1 < len(sys.argv):
        output_file = sys.argv[i + 1]

save_json(data, path=output_file)

if __name__ == "__main__":
    db_id = os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        print("[❌] NOTION_DATABASE_ID is not set in the environment variables.")
        exit(1)

    data = fetch_notion_data(db_id)
    save_json(data)
