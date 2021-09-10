"""
Warnings:
    ~/docs/devnote/currently-known-compilers-issues.md

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
from os.path import exists
from shutil import copyfile
from shutil import rmtree
from uuid import uuid1

from lk_logger import lk
from lk_utils import find_dirs
from lk_utils import send_cmd
from lk_utils.subproc import run_new_thread

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
        self._temp_dir = prj_model.temp
    
    def compile_all(self, *pyfiles):
        with lk.counting(len(pyfiles)):
            for i, o in pyfiles:
                o += 'd'  # py -> pyd
                lk.logtx('[D5520]', 'compiling', i, o)
                yield self.compile_one(i, o)
        run_new_thread(self.cleanup)
    
    def compile_one(self, src_file, dst_file):
        if basename(src_file) == '__init__.py':
            # https://stackoverflow.com/questions/58797673/how-to-compile-init
            #   -py-file-using-cython-on-windows
            lk.logt('[D0359]', 'cython doesn\'t compile __init__.py (leave it '
                               'uncompiled, just copy to the dist)', src_file)
            copyfile(src_file, dst_file)
            return dst_file
        
        # copy source file
        tmp_dir = f'{self._temp_dir}/{uuid1()}'
        tmp_file = f'{tmp_dir}/{basename(src_file)}'
        
        if len(tmp_file) > (path_limit := 150):  # TODO: 150 or lower?
            # the file path is too long, it will cause cythonize failed by
            # 'cl.exe > fatal error code C1081' (see more infomation at
            # https://docs.microsoft.com/en-us/cpp/error-messages/compiler
            # -errors-1/fatal-error-c1081).
            # we have to move `tmp_file` to another place.
            lk.logt('[I3926]', f'the tmp_file path is too long '
                               f'({len(tmp_file)} > {path_limit}), we have to '
                               f'create it in your desktop direcotry (it will '
                               f'be auto removed when compilation done)')
            _desktop_mode = True
            
            # ref: https://blog.csdn.net/u013948858/article/details/75072873
            import os.path
            desktop_dir = os.path.join(os.path.expanduser("~"), 'Desktop')
            assert exists(desktop_dir)
            tmp_dir = f'{desktop_dir}/{uuid1()}'
            tmp_file = f'{tmp_dir}/{basename(src_file)}'
            assert len(tmp_file) <= path_limit, (
                'The file name is too long to compile!',
                f'{tmp_file = }', f'{src_file = }'
            )
        else:
            _desktop_mode = False
        
        mkdir(tmp_dir)
        copyfile(src_file, tmp_file)
        
        # FIXME: the cythonize is installed in system python/scripts location.
        send_cmd(f'cythonize -3 -i "{tmp_file}"')
        
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
            lk.logt('[D5334]', 'delete dir', d)
            rmtree(d)
