# app/security/ed25519.py

"""
🔐 CitoLaw License Server — Ed25519 Signature Module

Этот модуль реализует:
- генерацию и хранение ключей (PKCS8 + SPKI в PEM)
- подпись JSON-объектов через canonical JSON (RFC 8785-style)
- верификацию подписи без зависимости от алгоритма (Ed25519() не нужен)

📌 Контекст:
- Ed25519 — современный, быстрый и безопасный алгоритм (RFC 8032).
- canonical_json — гарантирует, что JSON с одинаковыми данными,
  но разным порядком ключей, будет подписан одинаково.
- cryptography >= 40 — упрощённый API: sign(message) без Ed25519().

⚠️ Важно:
- Не используйте `Ed25519()` в `.sign()` / `.verify()` — это вызовет AttributeError.
- Функция verify_signature(payload, signature_b64) — единственная версия для API.
"""

import json
import base64
import os
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


# 🔑 Ключи лежат в `app/crypto/`
PRIVATE_KEY_PATH = os.getenv(
    "ED25519_PRIVATE_KEY",
    os.path.join(os.path.dirname(__file__), "..", "crypto", "ed25519_private.key")
)
PUBLIC_KEY_PATH = os.getenv(
    "ED25519_PUBLIC_KEY",
    os.path.join(os.path.dirname(__file__), "..", "crypto", "ed25519_public.key")
)

# =========================
# 🛠️ Генерация и сохранение ключей
# =========================

def generate_and_save_keys():
    """
    🔑 Генерирует новую пару Ed25519-ключей и сохраняет их в PEM-формате.

    - Private key: PKCS8 (универсальный, поддерживается всеми библиотеками)
    - Public key:  SPKI (SubjectPublicKeyInfo — стандарт для публичных ключей)

    📁 Файлы:
    - app/crypto/ed25519_private.key
    - app/crypto/ed25519_public.key

    ⚠️ Не сохраняйте private key в Git или открытые репозитории!
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key  = private_key.public_key()

    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()  # 🔒 без пароля (для dev)
    )

    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    os.makedirs(os.path.dirname(PRIVATE_KEY_PATH), exist_ok=True)

    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(pem_private)
    with open(PUBLIC_KEY_PATH,  "wb") as f:
        f.write(pem_public)


def load_private_key() -> ed25519.Ed25519PrivateKey:
    """
    🔑 Загружает приватный ключ из файла.

    📌 Используется в sign_payload().
    ⚠️ Если файл не найден — генерирует ошибку с подсказкой.
    """
    try:
        with open(PRIVATE_KEY_PATH, "rb") as f:
            pem_data = f.read()
    except FileNotFoundError:
        raise RuntimeError(
            f"Private key not found at {PRIVATE_KEY_PATH}. "
            "Run `generate_and_save_keys()` first."
        )

    return serialization.load_pem_private_key(pem_data, password=None)


def load_public_key() -> ed25519.Ed25519PublicKey:
    """
    🔑 Загружает публичный ключ из файла.

    📌 Используется в verify_signature().
    ⚠️ Если файл не найден — генерирует ошибку с подсказкой.
    """
    try:
        with open(PUBLIC_KEY_PATH, "rb") as f:
            pem_data = f.read()
    except FileNotFoundError:
        raise RuntimeError(
            f"Public key not found at {PUBLIC_KEY_PATH}. "
            "Run `generate_and_save_keys()` first."
        )

    return serialization.load_pem_public_key(pem_data)


# =========================
# 📜 Canonical JSON — стандартизация JSON для подписи
# =========================

def canonical_json(data: dict) -> bytes:
    """
    📜 Преобразует dict в канонический JSON-строку (bytes).

    🔍 Правила:
    - sort_keys=True → ключи всегда в алфавитном порядке;
    - separators=(",", ":") → убирает лишние пробелы;
    - ensure_ascii=False → сохраняет Unicode (например, кириллица).

    📌 Зачем?
    Без canonical JSON:
        {"a":1,"b":2} ≠ {"b":2,"a":1}
    С canonical JSON:
        {"a":1,"b":2} = {"b":2,"a":1}

    ✅ Это гарантирует, что подпись не зависит от порядка ключей.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


# =========================
# 🔐 Подпись JSON-объекта (Ed25519 — без Ed25519() в cryptography >= 40)
# =========================

def sign_payload(payload: dict) -> dict:
    """
    🔐 Подписывает JSON-объект и возвращает структуру с подписью.

    📌 Вход:
        payload = {"user": "admin", "action": "login"}

    📌 Выход:
        {
            "payload": {...},
            "signature": "base64-encoded-bytes",
            "algorithm": "ed25519"
        }

    🔍 Логика:
    1. canonical_json(payload) → bytes
    2. private_key.sign(message) → signature (bytes)
    3. base64.encode(signature) → string

    ⚠️ Важно: cryptography >= 40 — sign() без Ed25519()
    """
    private_key = load_private_key()
    message       = canonical_json(payload)

    signature     = private_key.sign(message)  # ✅ без Ed25519()

    signature_b64 = base64.b64encode(signature).decode()

    return {
        "payload": payload,
        "signature": signature_b64,
        "algorithm": "ed25519"
    }


# =========================
# 🔍 Верификация подписи (единая версия — для API)
# =========================

def verify_signature(payload: dict, signature_b64: str) -> bool:
    """
    🔍 Проверяет, что подпись соответствует payload.

    📌 Вход:
        payload = {"user": "admin", "action": "login"}
        signature_b64 = "base64-encoded-bytes"

    📌 Выход:
        True / False

    🔍 Логика:
    1. canonical_json(payload) → bytes
    2. base64.decode(signature_b64) → signature (bytes)
    3. public_key.verify(signature, message) → True/False

    ⚠️ Важно: cryptography >= 40 — verify() без Ed25519()
    """
    public_key = load_public_key()
    message      = canonical_json(payload)

    try:
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, message)  # ✅ без Ed25519()
        return True
    except Exception:
        return False


# =========================
# 🔧 Вспомогательные функции (не конфликтуют с основными API)
# =========================

def generate_keypair():
    """
    🛠️ Генерирует ключи и возвращает PEM-строки (для CLI/отладки).
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key  = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_pem, public_pem


def load_private_key_from_pem(pem_str: str):
    """
    🛠️ Загружает приватный ключ из PEM-строки (для CLI/отладки).
    """
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    return load_pem_private_key(
        pem_str.encode('utf-8'),
        password=None
    )


def load_public_key_from_pem(pem_str: str):
    """
    🛠️ Загружает публичный ключ из PEM-строки (для CLI/отладки).
    """
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    return load_pem_public_key(
        pem_str.encode('utf-8')
    )


def sign_message(private_key, message: bytes) -> bytes:
    """
    🛠️ Подписывает raw bytes (для CLI/отладки).
    """
    return private_key.sign(message)


def verify_signature_bytes(public_key, signature: bytes, message: bytes) -> bool:
    """
    🛠️ Верифицирует raw bytes (для CLI/отладки).
    """
    try:
        public_key.verify(signature, message)
        return True
    except Exception:
        return False


# Пример использования (если запустить как скрипт):
if __name__ == "__main__":
    priv_pem, pub_pem = generate_keypair()
    print("✅ Private key:")
    print(priv_pem)

    print("\n✅ Public key:")
    print(pub_pem)