import shutil
from os import remove

from Cython.Build import cythonize
from Cython.Distutils import build_ext
from lk_utils import find_dirs
from lk_utils.filesniff import get_filename
from setuptools import Extension
from setuptools import setup

from ..path_model import prj_model


class PydCompiler:
    """
    References:
        https://github.com/TechLearnersInc/cythonizer
    """
    
    def __init__(self):
        self._temp_dir = prj_model.temp
    
    def main(self, *files):
        modules = []
        
        for file in files:
            name = get_filename(file, suffix=False)
            modules.append(Extension(
                name, [file], extra_compile_args=['-O2', '-march=native']
            ))
        
        setup(
            cmdclass={'build_ext': build_ext},
            include_dirs=[],
            ext_modules=cythonize(modules, language_level='3'),
        )
        
        self._cleanup(*files)
    
    def _cleanup(self, *files):
        for d in find_dirs(self._temp_dir):
            shutil.rmtree(d)
        for f in files:
            remove(f.rsplit('.', 1)[0] + '.c')
