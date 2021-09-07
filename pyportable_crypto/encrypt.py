from Cryptodome import Random
from Cryptodome.Cipher import AES


def encrypt_file(file_i, file_o, key: str):
    with open(file_i, 'rb') as r:
        data = r.read()
    with open(file_o, 'wb') as w:
        w.write(encrypt(data, key))


def encrypt(data: bytes, key: str):
    random_iv = Random.new().read(AES.block_size)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, random_iv)
    padding_length = AES.block_size - (len(data) % AES.block_size)
    data += bytes([padding_length]) * padding_length
    data = random_iv + data
    data = cipher.encrypt(data)
    return data
