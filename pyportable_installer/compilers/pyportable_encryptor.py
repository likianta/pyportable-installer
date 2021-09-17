import os
import shutil
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
from ..path_model import src_model


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
            lk.logt('[I3130]', 'note: the PyportableEncryptor is running '
                               'under trial mode, the `key` attribute is '
                               'invalid.')
        
        # assignments
        self.trial_mode = trial_mode
        # self._cython_compiler = CythonCompiler(
        #     gconf.python_interpreter, gconf.python_version
        # )
        self._template = dedent('''
            from pyportable_runtime import inject
            globals().update(inject(globals(), locals(), {ciphertext}))
        ''').strip()  # `pyportable_crypto.inject._validate_source_file`
        self.__key = key
        
        # generate runtime lib
        self._generate_runtime_lib(trial_mode)
        self._encrypt_data = self._load_pyportable_crypto(trial_mode)
    
    def _generate_runtime_lib(self, trial_mode: bool):
        # 1.
        src_dir = prj_model.pyportable_crypto
        tmp_dir = prj_model.temp
        dst_dir = dst_model.lib + '/pyportable_runtime'
        
        # 2. create '__init__.py' for `pyportable_runtime`
        os.mkdir(dst_dir)
        dumps('from .inject import inject', f'{dst_dir}/__init__.py')

        # 3.
        if trial_mode:
            shutil.copyfile(
                prj_model.pyportable_crypto_trial +
                '/pyportable_crypto/inject.pyd',
                f'{dst_dir}/inject.pyd'
            )
            return
        elif self.__key.startswith('path:'):
            #   this is an experimental feature. see source from
            #   `pyportable_installer.main_flow.step1.indexing_paths
            #   .indexing_paths > the end of lines in the function`
            shutil.copytree(self.__key[5:], dst_dir, dirs_exist_ok=True)
            return

        # 4. generate temporary 'inject.py' in tmp_dir
        code = loads(f'{src_dir}/inject.py')
        code = code.replace('{KEY}', self.__key)
        dumps(code, tmp_file := f'{tmp_dir}/inject.py')
        
        # 5. cythonize from tmp_dir/~.py to dst_dir/~.pyd
        compiler = CythonCompiler(gconf.full_python)
        compiler.compile_one(tmp_file, f'{dst_dir}/inject.pyd')
        
        # 6. cleanup tmp_dir
        compiler.cleanup()
        os.remove(tmp_file)
    
    def _load_pyportable_crypto(self, trial_mode: bool):
        if trial_mode:
            import sys
            # TODO: to be explained
            if self.__key.startswith('path:'):
                # FIXME
                sys.path.insert(0, os.path.dirname(self.__key[5:]))
            else:
                sys.path.insert(0, prj_model.accessory +
                                '/pyportable_crypto_trial_python39')
            # # sys.path.insert(0, prj_model.pyportable_crypto_trial)
        import pyportable_crypto
        lk.logt('[D3149]',
                pyportable_crypto.__version__,
                pyportable_crypto.__file__)
        from pyportable_crypto import encrypt_data
        return encrypt_data
    
    def compile_all(self, pyfiles):
        with lk.counting(len(pyfiles)):
            for i, o in pyfiles:
                lk.logx('compiling', os.path.relpath(i, src_model.prj_root))
                self.compile_one(i, o)
    
    def compile_one(self, src_file, dst_file):
        if os.path.basename(src_file) == '__init__.py':
            # lk.logt('[D0359]', 'PyportableEncryptor doesn\'t compile '
            #                    '\'__init__.py\' (leave it uncompiled, just '
            #                    'copy to the dist)', src_file)
            shutil.copyfile(src_file, dst_file)
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
