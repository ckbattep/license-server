from fastapi import APIRouter

router = APIRouter()

@router.get("/config")
def get_config():
    return {
        "app_enabled": True,
        "min_version": 1,
        "kill_switch": False
    }