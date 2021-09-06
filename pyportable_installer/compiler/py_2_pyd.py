"""
References:
    https://github.com/TechLearnersInc/cythonizer
    https://www.youtube.com/watch?v=qYgKr_AYNjY

Prerequisites:
    cython package
    windows c compiler (install microsoft visual studio build tools, follow the
        guide of https://www.youtube.com/watch?v=qYgKr_AYNjY)
    how to prepare a 'py_2_pyd.bat' file: TODO
"""
import os
from os.path import dirname

from Cython.Build import cythonize
from lk_utils import find_files
from lk_utils.filesniff import get_filename

from .base_compiler import BaseCompiler
from ..path_model import prj_model


class CythonCompiler(BaseCompiler):
    """
    Tree:
        |= hello_world
            |- hello.py  # 1. provide a source file
        |= temp
            |= intermediate_files
                |- hello.c      # 2. cythonize (py -> c, no side effect)
                |- hello.exp    # 3. c compiler (from <msvcpp>/.../cl.exe,
                |- hello.lib    #    ~/link.exe, etc.)
                |- hello.obj    #
        |= dist
            |= hello_world_0.1.0
                |= src
                    |= hello_world
                        |- hello.pyd  # 4. pyd file (from ~/cl.exe, ~/link.exe,
                        |             #    etc.)
    """
    
    # noinspection PyMissingConstructor
    def __init__(self):
        self._bat_file = prj_model.py_2_pyd
        self._temp_dir = prj_model.temp
    
    def compile_all(self, *pyfiles):
        for i, o in pyfiles:
            o += 'd'  # py -> pyd
            yield from self.compile_one(i, o)
    
    def compile_one(self, src_file, dst_file):
        src_name = get_filename(src_file, suffix=False)
        dst_name = get_filename(dst_file, suffix=False)
        
        # 1. py -> c
        cythonize(src_file, f'{self._temp_dir}/{src_name}.c')
        
        # 2. c -> pyd
        # assertion:
        #   assert self._temp_dir != dirname(src_file) != dirname(dst_file)
        os.system(
            '"{bat_file}" "{src_name}" "{dst_name}" '
            '"{src_dir}" "{tmp_dir}" "{dst_dir}"'.format(
                bat_file=self._bat_file,
                src_name=src_name,
                dst_name=dst_name,
                src_dir=self._temp_dir,  # ~.c file's dir
                tmp_dir=self._temp_dir,  # ~.obj, ~.lib, ~.exp files' dir
                dst_dir=dirname(dst_file),
            )
        )
        yield dst_file
        self._cleanup()
    
    def _cleanup(self):
        for f in find_files(self._temp_dir):
            if f.endswith('/.gitkeep'):
                continue
            os.remove(f)
