"""
Warnings:
    ~/docs/devnote/currently-known-compilers-issues.md
    
FIXME:
    This module is not suggest to use, it will be refactored with the guidance
    of `.cython_compiler.CythonCompiler`.
"""
import os
import subprocess
import sys
from os import listdir
from os import mkdir
from os.path import basename
from os.path import dirname
from shutil import copyfile
from shutil import rmtree
from textwrap import dedent
from uuid import uuid1

from lk_utils import dumps
from lk_utils import find_dirs
from lk_utils.subproc import run_new_thread

from .base_compiler import BaseCompiler
from ..path_model import prj_model


class MypycCompiler(BaseCompiler):
    
    def __init__(self, full_python_interpreter):
        super().__init__(full_python_interpreter)
        self._temp_dir = prj_model.temp
    
    def compile_all(self, pyfiles):
        print(':i0')
        for i, o in pyfiles:
            o += 'd'  # py -> pyd
            print(':iv1', '[D5520]', 'compiling', i, o)
            self.compile_one(i, o)
        run_new_thread(self._cleanup)
    
    def compile_one(self, src_file, dst_file):
        """
        Notes:
            Code uses `~/python/scripts/mypyc` source code for reference.
        """
        # copy source file from src_dir to tmp_dir
        tmp_dir = f'{self._temp_dir}/{uuid1()}'
        print(':v1', '[D1402]', tmp_dir)
        mkdir(tmp_dir)
        tmp_file = f'{tmp_dir}/{basename(src_file)}'
        copyfile(src_file, tmp_file)
        
        # create setup.py
        setup_file = f'{tmp_dir}/setup.py'
        setup_code = dedent('''\
            from os import chdir
            from distutils.core import setup
            from mypyc.build import mypycify
            
            chdir(r'{0}')
            
            setup(name='mypyc_output',
                  ext_modules=mypycify({1}, opt_level="{2}"))
        ''').format(tmp_dir, [tmp_file], 3)
        dumps(setup_code, setup_file)
        
        # run setup
        env = os.environ.copy()
        env['PYTHONPATH'] = dirname(sys.executable)
        cmd = subprocess.run(
            [sys.executable, setup_file, 'build_ext', '--inplace'], env=env
        )
        if cmd.returncode != 0:
            raise RuntimeError(cmd, tmp_file)
        
        # get pyd file generated in tmp_dir
        pyd_names = [x for x in listdir(tmp_dir) if x.endswith('.pyd')]
        assert len(pyd_names) == 1
        pyd_name = pyd_names[0]
        pyd_file = f'{tmp_dir}/{pyd_name}'
        
        # copy pyd file from tmp_dir to dst_dir
        copyfile(pyd_file, dst_file)
        
        return dst_file
    
    def _cleanup(self):
        for d in find_dirs(self._temp_dir):
            print(':v1', '[D5334]', 'delete dir', d)
            rmtree(d)
