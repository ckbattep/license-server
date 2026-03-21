from fastapi import APIRouter
from app.security.ed25519 import sign_payload

router = APIRouter()

@router.get("/test-sign")
def test():
    return sign_payload({"test": "ok"})