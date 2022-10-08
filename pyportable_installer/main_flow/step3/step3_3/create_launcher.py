import os
import os.path as xpath
import pickle
import shutil
from secrets import token_hex

from lk_utils import dumps
from lk_utils import loads
from lk_utils import ropen
from lk_utils import wopen
from lk_utils.filesniff import filename

from ....global_conf import gconf
from ....path_model import *
from ....typehint import TBuildConf

_is_depsland_mode = False  # TODO: downgrade it to local variable
_abs_paths = ...  # type: dict
_rel_paths = ...  # type: dict


def create_launcher(build: TBuildConf):
    global _is_depsland_mode
    if build['venv']['enabled']:
        if build['venv']['mode'] == 'depsland':
            _is_depsland_mode = True
    
    # depsland setup
    if _is_depsland_mode:
        options = build['venv']['options']['depsland']
        _create_depsland_setup(
            build['launcher_name'],
            options['venv_name'],
            options['venv_id'],
            options['requirements'],
            offline=options['offline'],
            local=options['local'],
            pyversion='python' + build['python_version'].replace('.', '')
        )
    
    # depsland launcher
    if _is_depsland_mode:
        depsland_launcher_part_a = loads(prj_model.depsland_launcher_part_a)
        depsland_launcher_part_a_temp_dir = prj_model.create_temp_dir()
        # depsland_launcher_part_b = loads(prj_model.depsland_launcher_part_b)
        #   PS: `depsland_launcher_part_b`s content is same with `pyportable
        #   _installer/template/launch.bat`, there's no need to handle it
        #   specifically; just follow the procession of `_create_launcher`.
        depsland_exe_launchers_dir = f'{dst_model.build}/_exe_launchers'
        depsland_bat_launchers_dir = f'{dst_model.build}/_bat_launchers_template'
        if not xpath.exists(depsland_exe_launchers_dir):
            os.mkdir(depsland_exe_launchers_dir)
        if not xpath.exists(depsland_bat_launchers_dir):
            os.mkdir(depsland_bat_launchers_dir)
        if not xpath.exists(f'{dst_model.build}/_bat_launchers'):
            # pyportable_installer/template/depsland/launcher_part_a.bat
            os.mkdir(f'{dst_model.build}/_bat_launchers')
    else:
        depsland_launcher_part_a = None
        depsland_launcher_part_a_temp_dir = None
        depsland_exe_launchers_dir = None
        depsland_bat_launchers_dir = None
    
    # --------------------------------------------------------------------------
    
    kwargs_part_a = {}  # dynamic
    kwargs_part_b = {  # static
        'add_pywin32_support': build[
            'experimental_features']['add_pywin32_support'],
        'enable_console'     : build['enable_console'],
        'enable_venv'        : build['venv']['enabled'],
        'generate_exe'       : False if _is_depsland_mode else True,
        'module_paths'       : build['module_paths'],
        'module_paths_scheme': build['module_paths_scheme'],
    }
    
    for i, (k, v) in enumerate(build['launchers'].items()):
        kwargs_part_a.clear()
        kwargs_part_a.update({
            'name'         : k,
            'icon'         : v['icon'],
            'target'       : v,
            'is_main_entry': i == 0
        })
        file = _create_launcher(**kwargs_part_a, **kwargs_part_b)
        
        # ----------------------------------------------------------------------
        
        if _is_depsland_mode:
            # generate exe launcher and put it in `dst_model.build/_exe
            # _launchers`
            file_part_a_i = '{}/{}.bat'.format(
                depsland_launcher_part_a_temp_dir, kwargs_part_a['name']
            )
            file_part_a_o = '{}/{}.exe'.format(
                depsland_exe_launchers_dir, kwargs_part_a['name']
            )
            # update `_abs_paths['bat_file']` and `_abs_paths['exe_file']`,
            # they are global variant and will be fetched by the following
            # `_generate_exe`.
            _abs_paths['bat_file'] = file_part_a_i
            _abs_paths['exe_file'] = file_part_a_o
            dumps(depsland_launcher_part_a.format(
                LAUNCHER_NAME=kwargs_part_a['name']
            ), file_part_a_i)
            _generate_exe(
                icon=kwargs_part_a['icon'],
                show_console=kwargs_part_b['enable_console']
            )
            
            # move previous bat launcher into `dst_model.build/_bat_launchers`
            file_part_b_i = file
            file_part_b_o = '{}/{}.bat'.format(
                depsland_bat_launchers_dir, kwargs_part_a['name']
            )
            shutil.move(file_part_b_i, file_part_b_o)


