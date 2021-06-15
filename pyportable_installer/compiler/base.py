from ..typehint import *


class BaseCompiler:
    
    def __init__(self, python_interpreter: TPath = ''):
        """

        Args:
            python_interpreter: 如果启用了虚拟环境, 则这里传入 `.venv_builder:
                VEnvBuilder:get_embed_python:returns`; 如果没使用虚拟环境, 则留
                空, 它将使用默认 (全局的) python 解释器和 pyarmor. 此时请确保该
                解释器和 pyarmor 都可以在 cmd 中访问 (测试命令: `python
                --version`, `pyarmor --version`).
                参考: https://pyarmor.readthedocs.io/zh/latest/advanced.html
                    子章节: "使用不同版本 Python 加密脚本"
        """
        if python_interpreter:  # FIXME: support only Windows platform.
            self._interpreter = python_interpreter.replace('/', '\\')
        else:
            self._interpreter = 'python'
    
    def compile_all(self, pyfiles: list[TPath]):
        raise NotImplementedError
    
    def compile_one(self, src_file: TPath, dst_file: TPath):
        raise NotImplementedError


class BaseRuntimeLoader:
    pass
