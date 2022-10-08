"""
Warnings:
    ~/docs/devnote/currently-known-compilers-issues.md

References:
    https://cython.readthedocs.io/en/latest/src/tutorial/cython_tutorial.html
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
from os.path import exists
from shutil import copyfile
from shutil import rmtree
from textwrap import dedent
from uuid import uuid1

from lk_utils import dumps
from lk_utils import find_dirs
from lk_utils.subproc import run_cmd_args
from lk_utils.subproc import run_new_thread

from .base_compiler import BaseCompiler
from ..path_model import prj_model


class CythonCompiler(BaseCompiler):
    
    def __init__(self, full_python_interpreter):
        """
        Args:
            full_python_interpreter: system installed python (path), for
                example 'c:/program files/python39/python.exe'. usually we pass
                in `~.global_conf.gconf.full_python`.
        """
        super().__init__(full_python_interpreter)
        self._temp_dir = prj_model.temp
        self._template = dedent('''
            # placeholders:
            #   cythonize_packages
            #   filename
            
            from os import chdir
            from os.path import dirname
            from sys import path
            
            curr_dir = dirname(__file__)
            chdir(curr_dir)
            path.append(r'{cythonize_packages}')
            
            from setuptools import setup
            from Cython.Build import cythonize
            
            setup(ext_modules=cythonize('{filename}', language_level='3'))
        ''')
        #   TODO: we may turn to use loading './accessory/setup_for_cythonize
        #       .py' instead of defining long string here in the future.
    
    def compile_all(self, pyfiles):
        print(':i0')
        for i, o in pyfiles:
            o += 'd'  # *.py -> *.pyd
            print(':iv1' 'compiling', i, o)
            self.compile_one(i, o)
        run_new_thread(self.cleanup)
    
    def compile_one(self, src_file, dst_file):
        filename = basename(src_file)
        
        if filename == '__init__.py':
            # https://stackoverflow.com/questions/58797673/how-to-compile-init
            #   -py-file-using-cython-on-windows
            print(':v1', 'cython doesn\'t compile __init__.py (leave it '
                         'uncompiled, just copy to the dist)', src_file)
            copyfile(src_file, dst_file)
            return dst_file
        
        # copy source file
        tmp_dir = f'{self._temp_dir}/{uuid1()}'
        tmp_file = f'{tmp_dir}/{filename}'
        
        if len(tmp_file) > (path_limit := 150):  # TODO: 150 or lower?
            # the file path is too long, it will cause cythonize failed by
            # 'cl.exe > fatal error code C1081' (see more infomation at
            # https://docs.microsoft.com/en-us/cpp/error-messages/compiler
            # -errors-1/fatal-error-c1081).
            # we have to move `tmp_file` to another place.
            print(':v2', '[I3926]',
                  f'the tmp_file path is too long ({len(tmp_file)} > '
                  f'{path_limit}), we have to create it in your desktop '
                  f'direcotry (it will be auto removed when compilation done)')
            _desktop_mode = True
            
            # ref: https://blog.csdn.net/u013948858/article/details/75072873
            import os.path
            desktop_dir = os.path.join(os.path.expanduser("~"), 'Desktop')
            assert exists(desktop_dir)
            tmp_dir = f'{desktop_dir}/{uuid1()}'
            tmp_file = f'{tmp_dir}/{filename}'
            assert len(tmp_file) <= path_limit, (
                'The file name is too long to compile!',
                f'{tmp_file = }', f'{src_file = }'
            )
        else:
            _desktop_mode = False
        
        mkdir(tmp_dir)
        copyfile(src_file, tmp_file)
        dumps(self._template.format(
            cythonize_packages=prj_model.cythonize_required_packages_for_python3,
            filename=filename
        ), _setup := f'{tmp_dir}/_setup.py')
        
        from lk_utils.subproc import format_cmd
        print(':v1', '[D5200]', format_cmd(
            self._interpreter, _setup, 'build_ext', '--inplace'))
        
        run_cmd_args(self._interpreter, _setup, 'build_ext', '--inplace')
        
        # get pyd file generated in tmp_dir
        pyd_names = [x for x in listdir(tmp_dir) if x.endswith('.pyd')]
        assert len(pyd_names) == 1
        pyd_name = pyd_names[0]
        pyd_file = f'{tmp_dir}/{pyd_name}'
        
        copyfile(pyd_file, dst_file)
        
        if _desktop_mode:
            rmtree(tmp_dir)
        
        return dst_file
    
    def cleanup(self):
        for d in find_dirs(self._temp_dir):
            print(':v1', '[D5334]', 'delete dir', d.relpath)
            rmtree(d.path)
