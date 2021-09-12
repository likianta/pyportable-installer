"""
References:
    https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto
        -aes-256
"""
from . import keygen
from .decrypt import decrypt_data
from .decrypt import decrypt_file
from .encrypt import encrypt_data
from .encrypt import encrypt_file
from .inject import inject

__version__ = '0.1.1'
