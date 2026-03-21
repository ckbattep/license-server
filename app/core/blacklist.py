BLACKLIST = {
    "TEST-REVOKED-123"
}

def is_revoked(key: str) -> bool:
    return key in BLACKLIST