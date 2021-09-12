import os
from os import mkdir
from os import remove
from os.path import basename
from os.path import dirname
from shutil import copyfile
from shutil import copytree
from textwrap import dedent

from lk_logger import lk
from lk_utils import dumps
from lk_utils import loads

import pyportable_crypto
# from pyportable_crypto import encrypt_data
# from pyportable_crypto import keygen

from .base_compiler import BaseCompiler
from .cython_compiler import CythonCompiler
from ..global_conf import gconf
from ..path_model import dst_model
from ..path_model import prj_model


class PyportableEncryptor(BaseCompiler):
    trial_mode: bool
    # _cython_compiler: CythonCompiler
    _template: str
    __key: str
    
    # noinspection PyMissingConstructor
    def __init__(self, key: str, trial_mode=False, **_):
        # analyse params
        if key == '_trial':
            trial_mode = True
        elif key in ('', '_random', '{random}', '<random>'):
            #   TODO: we'll support only '_random' in the future.
            key = pyportable_crypto.keygen.generate_random_key()
        lk.logt('[D2858]', key)
        if trial_mode:
            lk.logt("[I3130]", 'the PyportableEncryptor is running under trial '
                               'mode, the `key` attribute is invalid.')

        # assignments
        self.trial_mode = trial_mode
        # self._cython_compiler = CythonCompiler(
        #     gconf.python_interpreter, gconf.python_version
        # )
        self._template = dedent('''\
            from pyportable_runtime import inject
            globals().update(inject(__file__, globals(), locals(), {ciphertext}))
        ''')  # `pyportable_crypto.inject._validate_source_file`
        self.__key = key

        # generate runtime lib
        self._generate_runtime_lib(trial_mode)
        if trial_mode: self._load_pyportable_crypto_trial_version()
    
    def _generate_runtime_lib(self, trial_mode: bool):    
        # 1.
        src_dir = prj_model.pyportable_crypto
        tmp_dir = prj_model.temp
        dst_dir = dst_model.lib + '/pyportable_runtime'
        
        # 2.
        if trial_mode:
            from zipfile import ZipFile
            with ZipFile(prj_model.pyportable_crypto_trial) as handle:
                # notice: the extracted result from `handle` is a sole folder
                # named 'pyportable_crypto'. we need to rename it to
                # 'pyportable_runtime'.
                handle.extractall(x := dirname(dst_dir))
                os.rename(f'{x}/pyportable_crypto', dst_dir)
            return
        else:
            mkdir(dst_dir)

        # 3.
        import Cryptodome
        copytree(dirname(Cryptodome.__file__), f'{dst_model.lib}/Cryptodome')
        
        # 4. create '__init__.py' for `pyportable_runtime`
        dumps('from .inject import inject', f'{dst_dir}/__init__.py')
        
        # 5. generate temporary 'inject.py' in tmp_dir
        code = loads(f'{src_dir}/inject.py')
        code = code.replace('{KEY}', self.__key)
        dumps(code, tmp_file := f'{tmp_dir}/inject.py')
        
        # 6. cythonize from tmp_dir/~.py to dst_dir/~.pyd
        compiler = CythonCompiler(gconf.full_python)
        compiler.compile_one(tmp_file, f'{dst_dir}/inject.pyd')
        
        # 7. cleanup tmp_dir
        compiler.cleanup()
        remove(tmp_file)
    
    @staticmethod
    def _load_pyportable_crypto_trial_version():
        lk.logt("[I3341]", 'replace `pyportable_crypto.encrypt_data` with '
                           '`~.pyportable_crypto_trial_version.encrypt_data`')
        import sys
        from importlib import reload
        sys.path.insert(0, prj_model.pyportable_crypto_trial)
        reload(pyportable_crypto)
        lk.loga(v := pyportable_crypto.__version__)
        assert v.endswith('trial')
    
    def compile_all(self, pyfiles):
        with lk.counting(len(pyfiles)):
            for i, o in pyfiles:
                lk.logx('compiling', i, o)
                self.compile_one(i, o)
    
    def compile_one(self, src_file, dst_file):
        if basename(src_file) == '__init__.py':
            lk.logt('[D0359]', 'PyportableEncryptor doesn\'t compile '
                               '\'__init__.py\' (leave it uncompiled, just '
                               'copy to the dist)', src_file)
            copyfile(src_file, dst_file)
            return dst_file
        
        data = loads(src_file)  # type: str
        data += '\n' + '__PYMOD_HOOK__.update(globals())'
        data = pyportable_crypto.encrypt_data(data, self.__key)  # type: bytes
        code = self._template.format(ciphertext=data)  # type: str
        dumps(code, dst_file)
        return dst_file
    
    @property
    def key(self):
        return self.__key
