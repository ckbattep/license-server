from nacl.signing import SigningKey

# генерация
signing_key = SigningKey.generate()
verify_key = signing_key.verify_key

# сохранение (ВАЖНО: бинарно!)
with open("ed25519_private.key", "wb") as f:
    f.write(signing_key.encode())  # 32 bytes

with open("ed25519_public.key", "wb") as f:
    f.write(verify_key.encode())  # 32 bytes

print("Keys generated | Ключи созданы")