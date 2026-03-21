from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

from app.security.ed25519 import sign_payload

router = APIRouter()

# =========================
# REQUEST MODEL
# =========================
class LicenseRequest(BaseModel):
    user_id: str
    device_id: str
    plan: str  # basic / pro / expert


# =========================
# RESPONSE MODEL
# =========================
class LicenseResponse(BaseModel):
    payload: dict
    signature: str


# =========================
# SIGN LICENSE
# =========================
@router.post("/sign-license", response_model=LicenseResponse)
def sign_license(req: LicenseRequest):
    try:
        now = datetime.utcnow()
        expires = now + timedelta(days=30)

        payload = {
            "license_id": str(uuid.uuid4()),
            "user_id": req.user_id,
            "device_id": req.device_id,
            "plan": req.plan,
            "issued_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "issuer": "citolaw-license-server"
        }

        signed = sign_payload(payload)

        return signed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# TEST SIGN (оставляем)
# =========================
@router.get("/test-sign")
def test_sign():
    return sign_payload({
        "status": "active",
        "test": True
    })