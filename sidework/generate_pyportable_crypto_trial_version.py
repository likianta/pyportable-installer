"""
Notes:
    If new version of pyportable-crypto installed, remember to delete
    "~/lib/pyportable_crypto" to make sure `pyportable_installer.path_model
    .PyPortablePathModel.build_dirs` generate new one.
"""
import os
import shutil
from os.path import basename
from secrets import token_hex  # secrets is introduced since Python 3.6
from textwrap import dedent
from uuid import uuid1

import pyportable_crypto
from lk_logger import lk
from lk_utils import dumps
from lk_utils import find_dirs
from lk_utils.filesniff import get_dirname
from lk_utils.read_and_write import ropen

from pyportable_installer.compilers import CythonCompiler
from pyportable_installer.path_model import prj_model

cython_compiler = ...  # type: CythonCompiler


def _check_version():
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
    try:
        version = pyportable_crypto.__version__
    except:  # note: pyportable_crypto v0.1.0 didn't have __version__ info.
        raise Exception('pyportable-crypto version is too low! please install '
                        'a newer version (pip install pyportable-crypto)')
    
    authorized_versions = tuple(REGISTERED_HANDLERS.keys())
    if version not in authorized_versions:
        raise Exception(f'current pyportable-crypto version ({version}) is not '
                        f'matched with our requirement ({authorized_versions}).')
    
    return version


def mainloop(key='', auto_move_to_accessory=False):
    crypto_version = _check_version()
    lk.logt('[I1050]', crypto_version)
    # input('press enter to go on: ')
    
    # https://blog.csdn.net/weixin_35667833/article/details/113979070
    if not key: key = token_hex(16)
    lk.loga(key)
    assert (_len := len(key.encode('utf-8'))) == 32, _len
    
    dirs = []
    while python_dir := input('system python dir (empty to escape loop): '):
        python = f'{python_dir}\\python.exe'
        assert os.path.exists(python)
        python_version = get_dirname(python.replace('\\', '/')).lower()
        
        lk.logdx()
        dir_ = _main(key, python, python_version, crypto_version,
                     auto_move_to_accessory)
        dirs.append(dir_)
    
    # cleanup
    for d in find_dirs(prj_model.temp):
        shutil.rmtree(d)
    
    lk.logp(dirs, title='see result dirs')
    return key


def _main(key, python, python_version, crypto_version, auto_move_to_accessory):
    # src_dir: crypto source dir
    # tmp_dir: temporary dir
    # dst_dir: crypto (pyd) destination dir
    src_dir = os.path.dirname(pyportable_crypto.__file__)
    tmp_dir = f'{prj_model.temp}/{uuid1()}'
    dst_dir_parent = f'{tmp_dir}/pyportable_crypto_trial_{python_version}'
    #   make sure the dirname is same with `prj_model._pyportable_crypto_trial`
    dst_dir = f'{dst_dir_parent}/pyportable_crypto'
    #   the dirname must be the same packge name with `pyportable_crypto`.
    
    os.mkdir(tmp_dir)
    os.mkdir(dst_dir_parent)
    os.mkdir(dst_dir)
    
    global cython_compiler
    cython_compiler = CythonCompiler(python)
    
    handle = REGISTERED_HANDLERS[crypto_version]
    handle(src_dir, tmp_dir, dst_dir, key=key,
           python_version=python_version, crypto_version=crypto_version)
    
    lk.loga('''
        see result at:
            parent dir: {}
            target dir: {}
        you can copy parent dir and put it under:
            accessory dir: {}
    '''.format(dst_dir_parent, dst_dir, prj_model.accessory))
    
    if auto_move_to_accessory:
        dir_i = dst_dir_parent
        dir_o = prj_model.accessory + '/' + basename(dst_dir_parent)
        if os.path.exists(dir_o):
            shutil.rmtree(dir_o)
        shutil.move(dir_i, dir_o)
        
        out = dir_o
    else:
        out = dst_dir_parent
    return out


# ------------------------------------------------------------------------------

