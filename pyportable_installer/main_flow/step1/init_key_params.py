import os
import re
from os.path import dirname
from os.path import exists

from embed_python_manager import EmbedPythonManager
from lk_logger import lk
from lk_utils import run_cmd_shell
from lk_utils.filesniff import normpath

from ...global_conf import gconf
from ...path_model import prj_model
from ...typehint import *


def init_key_params(conf: TConf, **kwargs):
    # pyproj_file
    gconf.pyproj_file = kwargs['pyproj_file']
    # pyproj_dir
    gconf.pyproj_dir = kwargs['pyproj_dir']
    
    # --------------------------------------------------------------------------
    # attachments
    
    gconf.attachments_exclusions = conf['build']['attachments_exclusions']
    assert type(gconf.attachments_exclusions) is tuple
    gconf.attachments_exist_scheme = conf['build']['attachments_exist_scheme']
    
    # --------------------------------------------------------------------------
    
    pyversion = conf['build']['venv']['python_version']
    assert pyversion, '`conf["build"]["venv"]["python_version"]` not defined'
    pyversion = 'python' + pyversion.replace('.', '')
    gconf.python_version = pyversion
    
    # --------------------------------------------------------------------------
    
    name = conf['build']['compiler']['name']  # type: TCompilerName
    mode = conf['build']['venv']['mode']  # type: TVenvMode
    enable_venv = conf['build']['venv']['enable_venv']  # type: bool
    
    is_full_python_required = False
    if not enable_venv:
        is_full_python_required = True
    elif name in ('cython', 'mypyc', 'nuitka'):
        is_full_python_required = True
    elif name == 'pyportable_crypto':
        key = conf['build']['compiler']['options'][name]['key']
        if key != '_trial' and not key.startswith('path:'):
            is_full_python_required = True
    
    is_embed_python_required = False
    if (
            (name in ('pyarmor', 'pyc')) or
            (enable_venv and mode == 'pip') or
            (enable_venv and mode == 'source_venv' and
             conf['build']['venv']['options']['source_venv']['copy_venv'])
    ):
        is_embed_python_required = True
    
    if name == 'pyportable_crypto':
        key = conf['build']['compiler']['options'][name]['key']
        if key.startswith('path:') and pyversion != 'python39':
            is_embed_python_required = True
    
    if name in ('pyarmor', 'pyc') or \
            (enable_venv and mode in ('pip', 'source_venv')):
        is_embed_python_required = True
    
    is_pip_required = False
    if enable_venv and mode == 'pip':
        is_pip_required = True
    
    lk.logt('[I5239]',
            is_full_python_required,
            is_embed_python_required,
            is_pip_required)
    
    # --------------------------------------------------------------------------
    
    if is_full_python_required:
        # noinspection PyTypedDict
        options = conf['build']['compiler']['options'][name]
        if options['python_path'] in ('_auto_detect', 'auto_detect', ''):
            gconf.full_python = _get_full_python(pyversion)
        else:
            if (p := options['python_path']).endswith('python.exe'):
                lk.logt(
                    '[W2320]',
                    'please do not pass "{}" path to `{}`, use "{}" instead. '
                    'the exe-path support may be removed in the future.'.format(
                        p, 'pyproject.json > build:compiler:options:{}:'
                           'python_path'.format(name), dirname(p)
                    )
                )
                gconf.full_python = p
            else:
                gconf.full_python = p + '/python.exe'
        lk.loga(gconf.full_python)
        assert exists(gconf.full_python)
    
    # --------------------------------------------------------------------------
    
    if is_embed_python_required:
        if is_pip_required:
            gconf.embed_python = _get_embed_python(pyversion, True)
        else:
            gconf.embed_python = _get_embed_python_from_local(pyversion) or \
                                 _get_embed_python(pyversion, False)
        assert exists(gconf.embed_python)


def _get_full_python(pyversion):
    def where_python_installed(pyversion: str):  # pyversion: e.g. 'python39'
        """
        PS: 'full python' means a full featured python, i.e. the regular python
            installed in your computer.
        
        There're two ways to search for full python:
            1. Use `py -{pyversion} ...`
               This is introduced since Python 3.3. See https://docs.python.org
               /3/using/windows.html#launcher for more information.
               Note that there're several inadequacies:
               1. It supports only Python 3.3+.
               2. If user has installed a Python version in user-only position,
                  it doesn't work.
            2. Look for the most frequently used positions. Include system
               environment variables.

        Returns:
            The full python dir. For example: 'C:/Program Files/Python38'
        """
        if pyversion.startswith('python3'):
            # if int(pyversion.removeprefix('python')) >= 33
            try:
                ret = run_cmd_shell(
                    'py -{} -c "import sys;print(sys.executable)"'.format(
                        '3' + '.' + pyversion.removeprefix('python3')
                    )
                )
                return normpath(ret).removesuffix('/python.exe')
            except:
                pass
        
        for v in filter(None, os.getenv('PATH').lower().split(';')):
            if re.search(rf'[/\\]{pyversion}[/\\]?$', v):
                return normpath(v).rstrip('/')
        
        available_paths = (
            f'{os.path.expanduser("~")}'
            + '/appdata/local/programs/python/{pyversion}',
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
    
    try:
        return where_python_installed(pyversion) + '/python.exe'
    except FileNotFoundError as e:
        lk.logt("[E5951]", 'Cannot find installed python in your computer. '
                           'Please pass in your python path manually (for '
                           'example "C:\\Program Files\\Python38") ...')
        path = input(f'Input path here ({pyversion}): ')
        if not exists(path):
            raise e
        else:
            return normpath(path) + '/python.exe'


def _get_embed_python_from_local(pyversion):
    if pyversion == 'python39' and \
            exists(f'{prj_model.prj_root}/venv/python39._pth.bak'):
        return f'{prj_model.prj_root}/venv/python.exe'
    else:
        return ''


def _get_embed_python(pyversion, add_pip_suits: bool):
    manager = EmbedPythonManager(pyversion)
    manager.change_source('npm_taobao_org.yml')
    manager.deploy(
        add_pip_suits=add_pip_suits,
        add_pip_scripts=False,
        add_tk_suits=False  # FIXME: check tkinter requirement
    )
    return manager.python
