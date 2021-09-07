from inspect import currentframe
from re import sub
from textwrap import dedent

from .decrypt import decrypt


_self_check = None


def inject(filename, ciphertext: bytes):
    _validate_self_package()
    _validate_source_file(filename)
    
    key = '{KEY}'
    #   you can replace this value with your own secret key, then compile this
    #   module to '.pyd' format to protect it from reverse engineer.
    #   see `pyportable_installer.compiler.pyportable_encrypt`.
    pymod_hook = {'__PYMOD_HOOK__': {}}
    
    try:
        plaintext = decrypt(ciphertext, key)
        exec(plaintext, pymod_hook)
    except Exception as e:
        raise Exception(filename, e)
    
    try:
        assert pymod_hook['__PYMOD_HOOK__']
    except AssertionError:
        # it assumes the `plaintext` hadn't contained
        # '__PYMOD_HOOK__.update(globals())' in its end lines.
        raise Exception(filename, 'Invalid script code that has not hooked up '
                                  'or updated `__PYMOD_HOOK__` dict.')
    else:
        return pymod_hook['__PYMOD_HOOK__']


def _validate_self_package():
    global _self_check
    if _self_check is None:
        # TODO: check whether self package (pyportable_crypto) had been modified or
        #   not. (tip: use md5 checksum.)
        pass
        # _self_check = True
        
    if _self_check is True:
        return
    else:
        raise RuntimeError('Decompling stopped because the source code '
                           'was manipulated!')


def _validate_source_file(filename):
    if currentframe().f_back.f_back.f_code.co_filename == filename:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
            text = sub(r"b'.+'", "b'...'", text)
            if text == dedent('''\
                from pyportable_crypto import inject
                globals().update(inject(__file__, b'...'))
            '''):
                return
    raise RuntimeError(filename, 'Decompling stopped because the source code '
                                 'was manipulated!')
