from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.security.ed25519 import verify_signature

router = APIRouter()


class VerifyRequest(BaseModel):
    payload: dict
    signature: str


class VerifyResponse(BaseModel):
    valid: bool
    reason: str | None = None


@router.post("/verify-license", response_model=VerifyResponse)
def verify_license(req: VerifyRequest):
    try:
        # 1️⃣ Проверка подписи
        is_valid = verify_signature(req.payload, req.signature)

        if not is_valid:
            return {"valid": False, "reason": "invalid_signature"}

        # 2️⃣ Проверка срока действия
        expires_at = datetime.fromisoformat(req.payload["expires_at"])

        if datetime.utcnow() > expires_at:
            return {"valid": False, "reason": "expired"}

        return {"valid": True, "reason": None}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))