import os
import os.path as xpath
import pickle
import shutil
from secrets import token_hex

from lk_logger import lk
from lk_utils import dumps
from lk_utils import loads
from lk_utils import ropen
from lk_utils import wopen
from lk_utils.filesniff import get_filename
from lk_utils.subproc import run_new_thread

from .bat_2_exe import bat_2_exe
from ....path_model import *
from ....typehint import TBuildConf

thread_pool = {}  # {bat_file: thread, ...}
_is_depsland_mode = False  # TODO: downgrade it to local variable
_abs_paths = ...  # type: dict
_rel_paths = ...  # type: dict


def create_launcher(build: TBuildConf):
    global _is_depsland_mode
    _is_debug_mode = False
    if build['venv']['enable_venv']:
        if build['venv']['mode'] == 'depsland':
            _is_depsland_mode = True
        elif build['venv']['mode'] == '_no_venv':
            _is_debug_mode = True
    
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
            pyversion='python' + build['venv'][
                'python_version'].replace('.', '')
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
    
    deduplicator = LauncherNamesDeduplicator(build['launcher_name'])
    kwargs_part_a = {}
    kwargs_part_b = {
        'add_pywin32_support': build[
            'experimental_features']['add_pywin32_support'],
        'enable_console'     : build['enable_console'],
        'enable_venv'        : build['venv']['enable_venv'],
        'generate_exe'       : False if _is_depsland_mode or
                                        _is_debug_mode else True,
        'module_paths'       : build['module_paths'],
        'module_paths_scheme': build['module_paths_scheme'],
        'venv_python'        : 'python' if _is_debug_mode else '',
    }
    
    for i, t in enumerate(build['target']):
        kwargs_part_a.clear()
        if i == 0:
            kwargs_part_a.update({
                'name'         : build['launcher_name'],
                'icon'         : build['icon'],
                'target'       : t,
                'is_main_entry': True
            })
        else:
            name = get_filename(t['file'], suffix=False)
            name = deduplicator.optimize_name(name, t['function'])
            kwargs_part_a.update({
                'name'         : name,
                'icon'         : '',
                'target'       : t,
                'is_main_entry': False
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
                enable_console=kwargs_part_b['enable_console']
            )
            
            # move previous bat launcher into `dst_model.build/_bat_launchers`
            file_part_b_i = file
            file_part_b_o = '{}/{}.bat'.format(
                depsland_bat_launchers_dir, kwargs_part_a['name']
                #   PS: kwargs_part_a['name'] == \
                #       xpath.basename(file).removesuffix('.bat')
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
        enable_venv:
        generate_exe: bool[True]
        module_paths: list[str]
        module_paths_scheme: Literal['translate', 'leave as-is']
        venv_python: str
    """
    launcher_name = name
    conf_name = 'main' if is_main_entry else token_hex(16)
    
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
    
    _rel0 = lambda p: relpath(p, dst_model.dst_root)  # starts from dst root
    _rel1 = lambda p: relpath(p, dst_model.src_root)  # strats from pylauncher dir
    _rel_paths = {
        'lib_dir'    : _rel1(dst_model.lib),  # '../lib'
        'launch_file': _rel0(_abs_paths['launch_file']),  # 'src/pylauncher.py'
        'target_dir' : _rel1(_abs_paths['target_dir']),  # 'hello_world'
        'conf_file'  : _rel1(_abs_paths['conf_file']),  # '.pylauncher_conf'
        'venv_dir'   : _rel0(dst_model.venv),  # 'venv'
        'venv_python': options.get('venv_python') or
                       _rel0(dst_model.python)  # 'venv/python.exe'
    }
    del _rel0, _rel1
    
    # --------------------------------------------------------------------------
    
    _generate_target_conf(target)
    _generate_pylauncher(module_paths, module_paths_scheme)
    _generate_bat(is_main_entry, options.get('enable_venv', True))
    if options.get('generate_exe', True):
        _generate_exe(icon, options.get('enable_console', True))
        return _abs_paths['exe_file']
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


class LauncherNamesDeduplicator:
    """ Make sure there's no duplicate name generated. """
    
    def __init__(self, *top_names):
        self._names_counter = {}  # type: dict[str, int]
        self._names_counter.update({n: 0 for n in top_names})
    
    def optimize_name(self, name, function=''):
        if name in self._names_counter:
            if function:
                name += ' ({})'.format(function)
                return self.optimize_name(name, '')
            self._names_counter[name] += 1
            name += ' ({})'.format(self._names_counter[name])
        else:
            self._names_counter[name] = 0
        return name


# ------------------------------------------------------------------------------

def _generate_target_conf(target):
    with open(_abs_paths['conf_file'], 'wb') as f:
        target_dir = _rel_paths['target_dir']
        target_pkg = ''
        # target_pkg = target_dir.replace('/', '.')
        target_mod = '{}.{}'.format(
            target_dir.replace('/', '.'),
            get_filename(_abs_paths['target_file'], suffix=False)
        )
        
        pickle.dump({
            'TARGET_DIR'   : target_dir,
            'TARGET_PKG'   : target_pkg,
            'TARGET_MOD'   : target_mod,
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
    else:  # leave module paths as is. (usually this is used in debug mode)
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
            # DEFAULT_CONF='default.pkl',
        )
    
    with wopen(_abs_paths['launch_file']) as f:
        f.write(code)


def _generate_bat(is_main_entry, enable_venv):
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
                PYCONF='%*' if is_main_entry else _rel_paths['conf_file']
            )
            #   '%*' supports passing multiple arguments to python. for
            #   example:
            #       example.bat:
            #           python test.py %*
            #       test.py
            #           import sys
            #           print(sys.argv)
            #       cmd:
            #           example.bat hello world 1 2 3
            #       output in console:
            #           ['test.py', 'hello', 'world', '1', '2', '3']
        elif enable_venv:
            code = template.format(
                PYTHON=_rel_paths['venv_python'].replace('/', '\\'),
                PYLAUNCHER=_rel_paths['launch_file'],
                PYCONF='%*' if is_main_entry else _rel_paths['conf_file']
            )
        else:
            code = template.format(
                PYTHON='python',  # use system python which is defined in
                #   global environment variable (PATH).
                PYLAUNCHER=_rel_paths['launch_file'],
                PYCONF='%*' if is_main_entry else _rel_paths['conf_file']
            )
    
    with wopen(_abs_paths['bat_file']) as f:
        f.write(code)


def _generate_exe(icon, enable_console):
    def _run(bat_file, exe_file, icon_file, *options):
        lk.loga('converting bat to exe ... '
                '(it may take several seconds ~ one minute)')
        bat_2_exe(bat_file, exe_file, icon_file, *options)
        lk.loga('convertion bat-to-exe done')
    
    # this is a time-consuming operation (persists 1-10 seconds), we put it
    # in a sub thread_of_bat_2_exe.
    thread_pool[_abs_paths['bat_file']] = run_new_thread(
        _run, _abs_paths['bat_file'], _abs_paths['exe_file'], icon, '/x64',
        '' if enable_console else '/invisible'
    )
    #   the thread_of_bat_2_exe will be recycled in `..step3_4.cleanup`.
