"""
注意: 本模块在运行时而非编译时生效.
FIXME: 本模块不应放在 `pyportable_installer/compiler` 目录, 请转移.
TODO: this module is under construction.
"""
import importlib
import zipfile
from io import BytesIO

from .base_compiler import BaseRuntimeLoader


class ZipImpLoader(BaseRuntimeLoader):
    """
    References:
        https://www.codenong.com/39135750/
        https://docs.python.org/3/library/zipimport.html
    """
    
    def __init__(self, zip_file):
        with open(zip_file, 'rb') as f:
            # convert in memory bytes to file like object
            data = BytesIO(f.read())
        
        self.zip_file = zip_file
        self.zip = zipfile.ZipFile(data)
        self._paths = tuple(x.filename for x in self.zip.filelist)
    
    def find_module(self, pkg_path: str):
        """ Get path from module.
        
        Args:
            pkg_path: A full package path. e.g. 'aaa.bbb.ccc'
        """
        # Consider `aaa.bbb.ccc` as `aaa/bbb/ccc.py`
        filepath_1 = pkg_path.replace('.', '/') + '.py'
        # Consider `aaa.bbb.ccc` as `aaa/bbb/ccc/__init__.py`
        filepath_2 = pkg_path.replace('.', '/') + '/__init__.py'
        
        if filepath_1 in self._paths:
            return filepath_1, 'module'
        elif filepath_2 in self._paths:
            return filepath_2, 'package'
        else:
            raise ModuleNotFoundError
    
    def load_module(self, pkg_path):
        try:
            file, mark = self.find_module(pkg_path)
        except ModuleNotFoundError:
            raise ImportError(pkg_path)
        
        module = importlib.import_module(file)
        if mark == 'package':
            module.__package__ = pkg_path
        
        return module
