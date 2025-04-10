from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Steed Webhook App is live!", 200

# Endpoint for webhook to trigger GitHub Action
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if not GITHUB_REPO or not GITHUB_TOKEN:
            return "Missing config", 500

        dispatch_url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        payload = {
            "event_type": "notion_sync"
        }

        r = requests.post(dispatch_url, headers=headers, json=payload)
        r.raise_for_status()

        return jsonify({"message": "GitHub Action triggered"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to serve mindmap data to Square Online page
@app.route("/get_mindmap_data", methods=["GET"])
def get_mindmap_data():
    try:
        # URL of the mindmap data stored on your server
        url = "https://steed-notion-webhook.onrender.com/mindmap_data_synced.json"
        
        # Fetch the mindmap data
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Failed to fetch mindmap data"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
