"""
Requirements:
    pycryptodomex
"""
from .decrypt import decrypt as decrypt_data
from .decrypt import decrypt_file
from .encrypt import encrypt as encrypt_data
from .encrypt import encrypt_file
from .inject import inject
from .keygen import generate_random_key
