import re
from os.path import exists

from lk_utils import run_cmd_args

from ...global_conf import gconf


def get_full_python(pyversion):
    """
    Args:
        pyversion: str['python38', 'python39', 'python310']
    
    Returns:
        str: python executable path. note this is file path, not dir.
    """
    pyversion = '.'.join(re.search(r'(\d)(\d+)', pyversion).groups())
    # -> '3.8', '3.9', '3.10'
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
