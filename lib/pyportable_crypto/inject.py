from base64 import b64decode
from hashlib import sha256
from re import sub
from textwrap import dedent

from Cryptodome.Cipher import AES


def __example_keygen() -> str:
    """
    All reverse and anti-reverse engineer battles focus on how to get the real
    key from keygen function.
    The example keygen function just returns real key to the caller, this is a
    very dangerous operation, the real key mustn't be put in the script
    directly, no matter if we compile this file to '.pyd' or '.so' etc.
    """
    
    # def _invalidate():
    #     pass
    
    # FIXME: use a more complicated method to generate KEY in runtime!
    return '{KEY}'
    #   see `pyportable_installer.compilers.pyportable_encryptor
    #   ._generate_runtime_lib`


def inject(filename, globals_, locals_, ciphertext: bytes):
    _validate_self_package()
    _validate_source_file(filename)
    
    key = __example_keygen()
    #   see `pyportable_installer.compiler.pyportable_encrypt`.
    locals_['__PYMOD_HOOK__'] = {}
    
    def __decrypt_data(data: bytes, key: str) -> str:
        """
        Notes:
            1. Here we copy part of source code from `./decrypt.py`.
               Note that do not import `.decrypt.decrypt_data` into this file,
               because we want to avoid decryption hijecked from outside.
            2. cython cannot handle reassignment (have no idea why this
               happend):
               for example:
                    a = 'some string'
                    
                    # if we reassign a...
                    a = a.encode()
                    # -> pyd runtime error: cannot encode because `a` is bytes
                    
                    # then if we think `a` is bytes but don't know why...
                    a = a.decode()
                    # -> pyd runtime error: cannot decode because `a` is str
                    
               to resolve this weired issue, we should assign to a new variable
               name:
                    a = 'some string'
                    b = a.encode()
                    # it worked.
        """
        
        def _unpad(s: bytes) -> bytes:
            return s[:-ord(s[len(s) - 1:])]
        
        data = b64decode(data)  # type: bytes
        _key = sha256(key.encode('utf-8')).digest()  # type: bytes
        iv = data[:AES.block_size]
        cipher = AES.new(_key, AES.MODE_CBC, iv)
        return _unpad(cipher.decrypt(data[AES.block_size:])).decode('utf-8')
    
    try:
        exec(__decrypt_data(ciphertext, key), globals_, locals_)
    except Exception as e:
        raise Exception(filename, e)
    
    try:
        assert locals_['__PYMOD_HOOK__']
    except AssertionError:
        # it assumes the `plaintext` hadn't contained
        # '__PYMOD_HOOK__.update(globals())' in its end lines.
        raise Exception(filename, 'Invalid script code that has not hooked up '
                                  'or updated `__PYMOD_HOOK__` dict.')
    else:
        return locals_['__PYMOD_HOOK__']
    finally:
        del key, globals_, locals_


def _validate_self_package():
    # TODO: check whether self package (pyportable_crypto) had been
    #   modified or not. (tip: use md5 checksum.)
    pass


def _validate_source_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read().rstrip()
        text = sub(r"b'[^\']+'", "b'...'", text)
        # see template generation at `pyportable_installer.compilers.pyportable
        # _encryptor.PyportableEncryptor.__init__`
        if text != dedent('''\
            from pyportable_runtime import inject
            globals().update(inject(__file__, globals(), locals(), b'...'))
        ''').rstrip():
            raise RuntimeError(filename, 'Decompling stopped because the '
                                         'source code was manipulated!')
