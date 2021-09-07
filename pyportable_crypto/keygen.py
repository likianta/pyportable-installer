from uuid import uuid1

from Cryptodome.Hash import SHA256


def generate_random_key(seed: str):
    return SHA256.new((seed or str(uuid1())).encode('utf-8')).digest()
