from os import mkdir
from os import remove
from os.path import basename
from shutil import copyfile
from textwrap import dedent

from lk_logger import lk
from lk_utils import dumps
from lk_utils import loads
from lk_utils.filesniff import find_filenames

from pyportable_crypto import encrypt_data
from pyportable_crypto import keygen
from .base_compiler import BaseCompiler
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
            from pyportable_crypto import inject
            globals().update(inject(__file__, globals(), locals(), {ciphertext}))
        ''')
        #   `pyportable_crypto.inject._validate_source_file`
    
    def _generate_runtime_lib(self):
        # 1.
        src_dir = prj_model.template + '/pyportable_crypto'
        tmp_dir = prj_model.temp
        dst_dir = dst_model.lib + '/pyportable_crypto'
        
        # 2. TODO: if pyportable_crypto folder structure changes, we need to
        #       recheck here.
        mkdir(dst_dir)
        for name in find_filenames(src_dir):
            # if name in ('__init__.py', 'inject.py'):
            if name == 'inject.py':
                continue
            copyfile(f'{src_dir}/{name}', f'{dst_dir}/{name}')
        
        # 3.
        # dumps('from .inject import inject', f'{dst_dir}/__init__.py')
        
        # 4.
        code = loads(f'{src_dir}/inject.py')
        code = code.replace('{KEY}', self.__key)
        dumps(code, tmp_file := f'{tmp_dir}/inject.py')
        
        # 5.
        from .cython_compiler import CythonCompiler
        compiler = CythonCompiler()
        compiler.compile_one(tmp_file, f'{dst_dir}/inject.pyd')
        
        # 6. cleanup
        compiler.cleanup()
        remove(tmp_file)
    
    def compile_all(self, *pyfiles):
        with lk.counting(len(pyfiles)):
            for i, o in pyfiles:
                lk.logtx('[D5520]', 'compiling', i, o)
                yield self.compile_one(i, o)
    
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
