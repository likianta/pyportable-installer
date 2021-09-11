"""
Warnings:
    ~/docs/devnote/currently-known-compilers-issues.md

FIXME:
    This module is not suggest to use, it will be refactored with the guidance
    of `.cython_compiler.CythonCompiler`.
"""
import sys
from os import listdir
from os import mkdir
from os.path import basename
from shutil import copyfile
from shutil import rmtree
from uuid import uuid1

from lk_logger import lk
from lk_utils import find_dirs
from lk_utils import send_cmd
from lk_utils.subproc import run_new_thread

from .base_compiler import BaseCompiler
from ..path_model import prj_model


class NuitkaCompiler(BaseCompiler):
    
    def __init__(self, full_python_interpreter):
        super().__init__(full_python_interpreter)
        self._temp_dir = prj_model.temp
    
    def compile_all(self, pyfiles):
        with lk.counting(len(pyfiles)):
            for i, o in pyfiles:
                o += 'd'  # py -> pyd
                lk.logtx('[D5520]', 'compiling', i, o, h='parent')
                self.compile_one(i, o)
        run_new_thread(self._cleanup)
    
    def compile_one(self, src_file, dst_file):
        """
        Notes:
            Code uses `~/python/scripts/mypyc` source code for reference.
        """
        # assert nuitka package installed
        try:
            # noinspection PyPackageRequirements
            import nuitka
        except ImportError as e:
            raise e
        
        # copy source file from src_dir to tmp_dir
        tmp_dir = f'{self._temp_dir}/{uuid1()}'
        lk.logt('[D1402]', tmp_dir)
        mkdir(tmp_dir)
        tmp_file = f'{tmp_dir}/{basename(src_file)}'
        copyfile(src_file, tmp_file)
        
        # compiling
        send_cmd('{} -m nuitka --module --nofollow-imports --output-dir="{}" '
                 '--no-pyi-file {}'.format(sys.executable, tmp_dir, tmp_file))
        # cmd = subprocess.run([
        #     sys.executable, 'nuitka', '--module', '--nofollow-imports',
        #     '--output-dir="{}"'.format(tmp_dir), '--no-pyi-file', tmp_file
        # ])
        # if cmd.returncode != 0:
        #     lk.logp(tmp_file, cmd, cmd.returncode,
        #             (cmd.stderr or b'').decode(), (cmd.stdout or b'').decode())
        #     raise RuntimeError(tmp_file, cmd)
        
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
            lk.logt('[D5334]', 'delete dir', d)
            rmtree(d)
