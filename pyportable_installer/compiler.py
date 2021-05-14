import shutil
from os import mkdir, popen
from os.path import dirname

from lk_logger import lk
from lk_utils import filesniff
from lk_utils.read_and_write import dumps, loads

from .global_dirs import global_dirs


def pyarmor_compile(pyfiles: list[str], lib_dir: str):
    """
    
    References:
        docs/devnote/how-does-pytransform-work.md
    """
    # create bootstrap files
    create_bootstrap_files(
        set(map(dirname, pyfiles)), lib_dir
    )
    
    for src_file in pyfiles:
        dst_file = global_dirs.to_dist(src_file)
        _compile_one(src_file, dst_file)


def create_bootstrap_files(src_dirs, lib_dir: str):
    dst_dirs = map(global_dirs.to_dist, src_dirs)
    
    template = loads(global_dirs.template('pytransform.txt'))
    
    for d in dst_dirs:
        dumps(template.format(
            # this must be relative path
            # e.g. '../..' (equals to '../../')
            LIB_PARENT_RELDIR=global_dirs.relpath(dirname(lib_dir), d)
        ), f'{d}/pytransform.py')


def _compile_one(src_file, dst_file):
    """
    Compile `src_file` and generate `dst_file`.
    
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
        |  --bootstrap 4`    |                                                 |
    """
    popen(
        f'pyarmor obfuscate '
        f'--output "{dirname(dst_file)}" '
        f'--bootstrap 2 '
        f'--exact '
        f'--no-runtime '
        f'--silent '
        f'"{src_file}"'
    )
    #   arguments:
    #       --output            output path, pass `dst_file`'s dirname, it will
    #                           generate a compiled file under and has the same
    #                           name with `src_file`
    #       --bootstrap 2       see `docstring:notes:table`
    #       --exact             only obfuscate the listed script(s) (here we
    #                           only obfuscate `src_file`)
    #       --no-runtime        do not generate runtime files (cause we have
    #                           generated runtime files in `{dst}/lib`)
    #       --silent            do not print normal info

# ------------------------------------------------------------------------------
# DELETE


def _move_src_files_to_cache_dir(single_src_dir: str, cache_dir: str):
    src_files_i = filesniff.find_files(single_src_dir, '.py')
    if not src_files_i:
        yield []
    else:
        mkdir(cache_dir)
        src_files_o = [f'{cache_dir}/{n}'
                       for n in map(filesniff.get_filename, src_files_i)]
        [shutil.move(i, o) for i, o in zip(src_files_i, src_files_o)]
        yield src_files_o


def _compile_all(files_i, dir_o):
    files_i = ' '.join([f'"{f}"' for f in files_i])
    r = popen(
        f'pyarmor obfuscate '
        f'-O "{dir_o}" --bootstrap 2 --exact -n '
        f'{files_i}'
    )
    lk.loga(r.read())
