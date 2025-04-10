import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

# Securely verify Notion webhooks
WEBHOOK_SECRET = os.getenv('NOTION_WEBHOOK_SECRET')  # Must match Notion's secret

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verify the webhook signature
    if request.headers.get('X-Notion-Signature') != WEBHOOK_SECRET:
        return 'Unauthorized', 403

    try:
        # Run your Notion-to-JSON script
        subprocess.run(['python', 'scripts/notion_to_json.py'], check=True)
        
        # Push changes to GitHub (if needed)
        subprocess.run(['git', 'config', '--global', 'user.name', 'Render Webhook'])
        subprocess.run(['git', 'config', '--global', 'user.email', 'render@example.com'])
        subprocess.run(['git', 'add', 'docs/mindmap_data.json'])
        subprocess.run(['git', 'commit', '-m', 'Auto-update mindmap data via Notion webhook'])
        subprocess.run(['git', 'push'])
        
        return '✅ Mindmap data updated!', 200
    except Exception as e:
        return f'❌ Error: {str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
