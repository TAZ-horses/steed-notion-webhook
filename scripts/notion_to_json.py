import os
import sys
import json
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables from .env or GitHub Actions
load_dotenv()

# Initialize Notion client with secret token
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def fetch_notion_data(database_id: str) -> dict:
    """
    Fetches and structures data from the specified Notion database.
    Returns a dictionary grouped by 'Category'.
    """
    try:
        response = notion.databases.query(database_id=database_id)
        results = response.get("results", [])
        grouped = {}

        for page in results:
            props = page.get("properties", {})

            category = props.get("Category", {}).get("select", {}).get("name", "Uncategorised")

            try:
                entry = {
                    "service": props.get("Service", {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                    "username": props.get("Username", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                    "password": props.get("Password", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                    "notes": props.get("Notes", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                    "description": props.get("Description", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
                }

                # Only include if there's a service name
                if entry["service"]:
                    grouped.setdefault(category, []).append(entry)

            except Exception as inner_error:
                print(f"[⚠️] Skipped a page due to missing or malformed fields: {inner_error}")
                continue

        return grouped

    except Exception as e:
        print(f"[❌] Notion fetch error: {e}")
        return {}

def save_json(data: dict, path: str = "docs/mindmap_data.json") -> None:
    """
    Saves the given data dictionary as a JSON file to the specified path.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[✅] mindmap_data.json successfully written to: {path}")
    except Exception as e:
        print(f"[❌] Failed to write JSON to {path}: {e}")

if __name__ == "__main__":
    # Grab Notion DB ID from env
    db_id = os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        print("[❌] Environment variable 'NOTION_DATABASE_ID' is not set.")
        sys.exit(1)

    # Parse optional --output path from command line
    output_file = "docs/mindmap_data.json"
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    # Fetch and write data
    data = fetch_notion_data(db_id)
    save_json(data, path=output_file)
