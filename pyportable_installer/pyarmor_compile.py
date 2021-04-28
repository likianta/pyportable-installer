import os
import shutil

from lk_logger import lk
from lk_utils import filesniff

from .assets_copy import CURR_DIR, copy_runtime


def main(dirs_to_compile: list[str], src_dir: str, cache_dir: str):
    """
    
    Args:
        dirs_to_compile: see `main.py > build_pyproject > vars:dirs_to_compile`
        src_dir: 'source code directory'. see `main.py > build_pyproject >
            vars:src_dir`
        cache_dir: 'cache directory'. see `main.py > build_pyproject >
            vars:cache_dir`
            
    References:
        docs/devnote/how-does-pytransform-work.md
    """
    for i, d in enumerate(dirs_to_compile):
        for src_files in _move_src_files_to_cache_dir(d, f'{cache_dir}/{i}'):
            if not src_files:
                continue
            else:
                _compile_all(src_files, d)
    
    copy_runtime(f'{CURR_DIR}/template', src_dir, dirs_to_compile)


def _move_src_files_to_cache_dir(single_src_dir: str, cache_dir: str):
    src_files_i = filesniff.find_files(single_src_dir, '.py')
    if not src_files_i:
        yield []
    else:
        os.mkdir(cache_dir)
        src_files_o = [f'{cache_dir}/{n}'
                       for n in map(filesniff.get_filename, src_files_i)]
        [shutil.move(i, o) for i, o in zip(src_files_i, src_files_o)]
        yield src_files_o


def _compile_all(files_i, dir_o):
    """
    References:
        `cmd:pyarmor obfuscate -h`
        `pyportable_installer/assets_copy.py:copy_runtime`

    Notes:
        table of `pyarmor obfuscate --bootstrap {0~4}`
        
        | command            | result                                          |
        | ================== | =============================================== |
        | `pyarmor obfuscate | each obfuscated file has a header of            |
        |  --bootstrap 0`    | `from .pytransform import pyarmor_runtime`      |
        | ------------------ | ----------------------------------------------- |
        | `pyarmor obfuscate | only `__init__.py` has a header of              |
        |  --bootstrap 1`    | `from .pytransform import pyarmor_runtime`      |
        | ------------------ | ----------------------------------------------- |
        | `pyarmor obfuscate | each obfuscated file has a header of            |
        |  --bootstrap 2`    | `from pytransform import pyarmor_runtime`       |
        |                    | **this is what we want**                        |
        | ------------------ | ----------------------------------------------- |
        | `pyarmor obfuscate | *unknown*                                       |
        |  --bootstrap 3`    |                                                 |
        | ------------------ | ----------------------------------------------- |
        | `pyarmor obfuscate | *unknown*                                       |
        |  --bootstrap 4`    |
    """
    files_i = ' '.join([f'"{f}"' for f in files_i])
    r = os.popen(
        f'pyarmor obfuscate '
        f'-O "{dir_o}" --bootstrap 2 --exact -n '
        f'{files_i}'
    )
    lk.loga(r.read())
