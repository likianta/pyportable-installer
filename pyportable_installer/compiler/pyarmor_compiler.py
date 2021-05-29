import asyncio
from os import path as ospath
from os import popen
from shutil import copyfile

from lk_logger import lk

from .base import BaseCompiler
from ..global_dirs import global_dirs
from ..utils import send_cmd


class PyArmorCompiler(BaseCompiler):
    
    # noinspection PyMissingConstructor
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
        self._liscense = 'trial'
        #   TODO: see https://pyarmor.readthedocs.io/zh/latest/license.html
        
        if python_interpreter:
            # warnings: `docs/devnote/warnings-about-embed-python.md`
            self._interpreter = python_interpreter.replace('/', '\\')
            # create pyarmor file copy
            origin_file = self._locate_pyarmor_script()
            backup_file = origin_file.removesuffix('.py') + '_copy.py'
            if not ospath.exists(backup_file):
                from lk_utils.read_and_write import loads, dumps
                content = loads(origin_file)
                dumps('\n'.join([
                    'from os.path import dirname',
                    'from sys import path as syspath',
                    'syspath.append(dirname(__file__))',
                    content
                ]), backup_file)
            self._pyarmor = backup_file
            self._head = f'"{self._interpreter}" "{self._pyarmor}"'
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
            lk.loga(f'{self._head} --silent runtime -O "{local_dir}"')
            popen(f'{self._head} runtime -O "{local_dir}"').read()
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
            asyncio.run(self.compile_one(src_file, dst_file))
    
    async def compile_one(self, src_file, dst_file):
        """
        Compile `src_file` and generate `dst_file`.

        Args:
            src_file
            dst_file
            
        References:
            `cmd:pyarmor obfuscate -h`
        
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
        lk.loga('compiling', ospath.basename(src_file))
        
        if self._liscense == 'trial':
            # The limitation of content size is 32768 bytes (i.e. 32KB) in
            # pyarmor trial version.
            if (size := ospath.getsize(src_file)) > 32768:
                lk.logt(
                    '[W0357]',
                    f'该文件: "{src_file}" 的体积 ({size}) 超出了 pyarmor 试用'
                    f'版的限制, 请购买个人版或商业版许可后重新编译! (本文件谨以'
                    f'源码形式打包)'
                )
                copyfile(src_file, dst_file)
                return
            # 注意: 虽然我们已经事先判断了, 如果文件体积大于试用版 pyarmor 的限
            # 制就不用 pyarmor 编译, 但是事实上仍会发生极少数 py 文件体积未超过
            # 限制却被 pyarmor 报超出限制的错误. 该现象目前在编译虚拟环境下的
            # gb2312.py 文件遇到过一次. 为了处理该报错, 我们需要从 subprocess 中
            # 获取到错误, 并转为拷贝源码的方式. 详见下面的处理.
        
        cmd = (
            f'{self._head} --silent obfuscate'
            f' -O "{ospath.dirname(dst_file)}"'
            f' --bootstrap 2'
            f' --exact'
            f' --no-runtime'
            f' "{src_file}"'
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
        try:
            send_cmd(cmd)
        except Exception as e:
            lk.logt('[E1747]', e)
            from os import remove
            remove(dst_file)
            copyfile(src_file, dst_file)