def _create_launcher(
        name, icon, target, is_main_entry: bool,
        module_paths=None, module_paths_scheme='translate', **options
):
    """

    Args:
        name:
        icon:
        target:
        is_main_entry:
        **options:

    Keyword Args:
        add_pywin32_support: bool[False]
        enable_console: bool[True]
        enable_venv: bool[True]
        generate_exe: bool[True]
        module_paths: List[str]
        module_paths_scheme: Literal['translate', 'as-is']
    """
    launcher_name = name
    conf_name = '.main' if is_main_entry else token_hex(16)
    
    global _abs_paths, _rel_paths
    
    _abs_paths = {
        'target_file': src_2_dst(target['file']),
        'target_dir' : src_2_dst(xpath.dirname(target['file'])),
        'launch_file': dst_model.pylauncher,
        'launch_dir' : dst_model.src_root,
        'conf_dir'   : dst_model.pylauncher_conf,
        'conf_file'  : f'{dst_model.pylauncher_conf}/{conf_name}.pkl',
        'bat_file'   : f'{dst_model.dst_root}/{launcher_name}.bat',
        'exe_file'   : f'{dst_model.dst_root}/{launcher_name}.exe',
    }
    
    _rel0 = lambda p: relpath(p, dst_model.dst_root)  # start from dst root
    _rel1 = lambda p: relpath(p, dst_model.src_root)  # start from pylauncher dir
    _rel_paths = {
        'lib_dir'    : _rel1(dst_model.lib),  # '../lib'
        'launch_file': _rel0(_abs_paths['launch_file']),  # 'src/pylauncher.py'
        'target_dir' : _rel1(_abs_paths['target_dir']),  # 'hello_world'
        'target_file': _rel1(_abs_paths['target_file']),
        'conf_file'  : _rel1(_abs_paths['conf_file']),  # '.pylauncher_conf'
        'venv_dir'   : _rel0(dst_model.venv),  # 'venv'
        'venv_python': _rel0(dst_model.python)  # 'venv/python.exe'
    }
    del _rel0, _rel1
    
    # --------------------------------------------------------------------------
    
    _generate_target_conf(target)
    _generate_pylauncher(module_paths, module_paths_scheme)
    _generate_shell(gconf.target_platform,
                    enable_venv=options.get('enable_venv', True))
    if options.get('generate_exe', True):
        # TEST
        if gconf.target_platform == 'windows':
            _generate_exe(icon, options.get('enable_console', True))
            return _abs_paths['exe_file']
        else:
            _generate_desktop(icon)
            return _abs_paths['bat_file']
    else:
        return _abs_paths['bat_file']


def _create_depsland_setup(launcher_name, venv_name, venv_id,
                           requirements, **kwargs):
    shutil.copyfile(
        prj_model.depsland_setup_part_a,
        dst_model.depsland_setup_part_a,
    )
    
    with ropen(prj_model.depsland_setup_part_b) as f:
        template = f.read()
        
        code = template.format(
            LAUNCHER=launcher_name,
            VENV_NAME=venv_name,
            VENV_ID=venv_id,
            PYVERSION=kwargs.get('pyversion', 'python39'),
            REQUIREMENTS=requirements,
            OFFLINE=kwargs.get('offline', False),
            # # LOCAL_DIR=kwargs.get('local', ''),
            LOCAL_DIR=relpath(kwargs.get('local', None), dst_model.build)
        )
    with wopen(dst_model.depsland_setup_part_b) as f:
        f.write(code)


# class LauncherNamesDeduplicator:
#     """ Make sure there's no duplicate name generated. """
#
#     def __init__(self, *top_names):
#         self._names_counter = {}  # type: Dict[str, int]
#         self._names_counter.update({n: 0 for n in top_names})
#
#     def optimize_name(self, name, function=''):
#         if name in self._names_counter:
#             if function:
#                 name += ' ({})'.format(function)
#                 return self.optimize_name(name, '')
#             self._names_counter[name] += 1
#             name += ' ({})'.format(self._names_counter[name])
#         else:
#             self._names_counter[name] = 0
#         return name


# ------------------------------------------------------------------------------

