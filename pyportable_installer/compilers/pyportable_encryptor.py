import os
import shutil
import sys
from textwrap import dedent
from typing import Callable

from lk_logger import lk
from lk_utils import dumps
from lk_utils import loads
from lk_utils import run_cmd_args

from .base_compiler import BaseCompiler
from .cython_compiler import CythonCompiler
from ..global_conf import gconf
from ..path_model import dst_model
from ..path_model import prj_model
from ..path_model import src_model


class PyportableEncryptor(BaseCompiler):
    mode: str  # str['regular', 'random', 'trial', 'delegation']
    _encrypt_data: Callable
    _template: str
    __key: str
    __runtime_dir: str
    
    # noinspection PyMissingConstructor
    def __init__(self, key: str, **_):
        # analyse params
        if key == '_trial':
            mode = 'trial'
        elif key.startswith('path:'):
            mode = 'delegation'
        elif key in ('', '_random'):
            mode = 'random'
        else:
            mode = 'regular'
        
        if mode == 'random':
            from secrets import token_hex
            key = token_hex(32)
        lk.logt('[D2858]', key)
        
        if mode == 'trial':
            lk.logt(
                '[I3130]', 'note: the PyportableEncryptor is running under '
                           'trial mode, the `key` attribute is invalid.'
            )
        elif mode == 'delegation':
            lk.logt(
                '[I3131]', 'note: the PyportableEncryptor is running under '
                           'delegation mode, the `key` attribute is invalid.'
            )
        
        # assignments
        self.mode = mode
        self._template = dedent('''
            from pyportable_runtime import inject
            globals().update(inject(globals(), locals(), {ciphertext}))
        ''').strip()  # `pyportable_crypto.inject._validate_source_file`
        self.__key = key
        self.__runtime_dir = key[5:] if mode == 'delegation' else ''
        
        # generate runtime lib
        self._generate_runtime_lib()
        self._encrypt_data = self._load_encryption_func()
    
    def _generate_runtime_lib(self):
        # 1.
        src_dir = prj_model.pyportable_crypto
        tmp_dir = prj_model.temp
        dst_dir = dst_model.lib + '/pyportable_runtime'
        
        # 2. create '__init__.py' for `pyportable_runtime`
        os.mkdir(dst_dir)
        # # code = 'from .inject import inject'
        code = dedent('''
            import sys
            
            current_pyversion = "python{{}}{{}}".format(
                sys.version_info.major, sys.version_info.minor
            )
            target_pyversion = "{0}"
            if current_pyversion != target_pyversion:
                raise Exception(
                    "Python interpreter version doesn't matched!",
                    "Required: {{}}, got {{}} ({{}})".format(
                        target_pyversion, current_pyversion, sys.executable
                    )
                )
            
            from .inject import inject
        ''').format(gconf.target_pyversion).strip()
        #   note: the pyversion check is copied from `sidework.generate
        #   _pyportable_crypto_trial_version.__generate__init__.<vars:code>`
        dumps(code, f'{dst_dir}/__init__.py')
        
        # 3.
        if self.mode == 'trial':
            shutil.copyfile(
                prj_model.pyportable_crypto_trial + '/inject.pyd',
                f'{dst_dir}/inject.pyd'
            )
            return
        elif self.mode == 'delegation':
            #   this is an experimental feature. see source from
            #   `pyportable_installer.main_flow.step1.indexing_paths
            #   .indexing_paths > the end of lines in the function`
            shutil.copytree(self.__runtime_dir, dst_dir, dirs_exist_ok=True)
            return
        
        # 4. generate temporary 'inject.py' in tmp_dir
        code = loads(f'{src_dir}/inject.py')
        code = code.replace('{KEY}', self.__key)  # FIXME
        #   tested on pyportable-crypto v0.1.0, 0.1.1, 0.2.0, 0.2.1
        dumps(code, tmp_file := f'{tmp_dir}/inject.py')
        
        # 5. cythonize from tmp_dir/~.py to dst_dir/~.pyd
        compiler = CythonCompiler(gconf.full_python)
        compiler.compile_one(tmp_file, f'{dst_dir}/inject.pyd')
        
        # 6. cleanup tmp_dir
        compiler.cleanup()
        os.remove(tmp_file)
    
    def _load_encryption_func(self):
        def _load_regular_encryption():
            import pyportable_crypto
            lk.logt('[D4703]',
                    pyportable_crypto.__version__,
                    pyportable_crypto.__file__)
            from pyportable_crypto import encrypt_data
            return encrypt_data
        
        # noinspection PyUnresolvedReferences
        def _load_prepared_encryption(dir_i):
            """ Load a prepared encryption module from `dir_i`. """
            from secrets import token_hex
            token = 'x' + token_hex(15)
            
            dir_x = f'{prj_model.temp_lib}/{token}'
            dir_o = f'{dir_x}/pyportable_crypto'
            #   notice: `dir_x` cannot be deleted by `pyportable_installer.main
            #   _flow.step4.cleanup._cleanup_intermediate_files`, it will raise
            #   a PermissionError ("Access is denied on '~/temp_lib/~/inject
            #   .pyd' ..."). so we postpone deletion to the next time startup,
            #   let `pyportable_installer.path_model.PyPortablePathModel.build
            #   _dirs` handle it.
            
            os.mkdir(dir_x)
            shutil.copytree(dir_i, dir_o)
            
            # inspired by `lk-lambdex` project
            __PYHOOK__ = {}
            exec(
                dedent('''
                    from sys import path
                    path.append(r'{lib_dir}')
                    from {token} import pyportable_crypto
                    __PYHOOK__['mod'] = pyportable_crypto
                ''').format(
                    lib_dir=prj_model.temp_lib,
                    token=token,
                ),
                {'__PYHOOK__': __PYHOOK__}
            )
            pyportable_crypto = __PYHOOK__['mod']
            # del __PYHOOK__

            # lk.logt('[D2009]', dir_i)
            lk.logt('[D4704]',
                    pyportable_crypto.__version__,
                    pyportable_crypto.__file__)
            return pyportable_crypto.encrypt_data
        
        def _load_precompiled_encryption():
            lk.logt('[W2908]', '(experimental feature)',
                    'using PyportableRuntimeDelegator to process external '
                    'precompiled pyportable_runtime')
            delegator = PyportableRuntimeDelegator(
                gconf.embed_python, self.__runtime_dir
            )
            setattr(
                self, 'compile_all',
                lambda *args, **kwargs: delegator.compile_all(*args, **kwargs)
            )
            setattr(
                self, 'compile_one',
                lambda *args, **kwargs: delegator.compile_one(*args, **kwargs)
            )
            return None
        
        # ----------------------------------------------------------------------
        
        if self.mode == 'regular':
            return _load_regular_encryption()
        
        elif self.mode == 'trial':
            assert os.path.exists(prj_model.pyportable_crypto_trial), '''
                Currently your requested [python_version][1] is not on the
                [supported trial-list][2].
                Please try the following options to resolve your problem:
                    a) Prompt your requested python_version to "3.8" or "3.9";
                    b) Use a custom pyportable_crypto key instead of trial key;
                       Note: you need to install Microsoft Visual Studio C++
                             Build Tools (2019) on your system.
                    c) Contact pyportable_installer project owner to extend
                       trial keys for requested [python_version][1].
                
                [1]: {0}
                [2]: {1}
            '''.format(
                gconf.current_pyversion,
                f'{prj_model.accessory}/pyportable_crypto_trial_*'
            )
            return _load_prepared_encryption(
                dir_i=prj_model.pyportable_crypto_trial
            )
        
        else:  # self.mode == 'delegation'
            pyversion = loads(f'{self.__runtime_dir}/__pyversion__.txt').strip()
            if pyversion == gconf.current_pyversion:
                return _load_prepared_encryption(dir_i=self.__runtime_dir)
            else:
                return _load_precompiled_encryption()
    
    def compile_all(self, pyfiles):
        with lk.counting(len(pyfiles)):
            for i, o in pyfiles:
                lk.logx('compiling', os.path.relpath(i, src_model.prj_root))
                self.compile_one(i, o)
    
    def compile_one(self, src_file, dst_file):
        if os.path.basename(src_file) == '__init__.py':
            shutil.copyfile(src_file, dst_file)
            return dst_file
        
        data = loads(src_file)  # type: str
        data += '\n' + '__PYMOD_HOOK__.update(globals())'
        data = self._encrypt_data(data, self.__key)  # type: bytes
        code = self._template.format(ciphertext=data)  # type: str
        dumps(code, dst_file)
        return dst_file
    
    # @property
    # def key(self):
    #     return self.__key


