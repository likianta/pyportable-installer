from Cryptodome.Cipher import AES


def decrypt_file(file_i, file_o=None, key=None) -> str:
    if not key:
        raise Exception
    with open(file_i, 'rb') as f:
        data = f.read()
    data = decrypt(data, key)
    if file_o:
        with open(file_o, 'w', encoding='utf-8') as f:
            f.write(data)
    return data


def decrypt(data: bytes, key: str) -> str:
    random_iv = data[:16]
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, random_iv)
    data = cipher.decrypt(data)
    return data.decode('utf-8')
