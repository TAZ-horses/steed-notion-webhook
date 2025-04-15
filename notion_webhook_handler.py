import os
import hmac
import hashlib
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

NOTION_SECRET = os.getenv('NOTION_SECRET')

def verify_signature(request):
    signature = request.headers.get('X-Notion-Signature')
    if not signature or not NOTION_SECRET:
        return False
    computed_signature = hmac.new(
        NOTION_SECRET.encode(),
        msg=request.data,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    if not verify_signature(request):
        abort(401, description='Unauthorized')
    data = request.get_json()
    if not data:
        abort(400, description='Invalid payload')
    # TODO: process webhook data here
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)
