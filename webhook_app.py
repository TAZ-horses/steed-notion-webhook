from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Steed Webhook App is live!", 200

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

if __name__ == "__main__":
    app.run(debug=True)
