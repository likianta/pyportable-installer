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
    if name in ('cython', 'mypyc', 'nuitka'):
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
            return path


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
