from os import popen
from os.path import dirname

from lk_utils.read_and_write import dumps, loads

from .global_dirs import global_dirs


# noinspection PyUnusedLocal
def pyarmor_compile(pyfiles: list[str], lib_dir: str):
    """
    
    References:
        docs/devnote/how-does-pytransform-work.md
    """
    # create bootstrap files
    # create_bootstrap_files(
    #     set(map(dirname, pyfiles)), lib_dir
    # )
    
    for src_file in pyfiles:
        dst_file = global_dirs.to_dist(src_file)
        _compile_one(src_file, dst_file)


def create_bootstrap_files(src_dirs, lib_dir: str):  # DELETE
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

    Results:
        the `dst_file` has the same content structure:
            from pytransform import pyarmor_runtime
            pyarmor_runtime()
            __pyarmor__(__name__, __file__, b'\\x50\\x59\\x41...')
        `pytransform` comes from `{dist}/lib`, it will be added to `sys.path` in
        the startup (see `pyportable_installer/template/bootloader.txt` and
        `pyportable_installer/no3_build_pyproject.py > func:_create_launcher`).

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
        f'pyarmor --silent obfuscate '
        f'--output "{dirname(dst_file)}" '
        f'--bootstrap 2 '
        f'--exact '
        f'--no-runtime '
        f'"{src_file}"'
    )
    #   arguments:
    #       --silent            do not print normal info
    #       --output            output path, pass `dst_file`'s dirname, it will
    #                           generate a compiled file under and has the same
    #                           name with `src_file`
    #       --bootstrap 2       see `docstring:notes:table`
    #       --exact             only obfuscate the listed script(s) (here we
    #                           only obfuscate `src_file`)
    #       --no-runtime        do not generate runtime files (cause we have
    #                           generated runtime files in `{dst}/lib`)
