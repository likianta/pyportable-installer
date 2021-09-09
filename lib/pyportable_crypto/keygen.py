from uuid import uuid1


def generate_random_key() -> str:
    return str(uuid1())


# def generate_random_keygen(seed: str, step: int, elements):
#     pass
