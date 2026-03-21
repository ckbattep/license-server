from fastapi import APIRouter

router = APIRouter()

@router.post("/integrity-check")
def integrity_check(data: dict):
    token = data.get("token")

    # TODO: verify via Google API (production)
    return {"status": "ok"}