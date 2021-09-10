from os.path import exists

from embed_python_manager import EmbedPythonManager

from ...global_conf import gconf
from ...path_model import prj_model
from ...typehint import TConf


def init_key_params(conf: TConf, **kwargs):
    # pyproj_file
    gconf.pyproj_file = kwargs['pyproj_file']
    # pyproj_dir
    gconf.pyproj_dir = kwargs['pyproj_dir']

    # --------------------------------------------------------------------------

    pyversion = conf['build']['venv']['python_version']
    pyversion = 'python' + pyversion.replace('.', '')
    gconf.python_version = pyversion

    # --------------------------------------------------------------------------

    name = conf['build']['compiler']['name']
    options = conf['build']['compiler']['options'][name]
    if name in ('cython', 'mypyc', 'nuitka', 'pyportable_crypto'):
        if options['python_path'] in ('auto_detect', ''):
            from ...compilers.accessory import where_python_installed
            gconf.full_python = where_python_installed(pyversion)
        else:
            gconf.full_python = options['python_path']

    # --------------------------------------------------------------------------
    
    if not conf['build']['venv']['enable_venv']:
        return
    
    mode = conf['build']['venv']['mode']
    if mode not in ('pip', 'source_venv'):
        return
    
    if pyversion == 'python39' and _does_pyportable_installer_have_embed_venv():
        gconf.embed_python = f'{prj_model.prj_root}/venv/python.exe'
    else:
        manager = EmbedPythonManager(pyversion)
        manager.deploy(
            add_pip_suits=True if mode == 'pip' else False,
            add_pip_scripts=False,
            add_tk_suits=False  # FIXME: check tkinter requirement
        )
        gconf.embed_python = manager.python


def _does_pyportable_installer_have_embed_venv():
    if exists(f'{prj_model.prj_root}/venv/python39._pth.bak'):
        return True
    else:
        return False