def _handle_v0_1_2(dir_i, dir_m, dir_o, **kwargs):
    for filename, lineno, indent in (
            ('inject.py', 64, 8),
            ('encrypt.py', 17, 4),
    ):
        file_i = f'{dir_i}/{filename}'
        file_m = f'{dir_m}/{filename}'
        file_o = f'{dir_o}/{filename}'
        
        __modify_specific_source_lines_a(
            file_i, file_m, lineno, ' ' * indent, kwargs['key']
        )
        
        lk.loga(f'compiling "{filename}" '
                f'(this may take several seconds)')
        __cythonize(file_m, file_o)
    
    __generate__init__(
        kwargs['python_version'], kwargs['crypto_version'], dir_o
    )


def _handle_v0_2_0(dir_i, dir_m, dir_o, **kwargs):
    for filename, lineno, indent in (
            ('inject.py', 65, 8),
            ('encrypt.py', 16, 4),
    ):
        file_i = f'{dir_i}/{filename}'
        file_m = f'{dir_m}/{filename}'
        file_o = f'{dir_o}/{filename}'
        
        __modify_specific_source_lines_a(
            file_i, file_m, lineno, ' ' * indent, kwargs['key']
        )
        
        lk.loga(f'compiling "{filename}" '
                f'(this may take several seconds ~ minutes)')
        __cythonize(file_m, file_o)
    
    __generate__init__(
        kwargs['python_version'], kwargs['crypto_version'], dir_o
    )


def _handle_v0_2_1(dir_i, dir_m, dir_o, **kwargs):
    for filename, lineno, indent in (
            ('inject.py', 774, 4),
    ):
        file_i = f'{dir_i}/{filename}'
        file_m = f'{dir_m}/{filename}'
        file_o = f'{dir_o}/{filename}'
        
        __modify_specific_source_lines_b(
            file_i, file_m, lineno, ' ' * indent, kwargs['key']
        )
        
        lk.loga(f'compiling "{filename}" '
                f'(this may take several minutes)')
        __cythonize(file_m, file_o)
    
    __generate__init__(
        kwargs['python_version'], kwargs['crypto_version'],
        dir_o, imports=(
            'from .inject import inject',
            'from .inject import encrypt_data',
        )
    )


REGISTERED_HANDLERS = {
    '0.1.2': _handle_v0_1_2,
    '0.2.0': _handle_v0_2_0,
    '0.2.1': _handle_v0_2_1,
}


# ------------------------------------------------------------------------------

def __modify_specific_source_lines_a(file_i, file_o, lineno, prefix, key):
    with ropen(file_i) as f:
        lines = f.readlines()
        # just simply modify the specific line
        assert lines[lineno].lstrip().startswith('_key = ')
        lines[lineno] = \
            '{}_key = "{}".encode("utf-8")\n'.format(prefix, key)
        dumps(''.join(lines), file_o)
    return file_o


def __modify_specific_source_lines_b(file_i, file_o, lineno, prefix, key):
    with ropen(file_i) as f:
        lines = f.readlines()
        # just simply modify the specific line
        assert lines[lineno].lstrip().startswith('key = ')
        lines[lineno] = \
            '{}key = "{}"\n'.format(prefix, key)
        dumps(''.join(lines), file_o)
    return file_o


def __cythonize(file_i, file_o):
    global cython_compiler
    cython_compiler.compile_one(file_i, file_o)


def __generate__init__(python_version, crypto_version, dst_dir, imports=(
        'from .encrypt import encrypt_data, encrypt_file',
        'from .inject import inject',
)):
    code = dedent('''\
        import sys

        current_pyversion = "python{{}}{{}}".format(
            sys.version_info.major, sys.version_info.minor
        )
        target_pyversion = "{0}"
        if current_pyversion != target_pyversion:
            raise Exception(
                "Python interpreter version doesn't matched!",
                "Required: {{}}, got {{}} ({{}})".format(
                    target_pyversion, current_pyversion, sys.executable
                )
            )

        __version__ = "{1}-trial"

        {2}
    ''').format(python_version, crypto_version, '\n'.join(imports))
    
    dumps(code, f'{dst_dir}/__init__.py')
    dumps(python_version, f'{dst_dir}/__pyversion__.txt')
    
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


if __name__ == '__main__':
    mainloop(auto_move_to_accessory=True)
