"""
References:
    https://github.com/TechLearnersInc/cythonizer
    https://www.youtube.com/watch?v=qYgKr_AYNjY

Prerequisites:
    cython package
    windows c compiler (install microsoft visual studio build tools, follow the
        guide of https://www.youtube.com/watch?v=qYgKr_AYNjY)
"""
from os import listdir
from os import mkdir
from os.path import basename
from shutil import copyfile
from shutil import rmtree
from uuid import uuid1

from lk_logger import lk
from lk_utils import find_dirs
from lk_utils import run_new_thread
from lk_utils import send_cmd

from .base_compiler import BaseCompiler
from ..path_model import prj_model


class CythonCompiler(BaseCompiler):
    """
    Tree:
        |= hello_world
            |- hello.py  # 1. provide a source file
        |= temp
            |= <uid>
                |- hello.py     # 2. copy of source
                |= tmp0o4yav6k  # 3. auto created temp dir by cythonize
                    |= release
                        |= ...
                            |- hello.cp39-win_amd64.exp
                            |- hello.cp39-win_amd64.lib
                            |- hello.obj
                |- hello.cp39-win_amd64.pyd  # 4. generated pyd file (in the
                |                            #    same dir with copy of source)
    """
    
    # noinspection PyMissingConstructor
    def __init__(self):
        self._bat_file = prj_model.py_2_pyd
        self._temp_dir = prj_model.temp
    
    def compile_all(self, *pyfiles):
        for i, o in pyfiles:
            o += 'd'  # py -> pyd
            yield from self.compile_one(i, o)
        run_new_thread(self._cleanup)
    
    def compile_one(self, src_file, dst_file):
        # copy source file
        tmp_dir = f'{self._temp_dir}/{uuid1()}'
        mkdir(tmp_dir)
        tmp_file = f'{tmp_dir}/{basename(src_file)}'
        copyfile(src_file, tmp_file)
        
        # FIXME: the cythonize is installed in system python/scripts location.
        send_cmd(f'cythonize -3 -i "{tmp_file}"')
        
        pyd_name = [x for x in listdir(tmp_dir) if x.endswith('.pyd')][0]
        pyd_file = f'{tmp_dir}/{pyd_name}'
        
        copyfile(pyd_file, dst_file)
        
        yield dst_file
    
    def _cleanup(self):
        for d in find_dirs(self._temp_dir):
            lk.logt('[D5334]', 'delete dir', d)
            rmtree(d)
        # for f in find_files(self._temp_dir):
        #     if f.endswith('/.gitkeep'):
        #         continue
        #     os.remove(f)
