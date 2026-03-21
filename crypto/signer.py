from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import base64

with open("crypto/ed25519_private.key", "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )

def sign_hash(hash_value: str) -> str:
    signature = private_key.sign(hash_value.encode("utf-8"))
    return base64.b64encode(signature).decode("ascii")