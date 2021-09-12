import secrets


def generate_random_key(bytelen=32) -> str:
    assert bytelen % 2 == 0
    return secrets.token_hex(int(bytelen / 2))


def generate_random_bytes(n=32) -> bytes:
    return secrets.SystemRandom().randbytes(n)