class PyportableRuntimeDelegator:
    
    def __init__(self, embed_python_exe, pyportable_runtime_dir):
        self._python_exe = embed_python_exe
        self._pyportable_runtime_dir = pyportable_runtime_dir
        self._template = dedent("""
            import sys
            sys.path.insert(0, '{pyportable_runtime_parent_dir}')
            sys.path.append('{lk_utils_dir}')
            
            import os
            import shutil
            from textwrap import dedent
            
            from lk_utils import dumps
            from lk_utils import loads
            from pyportable_runtime import encrypt_data
            
            
            class PyportableEncryptorMini:
            
                def __init__(self):
                    self._encrypt_data = encrypt_data
                    self._template = dedent('''
                        from pyportable_runtime import inject
                        globals().update(inject(globals(), locals(), {{ciphertext}}))
                    ''').strip()
                    # ^ warning: do not modify the template content (e.g. add
                    #   line breaks, adjust whitespaces, etc.), it will violate
                    #   `pyportable_runtime.inject.inject._validate_source_file`
                    self.__key = 'NO_NEED_TO_PASS_A_REAL_KEY'
                
                def compile_all(self, pyfiles):
                    for i, o in pyfiles:
                        self.compile_one(i, o)
                
                def compile_one(self, src_file, dst_file):
                    if os.path.basename(src_file) == '__init__.py':
                        shutil.copyfile(src_file, dst_file)
                        return dst_file
                    
                    data = loads(src_file)  # type: str
                    data += '\\n' + '__PYMOD_HOOK__.update(globals())'
                    data = self._encrypt_data(data, self.__key)  # type: bytes
                    code = self._template.format(ciphertext=data)  # type: str
                    dumps(code, dst_file)
                    return dst_file
            
            
            encryptor = PyportableEncryptorMini()
            encryptor.compile_all({pyfiles})
        """)
    
    def compile_all(self, pyfiles):
        # TODO: use argparse
        code = self._template.format(
            pyportable_runtime_parent_dir=os.path.dirname(
                self._pyportable_runtime_dir
            ),
            lk_utils_dir=os.path.abspath('{}/../lib/site-packages'.format(
                sys.executable
            )),
            pyfiles=pyfiles
        )
        
        dumps(code, x := prj_model.create_temp_dir() +
                         '/delegated_encryption.py')
        run_cmd_args(self._python_exe, x)
    
    def compile_one(self, src_file, dst_file):
        # the `compile_all` is more efficient.
        lk.logt('[W2201]', 'using `PyportableRuntimeDelegator.compile_all` is '
                           'more efficient than `~.compile_one`', h='parent')
        self.compile_all(((src_file, dst_file),))
