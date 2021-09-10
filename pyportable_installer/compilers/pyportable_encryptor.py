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

from pyportable_crypto import encrypt_data
from pyportable_crypto import keygen
from .base_compiler import BaseCompiler
from .cython_compiler import CythonCompiler
from ..global_conf import gconf
from ..path_model import dst_model
from ..path_model import prj_model


class PyportableEncryptor(BaseCompiler):
    __key: str
    _template: str
    
    # noinspection PyMissingConstructor
    def __init__(self, key: str):
        if key == '' or key == '{random}':
            key = keygen.generate_random_key()
        self.__key = key
        lk.logt('[D2858]', key)
        self._generate_runtime_lib()
        
        self._template = dedent('''\
            from pyportable_runtime import inject
            globals().update(inject(__file__, globals(), locals(), {ciphertext}))
        ''')
        #   `pyportable_crypto.inject._validate_source_file`
        
        # self._cython_compiler = CythonCompiler(
        #     gconf.python_interpreter, gconf.python_version
        # )
    
    def _generate_runtime_lib(self):
        # 1.
        import Cryptodome
        copytree(dirname(Cryptodome.__file__), f'{dst_model.lib}/Cryptodome')
        
        # 2.
        src_dir = prj_model.pyportable_crypto
        tmp_dir = prj_model.temp
        dst_dir = dst_model.lib + '/pyportable_runtime'
        mkdir(dst_dir)
        
        # 3. create '__init__.py' for `pyportable_runtime`
        dumps('from .inject import inject', f'{dst_dir}/__init__.py')
        
        # 4. generate temporary 'inject.py' in tmp_dir
        code = loads(f'{src_dir}/inject.py')
        code = code.replace('{KEY}', self.__key)
        dumps(code, tmp_file := f'{tmp_dir}/inject.py')
        
        # 5. cythonize from tmp_dir/~.py to dst_dir/~.pyd
        compiler = CythonCompiler(gconf.full_python)
        compiler.compile_one(tmp_file, f'{dst_dir}/inject.pyd')
        
        # 6. cleanup tmp_dir
        compiler.cleanup()
        remove(tmp_file)
    
    def compile_all(self, *pyfiles):
        with lk.counting(len(pyfiles)):
            for i, o in pyfiles:
                lk.logtx('[D5520]', 'compiling', i, o)
    
    def compile_one(self, src_file, dst_file):
        if basename(src_file) == '__init__.py':
            lk.logt('[D0359]', 'PyportableEncryptor doesn\'t compile '
                               '\'__init__.py\' (leave it uncompiled, just '
                               'copy to the dist)', src_file)
            copyfile(src_file, dst_file)
            return dst_file
        
        data = loads(src_file)  # type: str
        data += '\n' + '__PYMOD_HOOK__.update(globals())'
        data = encrypt_data(data, self.__key)  # type: bytes
        code = self._template.format(ciphertext=data)  # type: str
        dumps(code, dst_file)
        return dst_file
    
    @property
    def key(self):
        return self.__key
