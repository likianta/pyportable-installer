from base64 import b64encode
from hashlib import sha256
from os import urandom

from Cryptodome.Cipher import AES


def encrypt_file(file_i, file_o, key: str):
    with open(file_i, 'r', encoding='utf-8') as r:
        data = r.read()
    with open(file_o, 'wb') as w:
        w.write(encrypt_data(data, key))
    return file_o


def encrypt_data(data: str, key: str) -> bytes:
    data = _pad(data).encode('utf-8')  # type: bytes
    key = sha256(key.encode('utf-8')).digest()  # type: bytes
    iv = urandom(AES.block_size)  # type: bytes
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(data))


def _pad(s: str, size=AES.block_size) -> str:
    # sometimes len(s) doesn't equal to len(s.encode()), we should use bytes
    # length here.
    bytelen = len(s.encode('utf-8'))
    return s + (size - bytelen % size) * chr(size - bytelen % size)
