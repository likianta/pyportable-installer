from os import path as ospath
from os import popen

from .global_dirs import global_dirs


class PyArmorCompiler:
    
    def __init__(self, python_interpreter=''):
        """
        
        Args:
            python_interpreter: 如果启用了虚拟环境, 则这里传入 `.venv_builder:
                VEnvBuilder:get_embed_python:returns`; 如果没使用虚拟环境, 则留
                空, 它将使用默认 (全局的) python 解释器和 pyarmor. 此时请确保该
                解释器和 pyarmor 都可以在 cmd 中访问 (测试命令: `python
                --version`, `pyarmor --version`).
                参考: https://pyarmor.readthedocs.io/zh/latest/advanced.html
                    子章节: "使用不同版本 Python 加密脚本"
        
        Warnings:
            Currently only supports Windows platform.
        """
        if python_interpreter:
            self._interpreter = python_interpreter.replace('/', '\\')
            self._pyarmor = self._locate_pyarmor_script()
            self._head = f'"{self._interpreter}" "{self._pyarmor}"' \
                if self._interpreter else f'"{self._pyarmor}"'
        else:
            self._interpreter = 'python'
            self._pyarmor = 'pyarmor'
            self._head = 'pyarmor'
    
    @staticmethod
    def _locate_pyarmor_script():
        try:
            import pyarmor
        except ImportError as e:
            print('Error: could\'t find pyarmor lib! Please make sure you have '
                  'installed pyarmor (by `pip install pyarmor`).')
            raise e
        file = ospath.abspath(f'{pyarmor.__file__}/../pyarmor.py')
        assert ospath.exists(file)
        return file
    
    def generate_runtime(self, local_dir: str, lib_dir: str):
        from shutil import copytree
        
        dir_i = f'{local_dir}/pytransform'
        dir_o = f'{lib_dir}/pytransform'
        
        if not ospath.exists(dir_i):
            popen(f'{self._head} --silent runtime -O {local_dir}')
            #   note the target dir is `local_dir`, not `dir_i`
            #   see `cmd:pyarmor runtime -h`
        copytree(dir_i, dir_o)
    
    def compile_all(self, pyfiles: list[str]):
        """
        
        References:
            docs/devnote/how-does-pytransform-work.md
        """
        for src_file in pyfiles:
            dst_file = global_dirs.to_dist(src_file)
            self.compile_one(src_file, dst_file)
    
    def compile_one(self, src_file, dst_file):
        """
        Compile `src_file` and generate `dst_file`.

        Args:
            src_file
            dst_file
            
        References:
            `cmd:pyarmor obfuscate -h`
            `pyportable_installer/assets_copy.py:copy_runtime`

        Results:
            the `dst_file` has the same content structure:
                from pytransform import pyarmor_runtime
                pyarmor_runtime()
                __pyarmor__(__name__, __file__, b'\\x50\\x59\\x41...')
            `pytransform` comes from `{dist}/lib`, it will be added to
            `sys.path` in the startup (see `pyportable_installer/template/
            bootloader.txt` and `pyportable_installer/no3_build_pyproject.py::
            func:_create_launcher`).
        
        Notes:
            table of `pyarmor obfuscate --bootstrap {0~4}`

            | command            | result                                      |
            | ================== | =========================================== |
            | `pyarmor obfuscate | each obfuscated file has a header of        |
            |  --bootstrap 0`    | `from .pytransform import pyarmor_runtime`  |
            | ------------------ | ------------------------------------------- |
            | `pyarmor obfuscate | only `__init__.py` has a header of          |
            |  --bootstrap 1`    | `from .pytransform import pyarmor_runtime`  |
            | ------------------ | ------------------------------------------- |
            | `pyarmor obfuscate | each obfuscated file has a header of        |
            |  --bootstrap 2`    | `from pytransform import pyarmor_runtime`   |
            |                    | **this is what we want**                    |
            | ------------------ | ------------------------------------------- |
            | `pyarmor obfuscate | *unknown*                                   |
            |  --bootstrap 3`    |                                             |
            | ------------------ | ------------------------------------------- |
            | `pyarmor obfuscate | *unknown*                                   |
            |  --bootstrap 4`    |                                             |
        """
        popen(
            f'{self._head} --silent obfuscate '
            f'--output "{ospath.dirname(dst_file)}" '
            f'--bootstrap 2 '
            f'--exact '
            f'--no-runtime '
            f'"{src_file}"'
        )
        #   arguments:
        #       --silent        do not print normal info
        #       --output        output path, pass `dst_file`'s dirname, it will
        #                       generate a compiled file under and has the same
        #                       name with `src_file`
        #       --bootstrap 2   see `docstring:notes:table`
        #       --exact         only obfuscate the listed script(s) (here we
        #                       only obfuscate `src_file`)
        #       --no-runtime    do not generate runtime files (cause we have
        #                       generated runtime files in `{dst}/lib`)
