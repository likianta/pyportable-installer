from base64 import b64decode
from hashlib import sha256

from Cryptodome.Cipher import AES


def decrypt_file(file_i, file_o=None, key=None) -> str:
    if not key:
        raise Exception
    with open(file_i, 'rb') as f:
        data = f.read()
    data = decrypt_data(data, key)
    if file_o:
        with open(file_o, 'w', encoding='utf-8') as f:
            f.write(data)
    return data


def decrypt_data(data: bytes, key: str) -> str:
    data = b64decode(data)  # type: bytes
    key = sha256(key.encode('utf-8')).digest()  # type: bytes

    iv = data[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return _unpad(cipher.decrypt(data[AES.block_size:])).decode('utf-8')


def _unpad(s: bytes) -> bytes:
    return s[:-ord(s[len(s) - 1:])]
