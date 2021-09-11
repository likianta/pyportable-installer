from os.path import exists

from embed_python_manager import EmbedPythonManager
from lk_logger import lk

from ...compilers.accessory import where_python_installed
from ...global_conf import gconf
from ...path_model import prj_model
from ...typehint import *


def init_key_params(conf: TConf, **kwargs):
    # pyproj_file
    gconf.pyproj_file = kwargs['pyproj_file']
    # pyproj_dir
    gconf.pyproj_dir = kwargs['pyproj_dir']
    
    # --------------------------------------------------------------------------
    
    pyversion = conf['build']['venv']['python_version']
    assert pyversion, '`conf["build"]["venv"]["python_version"]` not defined'
    pyversion = 'python' + pyversion.replace('.', '')
    gconf.python_version = pyversion
    
    # --------------------------------------------------------------------------
    
    name = conf['build']['compiler']['name']  # type: TCompilerName
    mode = conf['build']['venv']['mode']  # type: TMode
    enable_venv = conf['build']['venv']['enable_venv']  # type: bool
    
    is_full_python_required = False
    if name in ('cython', 'mypyc', 'nuitka', 'pyportable_crypto'):
        is_full_python_required = True
    
    is_embed_python_required = False
    if name in ('pyarmor', 'pyc') or \
            (enable_venv and mode in ('pip', 'source_venv')):
        is_embed_python_required = True
    
    is_pip_required = False
    if enable_venv and mode == 'pip':
        is_pip_required = True
    
    lk.loga(is_full_python_required, is_embed_python_required, is_pip_required)
    
    # --------------------------------------------------------------------------
    
    if is_full_python_required:
        options = conf['build']['compiler']['options'][name]
        if options['python_path'] in ('auto_detect', ''):
            gconf.full_python = _get_full_python(pyversion)
        else:
            gconf.full_python = options['python_path']
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
    return where_python_installed(pyversion) + '/python.exe'


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
