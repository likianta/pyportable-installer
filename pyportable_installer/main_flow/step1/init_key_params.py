import os
import os.path

from lk_logger import lk

from . import where_is_python
from ...global_conf import gconf
from ...path_model import prj_model
from ...typehint import *

_conf = ...  # type: TConf


def init_key_params(conf: TConf, **kwargs):
    global _conf
    _conf = conf
    
    _init_proj_paths(**kwargs)
    _init_attachments_scheme()
    _init_pyversion()
    _init_platform()
    _init_pyportable_runtime_package()
    _init_python_paths()


def _init_proj_paths(**kwargs):
    gconf.pyproj_dir = kwargs['pyproj_dir']
    gconf.pyproj_file = kwargs['pyproj_file']


def _init_attachments_scheme():
    assert type(_conf['build']['attachments_exclusions']) is tuple
    gconf.attachments_exclusions = _conf['build']['attachments_exclusions']
    gconf.attachments_exist_scheme = _conf['build']['attachments_exist_scheme']


def _init_pyversion():
    pyversion = _conf['build']['python_version']
    assert pyversion, '`conf["build"]["python_version"]` not defined'
    pyversion = 'python' + pyversion.replace('.', '')  # e.g. 'python38'
    gconf.target_pyversion = pyversion


def _init_platform():
    p = _conf['build']['experimental_features']['platform']
    if p == 'system_default':
        from platform import system
        p = system().lower()  # 'windows', 'linux', 'macos'.
    
    assert p in ('windows', 'linux', 'macos'), 'platform not support'
    
    gconf.target_platform = p


def _init_pyportable_runtime_package():
    import sys
    
    if gconf.target_platform != 'windows':
        # # package_dir = {
        # #     'python38' : prj_model.pyportable_runtime_py38_linux,
        # #     'python39' : prj_model.pyportable_runtime_py39_linux,
        # #     'python310': prj_model.pyportable_runtime_py310_linux,
        # # }[gconf.target_pyversion]
        try:
            assert _conf['build']['python_version'] == '3.8'
        except AssertionError:
            raise Exception('For Linux/macOS system, the python version '
                            'accepts only 3.8 for now.')
        try:
            assert os.path.exists(prj_model.pyportable_runtime_py38_linux)
        except AssertionError:
            from textwrap import dedent
            lk.logd('interactive prompt')
            runtime_dir = input(dedent('''
                The platform you defined in project configurations requires
                pyportable_runtime package which is built on Linux. You can find
                this package in https://github.com/likianta/pyportable-installer
                (browse ~/addons/linux/pyportable_runtime_py38), and copy it
                here:
                    {}
                Then re-run this installer.
                BTW if you have downloaded that package but not copied, you can
                pass me the path of download here, to continue the process (or
                press enter to leave):
            '''.format(
                prj_model.pyportable_runtime_py38_linux
            )).strip() + ' ').strip()
            if runtime_dir == '':
                exit()
            else:
                assert os.path.exists(runtime_dir)
                prj_model.pyportable_runtime_py38_linux = runtime_dir
    
    # -------------------------------------------------------------------------
    
    if gconf.current_platform == 'windows':
        runtime_dir = {
            'python38' : prj_model.pyportable_runtime_py38,
            'python39' : prj_model.pyportable_runtime_py39,
            'python310': prj_model.pyportable_runtime_py310,
        }[gconf.current_pyversion]
        sys.path.insert(0, os.path.dirname(runtime_dir))
    else:
        sys.path.insert(0, prj_model.pyportable_runtime_py38_linux)
    
    import pyportable_runtime  # noqa
    lk.logt('[I4053]', pyportable_runtime.__path__)


def _init_python_paths():
    """
    
    Requirements:
        | venv/compiler     | full python | embed python | pip |
        | ----------------- | ----------- | ------------ | --- |
        | cython            |      Y      |              |     |
        | mypyc             |      Y      |              |     |
        | nuitka            |      Y      |              |     |
        | pip               |             |      Y       |  Y  |
        | pyarmor           |             |      Y       |     |
        | pyc               |             |      Y       |     |
        | pyportable_crypto |             |              |     |
        | source_venv       |             |      Y       |     |
        | *zipapp           |             |              |  Y  |
    
        Notes:
            - zipapp is not supported.
            - the venv/compiler list is from `typehint._TCompilerOptions` and
              `typehint._TVenvModeOptions`.
            - venv related options only available when enable_venv is True.
            - pyportable_crypto is the best option in current version.
            - the table is made for general suggestions, not responsible for the
              final decision.
    """
    name = _conf['build']['compiler']['name']  # type: TCompilerName
    mode = _conf['build']['venv']['mode']  # type: TVenvMode
    enable_venv = _conf['build']['venv']['enable_venv']  # type: bool
    
    # --------------------------------------------------------------------------
    
    is_full_python_required = False
    is_embed_python_required = False
    is_pip_required = False
    
    # 1. is_full_python_required
    if not enable_venv:
        is_full_python_required = True
    elif name in ('cython', 'mypyc', 'nuitka'):
        is_full_python_required = True
    
    # 2. is_embed_python_required
    if (
            (name in ('pyarmor', 'pyc')) or
            (enable_venv and mode == 'pip') or
            (enable_venv and mode == 'source_venv' and
             _conf['build']['venv']['options']['source_venv']['copy_venv'])
    ):
        is_embed_python_required = True
    
    # 3. is_pip_required
    if enable_venv and mode == 'pip':
        is_pip_required = True
    
    lk.logt('[I5239]',
            is_full_python_required,
            is_embed_python_required,
            is_pip_required)
    
    # --------------------------------------------------------------------------
    
    pyversion = gconf.target_pyversion
    
    if is_full_python_required:
        # noinspection PyTypedDict
        options = _conf['build']['compiler']['options'][name]
        if options.get('python_path', '') in \
                ('{auto_detect}', 'auto_detect', ''):
            try:
                gconf.full_python = where_is_python.get_full_python(pyversion)
            except FileNotFoundError:
                lk.logt(
                    '[W5951]',
                    'Cannot find installed python in your computer. Please '
                    'pass in your python path (e.g. ~/python.exe) manually.'
                )
                gconf.full_python = input(
                    f'Input file path here ({pyversion}): '
                )
        else:
            gconf.full_python = options['python_path']
        lk.logt('[I1955]', gconf.full_python)
        assert os.path.exists(gconf.full_python)
    
    # --------------------------------------------------------------------------
    
    if is_embed_python_required:
        if is_pip_required:
            gconf.embed_python = where_is_python.get_embed_python(
                pyversion, add_pip_suits=True
            )
        else:
            gconf.embed_python = (
                    where_is_python.get_embed_python_from_local(pyversion) or
                    where_is_python.get_embed_python(
                        pyversion, add_pip_suits=False
                    )
            )
        assert os.path.exists(gconf.embed_python)
