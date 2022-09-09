import sys
from importlib import util
from os.path import basename
from os.path import exists
from types import ModuleType


def load_package_from_path(pkg_path: str) -> ModuleType:
    """
    https://stackoverflow.com/a/50395128
    """
    init_path = f'{pkg_path}/__init__.py'
    assert exists(init_path)
    name = basename(pkg_path)
    
    spec = util.spec_from_file_location(name, init_path)
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    return module
