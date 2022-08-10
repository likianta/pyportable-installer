import re
from os.path import exists

from lk_utils import run_cmd_args

from ...global_conf import gconf
from ...path_model import prj_model


def get_full_python(pyversion):
    """
    Args:
        pyversion: str['python38', 'python39', 'python310']
    
    Returns:
        str: python executable path. note this is file path, not dir.
    """
    import sys
    
    pyversion = '.'.join(re.search(r'(\d)(\d+)', pyversion).groups())
    # -> '3.8', '3.9', '3.10'
    
    if sys.version.startswith(pyversion):
        return sys.executable
    
    if gconf.current_platform == 'windows':
        path = run_cmd_args(
            'py', f'-{pyversion}', '-c', 'import sys; print(sys.executable)'
        )
        if ' not found!' in path:
            ''' e.g.
                Python 3.11 not found!
                Installed Pythons found by py Launcher for Windows
                 -3.10-64 *
                 -3.9-64
                 -3.8-64
                 -2.7-64
            '''
            raise FileNotFoundError(path)
        return path
    else:
        path = f'/usr/bin/python{pyversion}'
        if not exists(path):
            raise FileNotFoundError(path)
        return path


def get_embed_python(pyversion, add_pip_suits: bool):
    from embed_python_manager import EmbedPythonManager
    manager = EmbedPythonManager(pyversion)
    manager.change_source('npm_taobao_org.yml')
    manager.deploy(
        add_pip_suits=add_pip_suits,
        add_pip_scripts=False,
        add_tk_suits=False  # FIXME: check tkinter requirement
    )
    return manager.python


def get_embed_python_from_local(pyversion):
    if pyversion == 'python38' and \
            exists(f'{prj_model.prj_root}/venv/python38._pth.bak'):
        return f'{prj_model.prj_root}/venv/python.exe'
    else:
        return ''
