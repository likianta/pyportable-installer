import shutil

from .base_compiler import BaseCompiler
from ..typehint import TPyFilesToCompile


class EffectlessCompiler(BaseCompiler):
    """ No compiling process, just do copy files.
    
    This is made for debug mode. (See `pyportable_installer.main.debug_build`.)
    """
    
    # noinspection PyMissingConstructor
    def __init__(self):
        pass
    
    def compile_all(self, pyfiles: TPyFilesToCompile):
        for i, o in pyfiles:
            shutil.copyfile(i, o)
    
    def compile_one(self, src_file, dst_file):
        shutil.copyfile(src_file, dst_file)
