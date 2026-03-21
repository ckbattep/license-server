# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✔ правильные импорты
from app.api.verify import router as verify_router
from app.api.sign import router as sign_router

app = FastAPI(
    title="CitoLaw License & Audit API",
    description="License verification and audit signature (Ed25519)",
    version="2.0.0"
)

# CORS (для Android достаточно оставить *)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✔ Роутеры подключаются ПОСЛЕ создания app
app.include_router(sign_router, prefix="/api/v1")
app.include_router(verify_router, prefix="/api/v1")


# health-check (обязательно для диагностики)
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "citolaw-license-server"
    }


# root
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "CitoLaw API running"
    }
    
app.include_router(license_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": "citolaw-license-server"}