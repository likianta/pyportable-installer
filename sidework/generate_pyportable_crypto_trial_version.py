import os
import shutil
import zipfile
from os.path import basename
from secrets import token_hex  # secrets is introduced since Python 3.6
from uuid import uuid1

from lk_logger import lk
from lk_utils import dumps
from lk_utils.filesniff import get_dirname
from lk_utils.read_and_write import ropen

import pyportable_crypto
from pyportable_installer.compilers import CythonCompiler
from pyportable_installer.path_model import prj_model


def _check_version(version, target_version_range=('0.1.0', '0.1.1')):
    if version not in target_version_range:
        raise Exception


def main():
    pyportable_crypto_version = getattr(
        pyportable_crypto, '__version__', '0.1.0')
    _check_version(pyportable_crypto_version)
    
    python = input('System Python dir: ') + '\\python.exe'
    assert os.path.exists(python)
    pyversion = get_dirname(python.replace('\\', '/')).lower()
    
    crypto_dir = os.path.dirname(pyportable_crypto.__file__)
    temp_dir = f'{prj_model.temp}/{uuid1()}'
    trial_dir = f'{temp_dir}/pyportable_crypto'
    #   the dirname must be 'pyportable_crypto'
    trial_file = f'{temp_dir}/pyportable_crypto_trial_{pyversion}.zip'
    #   make sure the filename is same with `prj_model._pyportable_crypto_trial`
    os.mkdir(temp_dir)
    os.mkdir(trial_dir)
    
    file_a1 = f'{crypto_dir}/inject.py'
    file_a2 = f'{temp_dir}/inject.py'
    file_a3 = f'{trial_dir}/inject.pyd'
    
    file_b1 = f'{crypto_dir}/encrypt.py'
    file_b2 = f'{temp_dir}/encrypt.py'
    file_b3 = f'{trial_dir}/encrypt.pyd'
    
    # https://blog.csdn.net/weixin_35667833/article/details/113979070
    key = token_hex(16)
    lk.loga(key)
    assert len(key.encode('utf-8')) == 32, len(key.encode('utf-8'))
    
    with ropen(file_a1) as f:
        lines = f.readlines()
        # just simply modify the 65th line
        lines[64] = '{}_key = "{}".encode("utf-8")\n'.format(' ' * 8, key)
        # lines[64] = lines[64].replace('key', f'"{key}"')
        dumps(''.join(lines), file_a2)
    
    with ropen(file_b1) as f:
        lines = f.readlines()
        lines[17] = '{}key = "{}".encode("utf-8")\n'.format(' ' * 4, key)
        # lines[17] = lines[17].replace('key.', f'"{key}".')
        dumps(''.join(lines), file_b2)
    
    compiler = CythonCompiler(python)
    compiler.compile_one(file_a2, file_a3)
    compiler.compile_one(file_b2, file_b3)
    # dumps(pyversion, f'{temp_dir}/__pyversion__.txt')

    # generate __init__.py
    dumps(
        'from .encrypt import encrypt_data, encrypt_file\n'
        'from .inject import inject\n\n'
        '__version__ = "{}-trial"'.format(pyportable_crypto_version),
        f'{trial_dir}/__init__.py'
    )

    # genearte zip file
    # https://www.cnblogs.com/sea-stream/p/10008029.html
    os.chdir(temp_dir)
    with zipfile.ZipFile(trial_file, 'w') as handle:
        handle.write('pyportable_crypto/__init__.py')
        handle.write('pyportable_crypto/encrypt.pyd')
        handle.write('pyportable_crypto/inject.pyd')

    lk.loga('''
        see result at:
            folder: {}
            file: {}
        you can copy zip file and put it to:
            accessory dir: {}
    '''.format(temp_dir, trial_file, prj_model.accessory))
    
    if input('move it now? (y/n): ') == 'y':
        file_i = trial_file
        file_o = prj_model.accessory + '/' + basename(trial_file)
        if os.path.exists(file_o):
            os.remove(file_o)
        shutil.move(file_i, file_o)
        lk.loga('see result: ' + file_o)


if __name__ == '__main__':
    main()
