import os
from os.path import basename
from os.path import dirname
from shutil import copyfile
from shutil import copytree
from textwrap import dedent
from typing import Callable

from lk_logger import lk
from lk_utils import dumps
from lk_utils import loads

from .base_compiler import BaseCompiler
from .cython_compiler import CythonCompiler
from ..global_conf import gconf
from ..path_model import dst_model
from ..path_model import prj_model


class PyportableEncryptor(BaseCompiler):
    trial_mode: bool
    # _cython_compiler: CythonCompiler
    _encrypt_data: Callable
    _template: str
    __key: str
    
    # noinspection PyMissingConstructor
    def __init__(self, key: str, trial_mode=False, **_):
        # analyse params
        if key == '_trial':
            trial_mode = True
        elif key in ('', '_random', '{random}', '<random>'):
            #   TODO: we'll support only '_random' in the future.
            from secrets import token_hex
            key = token_hex(32)
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
        self._encrypt_data = self._load_pyportable_crypto(trial_mode)
    
    def _generate_runtime_lib(self, trial_mode: bool):
        # 1.
        src_dir = prj_model.pyportable_crypto
        tmp_dir = prj_model.temp
        dst_dir = dst_model.lib + '/pyportable_runtime'
        
        # 2.
        if trial_mode:
            copytree(prj_model.pyportable_crypto_trial + '/pyportable_crypto',
                     dst_dir)
            #   notice: there's a sole subfolder in `prj_model.pyportable_crypto
            #   _trial`, that's we need to copy, then rename it to
            # 'pyportable_runtime'.
            return
        else:
            os.mkdir(dst_dir)
        
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
        os.remove(tmp_file)
    
    @staticmethod
    def _load_pyportable_crypto(trial_mode: bool):
        if trial_mode:
            import sys
            sys.path.insert(0, prj_model.pyportable_crypto_trial)
        from pyportable_crypto import encrypt
        lk.logt("[D1631]", encrypt.__file__)
        return encrypt.encrypt_data

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
        data = self._encrypt_data(data, self.__key)  # type: bytes
        code = self._template.format(ciphertext=data)  # type: str
        dumps(code, dst_file)
        return dst_file
    
    @property
    def key(self):
        return self.__key
