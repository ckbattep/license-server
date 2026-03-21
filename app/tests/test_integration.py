# app/tests/test_integration.py

"""
🧪 Интеграционный тест: подпись и верификация реальной лицензии.
"""

import sys
import os
import json

# 🔧 Явно задаём путь к корню проекта (работает всегда)
PROJECT_ROOT = r"C:\IT\CitoLaw\license-server"
sys.path.insert(0, PROJECT_ROOT)

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def generate_and_save_keys():
    """
    🔑 Генерирует ключи, если их нет (для теста).
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key  = private_key.public_key()

    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    os.makedirs("app/crypto", exist_ok=True)

    with open("app/crypto/ed25519_private.key", "wb") as f:
        f.write(pem_private)
    with open("app/crypto/ed25519_public.key",  "wb") as f:
        f.write(pem_public)


def sign_and_save_license():
    """
    📄 Генерирует лицензию, подписывает и сохраняет.
    """
    license_data = {
        "id": "LIC-2026-03-21-001",
        "user": "CitoLaw",
        "product": "License Server v1.0",
        "expires": "2027-03-21T00:00:00Z",
        "features": ["api", "web", "cli"],
        "signature_algorithm": "ed25519"
    }

    os.makedirs("app/licenses", exist_ok=True)

    # Сохраняем license.json (canonical JSON — sort_keys=True)
    with open("app/licenses/lic_2026-03-21-001.json", "w", encoding="utf-8") as f:
        json.dump(license_data, f, indent=2, sort_keys=True)

    # Подписываем
    from app.security.ed25519 import sign_payload

    signed = sign_payload(license_data)
    sig_b64 = signed["signature"]

    # Сохраняем signature.txt
    with open("app/licenses/lic_2026-03-21-001.sig", "w") as f:
        f.write(sig_b64)

    return license_data, sig_b64


def verify_license():
    """
    🔍 Верифицирует лицензию.
    """
    from app.security.ed25519 import verify_signature

    with open("app/licenses/lic_2026-03-21-001.json", "r", encoding="utf-8") as f:
        license_data = json.load(f)

    with open("app/licenses/lic_2026-03-21-001.sig", "r") as f:
        sig_b64 = f.read()

    ok = verify_signature(license_data, sig_b64)
    return ok


if __name__ == "__main__":
    print("🧪 Интеграционный тест: подпись и верификация лицензии")

    # 🔑 Генерируем ключи (если нет)
    if not os.path.exists("app/crypto/ed25519_private.key"):
        generate_and_save_keys()
        print("✅ Ключи сгенерированы.")

    # 📄 Подписываем лицензию
    license_data, sig_b64 = sign_and_save_license()
    print(f"✅ Лицензия подписана: {license_data['id']}")
    print(f"   • app/licenses/lic_2026-03-21-001.json")
    print(f"   • app/licenses/lic_2026-03-21-001.sig")

    # 🔍 Верифицируем
    ok = verify_license()
    if ok:
        print("✅ verify_signature() → True")
    else:
        raise RuntimeError("❌ verify_signature() failed!")