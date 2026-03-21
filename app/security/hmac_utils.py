import hmac
import hashlib
import base64
import time
import uuid

SECRET = b"SUPER_SECRET_KEY_CHANGE_ME"

def sign_response(payload: str):
    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())

    message = f"{payload}|{timestamp}|{nonce}".encode()

    signature = hmac.new(
        SECRET,
        message,
        hashlib.sha256
    ).digest()

    return {
        "payload": payload,
        "timestamp": timestamp,
        "nonce": nonce,
        "signature": base64.b64encode(signature).decode()
    }