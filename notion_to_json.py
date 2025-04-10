import os
import json
from notion_client import Client
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Category icons (customize as needed)
CATEGORY_ICONS = {
    "Hosting": "🌐",
    "Development": "💻",
    "Social Media": "📱",
    "Business Tools": "🧰",
    "Uncategorized": "🧩"
}

def sanitize_data(data):
    """Remove or mask sensitive fields before saving to JSON"""
    for category in data.values():
        for entry in category:
            # Always mask passwords
            if 'password' in entry:
                entry['password'] = '••••••••' if entry['password'] else '[NONE]'
            
            # Redact notes containing sensitive keywords
            sensitive_keywords = ['password', 'key', 'secret', 'token', 'login']
            if 'notes' in entry:
                notes_lower = entry['notes'].lower()
                if any(keyword in notes_lower for keyword in sensitive_keywords):
                    entry['notes'] = '[REDACTED - CONTAINS SENSITIVE INFO]'
    return data

def get_property_value(prop, prop_type='text'):
    """Safely extract Notion property values"""
    try:
        if not prop:
            return ''
        if prop_type == 'title':
            return prop['title'][0]['plain_text'] if prop.get('title') else ''
        elif prop_type == 'text':
            return prop['rich_text'][0]['plain_text'] if prop.get('rich_text') else ''
        elif prop_type == 'select':
            return prop['select']['name'] if prop.get('select') else 'Uncategorized'
        return ''
    except Exception as e:
        logger.warning(f"Property parse error: {e}")
        return ''

def fetch_notion_database(database_id, notion):
    """Fetch all pages from Notion database"""
    results = []
    next_cursor = None
    
    while True:
        try:
            response = notion.databases.query(
                database_id=database_id,
                start_cursor=next_cursor
            )
            results.extend(response.get('results', []))
            if not response.get('has_more'):
                break
            next_cursor = response.get('next_cursor')
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            break
    
    logger.info(f"Fetched {len(results)} pages from Notion")
    return results

def transform_data(pages):
    """Convert Notion pages to structured data"""
    structured_data = {}
    
    for page in pages:
        try:
            props = page.get('properties', {})
            service = get_property_value(props.get('Service'), 'title')
            if not service:
                continue
                
            category = get_property_value(props.get('Category'), 'select') or "Uncategorized"
            icon = CATEGORY_ICONS.get(category, "🧩")
            
            entry = {
                'service': service,
                'description': get_property_value(props.get('Description'), 'text'),
                'username': get_property_value(props.get('Username'), 'text'),
                'password': get_property_value(props.get('Password'), 'text'),  # Will be sanitized later
                'notes': get_property_value(props.get('Notes'), 'text'),       # Will be sanitized later
                'icon': icon
            }
            
            if category not in structured_data:
                structured_data[category] = []
            structured_data[category].append(entry)
            
        except Exception as e:
            logger.error(f"Error processing page {page.get('id')}: {e}")
            continue
    
    return structured_data

def main():
    """Main execution flow"""
    load_dotenv()
    
    notion_token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    if not notion_token or not database_id:
        logger.error("Missing NOTION_TOKEN or NOTION_DATABASE_ID in environment")
        return

    try:
        notion = Client(auth=notion_token)
        pages = fetch_notion_database(database_id, notion)
        mindmap_data = transform_data(pages)
        
        # Sanitize sensitive data before saving
        sanitized_data = sanitize_data(mindmap_data)
        
        # Write to output directory
        output_dir = 'docs'  # Change to 'public' if using Netlify
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, 'mindmap_data.json')
        with open(output_path, 'w') as f:
            json.dump(sanitized_data, f, indent=2)
        
        logger.info(f"Successfully wrote sanitized data to {output_path}")
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise

if __name__ == '__main__':
    main()
