"""
Notes:
    If new version of pyportable-crypto installed, remember to delete
    "~/lib/pyportable_crypto" to make sure `pyportable_installer.path_model
    .PyPortablePathModel.build_dirs` generate new one.
"""
import os

import pyportable_crypto
from lk_logger import lk
from lk_utils import run_cmd_args


def _check_crypto_version():
    """ require pyportable_crypto version >= 1.0 """
    ver_segs = pyportable_crypto.__version__.split('.')
    assert float('.'.join(ver_segs[:2])) >= 1.0
    del ver_segs
    return True


def _get_pyversion(python_path) -> str:
    pyversion = run_cmd_args(python_path, '--version')
    # -> e.g. 'Python 3.8.0'
    pyversion = tuple(map(int, pyversion.split(' ')[1].split('.')[:2]))
    # -> e.g. (3, 8)
    pyversion = 'py{}{}'.format(*pyversion)
    # -> e.g. 'py38'
    return pyversion


def mainloop(key, root_dir='../pyportable_installer/compilers/lib'):
    _check_crypto_version()
    
    while python_dir := input('system python dir (empty to escape loop): '):
        python_exe = f'{python_dir}\\python.exe'
        pyversion = _get_pyversion(python_exe)
        assert os.path.exists(python_exe)
        
        lk.logdx(pyversion)
        dir_o = root_dir + '/pyportable_runtime_' + pyversion
        pyportable_crypto.cipher_gen.generate_custom_cipher_package(
            key, dir_o, python_exe
        )


if __name__ == '__main__':
    from secrets import token_urlsafe
    
    mainloop(key=token_urlsafe())
    # mainloop(key_='we1c0me_to_depsland', auto_move_to_accessory=False)
