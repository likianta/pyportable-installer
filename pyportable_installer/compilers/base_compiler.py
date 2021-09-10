from ..typehint import *


class BaseCompiler:
    
    def __init__(self, python_interpreter):
        """
        Args:
            python_interpreter: str. the path to system installed python dir or
                an embedded python dir. for example 'c:/program files/python39'.
                by default the embed python is suggested to pass in, which  you
                can use is `pyportable_installer.global_conf.gconf.embed_python`.
                (note that `~.gconf.embed_python` is instantiated after
                `pyportable_installer.main_flow.step1.init_key_params.init_key
                _params`.)
        """
        self._interpreter = python_interpreter
    
    def compile_all(self, pyfiles: TPyFilesToCompile):
        raise NotImplementedError
    
    def compile_one(self, src_file: TPath, dst_file: TPath):
        raise NotImplementedError


class BaseRuntimeLoader:
    pass
