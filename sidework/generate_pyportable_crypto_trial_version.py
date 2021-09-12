import os
import shutil
from os.path import basename
from secrets import token_hex  # secrets is introduced since Python 3.6
from uuid import uuid1

import pyportable_crypto
from lk_logger import lk
from lk_utils import dumps
from lk_utils.filesniff import get_dirname
from lk_utils.read_and_write import ropen

from pyportable_installer.compilers import CythonCompiler
from pyportable_installer.path_model import prj_model


def _check_version(version):
    """
    Requirement: pyportable-crypto version must be >= v0.1.2.
    
    Since v0.1.2 (released at 2021-09-12), pyportable-crypto changes all its
    reassigning statements.
    From something like this:
        a = 'a string blabla...'  # type: str
        a = a.encode()  # type: bytes
    To:
        a = 'a string blabla...' # type: str
        b = a.encode()  # type: bytes
    The reason is when we use cythonize to compile pyportable-crypto to pyd
    files, if a variable (e.g. `a`) is reassigned with type changed, it will
    crash encrypt/decrypt processments.
    """
    if version not in (req := ('0.1.2',)):
        raise Exception(f'current pyportable-crypto version ({version}) is not '
                        f'matched with our requirement ({req}).')


def main():
    try:
        pyportable_crypto_version = pyportable_crypto.__version__
    except:  # note: pyportable_crypto v0.1.0 didn't have __version__ info.
        raise Exception('pyportable-crypto version is too low! please install '
                        'a newer version (pip install pyportable-crypto)')
    _check_version(pyportable_crypto_version)
    
    python = input('System Python dir: ') + '\\python.exe'
    assert os.path.exists(python)
    pyversion = get_dirname(python.replace('\\', '/')).lower()
    
    crypto_src_dir = os.path.dirname(pyportable_crypto.__file__)
    temp_dir = f'{prj_model.temp}/{uuid1()}'
    crypto_dst_parent_dir = f'{temp_dir}/pyportable_crypto_trial_{pyversion}'
    #   make sure the dirname is same with `prj_model._pyportable_crypto_trial`
    crypto_dst_dir = f'{crypto_dst_parent_dir}/pyportable_crypto'
    #   the dirname must be the same packge name with `pyportable_crypto`.
    os.mkdir(temp_dir)
    os.mkdir(crypto_dst_parent_dir)
    os.mkdir(crypto_dst_dir)
    
    file_a1 = f'{crypto_src_dir}/inject.py'
    file_a2 = f'{temp_dir}/inject.py'
    file_a3 = f'{crypto_dst_dir}/inject.pyd'
    
    file_b1 = f'{crypto_src_dir}/encrypt.py'
    file_b2 = f'{temp_dir}/encrypt.py'
    file_b3 = f'{crypto_dst_dir}/encrypt.pyd'
    
    # https://blog.csdn.net/weixin_35667833/article/details/113979070
    key = token_hex(16)
    lk.loga(key)
    assert (_len := len(key.encode('utf-8'))) == 32, _len
    
    with ropen(file_a1) as f:
        lines = f.readlines()
        # just simply modify the 65th line
        lines[64] = '{}_key = "{}".encode("utf-8")\n'.format(' ' * 8, key)
        dumps(''.join(lines), file_a2)
    
    with ropen(file_b1) as f:
        lines = f.readlines()
        # just simply modify the 18th line
        lines[17] = '{}_key = "{}".encode("utf-8")\n'.format(' ' * 4, key)
        dumps(''.join(lines), file_b2)
    
    compiler = CythonCompiler(python)
    compiler.compile_one(file_a2, file_a3)
    compiler.compile_one(file_b2, file_b3)
    # dumps(pyversion, f'{crypto_dst_dir}/__pyversion__.txt')
    
    # generate __init__.py
    dumps(
        'from .encrypt import encrypt_data, encrypt_file\n'
        'from .inject import inject\n\n'
        '__version__ = "{}-trial"'.format(pyportable_crypto_version),
        f'{crypto_dst_dir}/__init__.py'
    )
    
    ''' Note: Do Non Use `sys.path.append(xxx.zip)`
    
    Do not generate zip file, and do not import from a zip file, because python
    zipimport doesn't work if we add it to `sys.path`.
    
    For example:
        import sys
        zip_file = 'xxx.zip'
        #   xxx.zip
        #   |= package_x
        #       |- __init__.py  # ::
        #       |       from . import abc
        #       |- abc.pyd      # note that this is a pyd file.
        
        # Add zip file to `sys.path`
        sys.path.insert(0, zip_file)
        # The zipimport can introduce `package_x.__init__`, but cannot
        # recognize `abc` module (ImportError).
        
        import package_x
        print(package_x.__file__)
        # -> '~/xxx.zip/package_x/__init__.py'
        
        from package_x import abc
        # -> ImportError: cannot import name 'abc' from 'package_x'!
        
        # If we don't import zip file, i.e. assumed "xxx" is a folder path, it
        # works well then.
    '''
    
    lk.loga('''
        see result at:
            parent dir: {}
            target dir: {}
        you can copy parent dir and put it under:
            accessory dir: {}
    '''.format(crypto_dst_parent_dir, crypto_dst_dir, prj_model.accessory))
    
    if input('move it now? (y/n): ') == 'y':
        dir_i = crypto_dst_parent_dir
        dir_o = prj_model.accessory + '/' + basename(crypto_dst_parent_dir)
        if os.path.exists(dir_o):
            shutil.rmtree(dir_o)
        shutil.move(dir_i, dir_o)
        lk.loga('see result: ' + dir_o)


if __name__ == '__main__':
    main()
