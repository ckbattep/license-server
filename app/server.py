# app/server.py

from flask import Flask, request, jsonify, render_template
import os
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, r"C:\IT\CitoLaw\license-server")

from app.security.ed25519 import sign_payload, verify_signature

app = Flask(__name__)

# 🔒 API Key — из env или fallback (dev)
API_KEY = os.getenv("LICENSE_API_KEY", "dev-key-123")  # ⚠️ в prod замени на случайный!

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/verify', methods=['POST'])
def verify_api():
    key = request.headers.get('X-API-Key')
    if not key or key != API_KEY:
        return jsonify({"error": "Unauthorized: invalid X-API-Key"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload"}), 400

    payload = data.get("payload")
    signature = data.get("signature")

    if not payload or not signature:
        return jsonify({"error": "Missing 'payload' or 'signature'"}), 400

    try:
        ok = verify_signature(payload, signature)
        return jsonify({"valid": ok})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_api():
    data = request.get_json() or {}
    license_data = {
        "id": f"LIC-{datetime.now().strftime('%Y-%m-%d')}-001",
        "user": data.get("user", "CitoLaw"),
        "product": data.get("product", "License Server v1.0"),
        "expires": (datetime.utcnow() + timedelta(days=365)).isoformat() + "Z",
        "features": data.get("features", ["api", "web"]),
        "signature_algorithm": "ed25519"
    }

    signed = sign_payload(license_data)
    sig_b64 = signed["signature"]

    os.makedirs("app/licenses", exist_ok=True)
    with open(f"app/licenses/{license_data['id']}.json", "w") as f:
        json.dump(license_data, f, indent=2, sort_keys=True)
    with open(f"app/licenses/{license_data['id']}.sig", "w") as f:
        f.write(sig_b64)

    return jsonify({
        "id": license_data["id"],
        "signature": sig_b64,
        "valid": True
    })


@app.route('/api/list', methods=['GET'])
def list_licenses_api():
    licenses = []
    for f in os.listdir("app/licenses"):
        if f.endswith(".json"):
            with open(f"app/licenses/{f}") as fp:
                licenses.append(json.load(fp))
    return jsonify({"licenses": licenses})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)