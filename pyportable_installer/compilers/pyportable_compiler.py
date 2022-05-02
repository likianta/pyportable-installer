import os
import shutil

from lk_utils import dumps
from lk_utils import loads

from .base_compiler import BaseCompiler
from ..global_conf import gconf
from ..path_model import dst_model
from ..path_model import prj_model
from ..path_model import src_model


class PyportableCompiler(BaseCompiler):
    
    # noinspection PyMissingConstructor
    def __init__(self, salt: str, **_):
        """
        Args:
            salt: str.
                PyPortableCompiler has its own private key, so the param is
                receiving a salt value.
                the private key is hidden in `.lib.*.pyportable_runtime.cipher`,
                which is a '.pyd' or '.so' file. more infomation see `~/sidework
                /generate_pyportable_crypto_trial_version.py`.
            **_:
        """
        print(':v', '[D3100]', salt)
        self.salt = salt
        
        from textwrap import dedent
        self._template = dedent('''
            from pyportable_runtime import decrypt
            globals().update(decrypt({ciphertext}, globals(), locals()))
        ''').strip()
        
        self._generate_runtime_lib()
    
    def _generate_runtime_lib(self):
        import pyportable_runtime  # noqa
        #   this package is from `.lib.*.pyportable_runtime`.
        #   the package path is added since `../main_flow/step1/init_key_params
        #   .py:[func]_init_pyportable_runtime_package`.
        
        if gconf.target_platform == 'windows':
            package_dir = {
                'python38' : prj_model.pyportable_runtime_py38,
                'python39' : prj_model.pyportable_runtime_py39,
                'python310': prj_model.pyportable_runtime_py310,
            }[gconf.target_pyversion]
            #   note this is different from `../main_flow/step1/init_key_params
            #   .py:[func]_init_pyportable_runtime_package`. here we are using
            #   `gconf.target_pyversion`, not `gconf.current_pyversion`.
        else:
            package_dir = prj_model.pyportable_runtime_py38_linux
        
        dir_i = package_dir
        dir_o = dst_model.lib + '/pyportable_runtime'
        
        #: [scheme 1]
        shutil.copytree(dir_i, dir_o)
        
        #: [scheme 2] copy whole dir_i to dir_o, but exclude __pycache__ folder.
        # os.mkdir(dir_o)
        # for name in os.listdir(dir_i):
        #     if name == '__pycache__': continue
        #     shutil.copyfile(f'{dir_i}/{name}', f'{dir_o}/{name}')
        
        # add salt file ('<dir_o>/__salt__')
        dumps(pyportable_runtime.encrypt(self.salt).decode('utf-8'),
              dir_o + '/__salt__')
    
    def compile_all(self, pyfiles):
        print(':i0')
        for i, o in pyfiles:
            print(':is', 'compiling', os.path.relpath(i, src_model.prj_root))
            self.compile_one(i, o)
    
    def compile_one(self, src_file, dst_file):
        if os.path.basename(src_file) == '__init__.py':
            shutil.copyfile(src_file, dst_file)
            return dst_file
        
        data_r = loads(src_file)
        data_w = self._encrypt(data_r)
        dumps(data_w, dst_file)
        
        return dst_file
    
    def _encrypt(self, data: str) -> str:
        from pyportable_runtime import encrypt  # noqa
        data = encrypt(data, add_shell=True, salt=self.salt)  # type: bytes
        return self._template.format(ciphertext=data)
