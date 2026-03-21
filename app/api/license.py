import time
import hashlib

from fastapi import APIRouter
from app.security.ed25519 import sign_payload
from app.models.license import LicenseResponse, LicensePayload
from app.core.blacklist import is_revoked

router = APIRouter()


@router.post("/activate", response_model=LicenseResponse)
def activate(data: dict):
    license_key = data.get("license_key")
    device_id = data.get("device_id")
    if is_revoked(license_key):
    return {
        "payload": {"status": "revoked"},
        "signature": ""
    }
    payload = {
        "license_key": license_key,
        "status": "active",
        "device_id": device_id,
        "issued_at": int(time.time()),
        "expires_at": int(time.time()) + 31536000,
        "features": ["pro", "expert"]
    }

    signature = sign_payload(payload)

    return {
        "payload": payload,
        "signature": signature
    }