def _generate_target_conf(target):
    with open(_abs_paths['conf_file'], 'wb') as f:
        target_dir = _rel_paths['target_dir']
        target_file = _rel_paths['target_file']
        target_pkg = ''
        # target_pkg = target_dir.replace('/', '.')
        target_mod = '{}.{}'.format(
            target_dir.replace('/', '.'),
            filename(_abs_paths['target_file'], suffix=False)
        )
        
        pickle.dump({
            'TARGET_DIR'   : target_dir,
            'TARGET_FILE'  : target_file,
            'TARGET_PKG'   : target_pkg,
            'TARGET_MOD'   : target_mod,
            # 'TARGET_NAME'  : xpath.basename(target_file).rsplit('.', 1)[0],
            'TARGET_NAME'  : filename(target_file, suffix=False),
            'TARGET_FUNC'  : target['function'],
            'TARGET_ARGS'  : target['args'],
            'TARGET_KWARGS': target['kwargs'],
        }, f)


def _generate_pylauncher(module_paths, module_paths_scheme, **options):
    if module_paths_scheme == 'translate':
        _ext_paths = list(map(
            lambda d: relpath(
                d if not d.startswith('src:') else src_2_dst(d[4:]),
                #   FIXME: this is a temp measure. see source point at
                #       `pyportable_installer/main_flow/step1/indexing_paths.py
                #        > vars:module_paths`
                start=_abs_paths['launch_dir']
            ),
            module_paths
        ))
    else:  # leave module paths as is. (usually used for debug mode)
        _ext_paths = list(map(
            lambda d: d[4:] if d.startswith('src:') else d,
            module_paths
        ))
    
    with ropen(prj_model.pylauncher) as f:
        template = f.read()
        code = template.format(
            # see `~/template/pylauncher.txt > docs:placeholders`
            PROJ_LIB_DIR=_rel_paths['lib_dir'],
            ADD_PYWIN32_SUPPORT=str(
                options.get('add_pywin32_support', False)),
            MODULE_PATHS=str(_ext_paths),
        )
    
    with wopen(_abs_paths['launch_file']) as f:
        f.write(code)


def _generate_shell(system, **kwargs):
    def dump_with_crlf_to_lf(code, file_o):
        # convert CRLF to LF
        # https://stackoverflow.com/questions/47178459/replace-crlf-with-lf-in
        # -python-3-6/53657266
        with open(file_o, 'wb') as f:
            f.write(code.encode('utf-8').replace(b'\r\n', b'\n'))
    
    if system == 'windows':
        _generate_bat(**kwargs)
    elif system == 'linux' or system == 'darwin':  # TEST
        template = loads(prj_model.template + '/launch.sh')
        code = template.format(PYTHON='python3', PYCONF=_rel_paths['conf_file'])
        dump_with_crlf_to_lf(
            code, _abs_paths['exe_file'].replace('.exe', '.sh')  # PERF
        )
    else:
        raise Exception(system)


def _generate_bat(enable_venv):
    with ropen(prj_model.launch_bat) as f:
        template = f.read()
        
        if _is_depsland_mode:
            code = template.format(
                PYTHON='{PYTHON}',  # remain placeholder for the client
                #   side, this value will be filled when user runs depsland
                #   installer.
                #   see `~/template/setup_for_depsland.txt > section
                #   :generate launcher`
                PYLAUNCHER='../../' + _rel_paths['launch_file'],
                #   TODO: to be explained (why we use '../../')
                PYCONF=_rel_paths['conf_file']
            )
        elif enable_venv:
            code = template.format(
                PYTHON=_rel_paths['venv_python'].replace('/', '\\'),
                PYLAUNCHER=_rel_paths['launch_file'],
                PYCONF=_rel_paths['conf_file']
            )
        else:
            code = template.format(
                PYTHON=gconf.full_python,
                PYLAUNCHER=_rel_paths['launch_file'],
                PYCONF=_rel_paths['conf_file']
            )
    
    with wopen(_abs_paths['bat_file']) as f:
        f.write(code)


def _generate_exe(icon, show_console):
    from .bat_2_exe import bat_2_exe
    bat_2_exe(
        file_i=_abs_paths['bat_file'],
        file_o=_abs_paths['exe_file'],
        icon=icon,
        show_console=show_console
    )
    
    # then delete bat file
    os.remove(_abs_paths['bat_file'])


def _generate_desktop(icon):  # noqa  # TODO
    """ Generate Linux desktop launcher with icon.
    
    References:
        https://juejin.cn/post/6844904127047139342
    """
    pass
