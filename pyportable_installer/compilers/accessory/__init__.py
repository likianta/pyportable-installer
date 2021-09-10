import os
import re


def where_python_installed(pyversion: str):  # pyversion: e.g. 'python39'
    for v in filter(None, os.getenv('PATH').lower().split(';')):
        if re.search(rf'[/\\]{pyversion}[/\\]?$', v):
            return v.rstrip('/\\')
    
    available_paths = (
        f'{os.path.expanduser("~")}/appdata/local/programs/python/{pyversion}',
        f'c:/program files/{pyversion}',
        f'c:/program files (x86)/{pyversion}',
        f'c:/program files (x86)/{pyversion}',
        f'd:/program files/{pyversion}',
        f'd:/program files (x86)/{pyversion}',
        f'd:/program files (x86)/{pyversion}',
        f'e:/program files/{pyversion}',
        f'e:/program files (x86)/{pyversion}',
        f'e:/program files (x86)/{pyversion}',
    )
    
    for p in available_paths:
        if os.path.exists(p):
            return p
    
    raise FileNotFoundError(
        'Auto detection failed finding avaiable executable python in your '
        'computer. Please make sure you have installed the required Python '
        f'(version {pyversion[6:]}) in your computer and fill the path in '
        f'your "~/pyproject.json" file.'
    )
