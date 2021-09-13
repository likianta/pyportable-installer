import pickle
from os.path import dirname
from shutil import copyfile
from uuid import uuid1

from lk_logger import lk
from lk_utils import ropen
from lk_utils import wopen
from lk_utils.filesniff import get_filename
from lk_utils.subproc import run_new_thread

from ....bat_2_exe import bat_2_exe
from ....path_model import *
from ....typehint import TBuildConf

thread_of_bat_2_exe = None
_is_depsland_mode = False  # TODO: downgrade it to local variable


def create_launcher(build: TBuildConf):
    global _is_depsland_mode
    _is_debug_mode = False
    if build['venv']['enable_venv']:
        if build['venv']['mode'] == 'depsland':
            _is_depsland_mode = True
        elif build['venv']['mode'] == '_no_venv':
            _is_debug_mode = True
    #   these will effect `_create_launcher` function.
    
    deduplicator = LauncherNamesDeduplicator(build['launcher_name'])
    fixed_kwargs_for_creating_launcher = {
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
        if i == 0:
            _create_launcher(
                name=build['launcher_name'], icon=build['icon'],
                target=t, is_main_entry=True,
                **fixed_kwargs_for_creating_launcher
            )
            
            if _is_depsland_mode:
                options = build['venv']['options']['depsland']
                _create_depsland_setup(
                    build['launcher_name'], build['icon'],
                    options['venv_name'], options['venv_id'],
                    options['requirements'], build['enable_console'],
                    offline=options['offline'], local=options['local']
                )
        else:
            name = get_filename(t['file'], suffix=False)
            name = deduplicator.optimize_name(name, t['function'])
            _create_launcher(
                name=name, icon='',
                target=t, is_main_entry=False,
                **fixed_kwargs_for_creating_launcher
            )


def _create_launcher(
        name, icon, target, is_main_entry: bool,
        module_paths=None, module_paths_scheme='translate',
        enable_venv=True, **options
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
    conf_name = 'main' if is_main_entry else str(uuid1())
    
    abs_paths = {
        'target_file': src_2_dst(target['file']),
        'target_dir' : src_2_dst(dirname(target['file'])),
        'launch_file': dst_model.pylauncher,
        'launch_dir' : dst_model.src_root,
        'conf_dir'   : dst_model.pylauncher_conf,
        'conf_file'  : f'{dst_model.pylauncher_conf}/{conf_name}.pkl',
        'bat_file'   : f'{dst_model.dst_root}/{launcher_name}.bat',
        'exe_file'   : f'{dst_model.dst_root}/{launcher_name}.exe',
    }
    
    if _is_depsland_mode:
        abs_paths['bat_file'] = f'{dst_model.build}/{launcher_name}.bat'
        abs_paths['exe_file'] = ''
    
    # if not exists(d := abs_paths['conf_dir']):
    #     mkdir(d)
    
    _rel0 = lambda p: relpath(p, dst_model.dst_root)  # starts from dst root
    _rel1 = lambda p: relpath(p, dst_model.src_root)  # strats from pylauncher dir
    rel_paths = {
        'lib_dir'    : _rel1(dst_model.lib),  # '../lib'
        'launch_file': _rel0(abs_paths['launch_file']),  # 'src/pylauncher.py'
        'target_dir' : _rel1(abs_paths['target_dir']),  # 'hello_world'
        'conf_file'  : _rel1(abs_paths['conf_file']),  # '.pylauncher_conf'
        'venv_dir'   : _rel0(dst_model.venv),  # 'venv'
        'venv_python': options.get('venv_python') or
                       _rel0(dst_model.python)  # 'venv/python.exe'
    }
    del _rel0, _rel1
    
    # --------------------------------------------------------------------------
    
    def _generate_target_conf():
        with open(abs_paths['conf_file'], 'wb') as f:
            target_dir = rel_paths['target_dir']
            target_pkg = ''
            # target_pkg = target_dir.replace('/', '.')
            target_mod = '{}.{}'.format(
                target_dir.replace('/', '.'),
                get_filename(abs_paths['target_file'], suffix=False)
            )
            
            pickle.dump({
                'TARGET_DIR'   : target_dir,
                'TARGET_PKG'   : target_pkg,
                'TARGET_MOD'   : target_mod,
                'TARGET_FUNC'  : target['function'],
                'TARGET_ARGS'  : target['args'],
                'TARGET_KWARGS': target['kwargs'],
            }, f)
    
    def _generate_pylauncher():
        if module_paths_scheme == 'translate':
            _ext_paths = list(map(
                lambda d: relpath(
                    d if not d.startswith('src:') else src_2_dst(d[4:]),
                    #   FIXME: this is a temp measure. see source point at
                    #       `pyportable_installer/main_flow/step1/indexing_paths.py
                    #        > vars:module_paths`
                    start=abs_paths['launch_dir']
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
                PROJ_LIB_DIR=rel_paths['lib_dir'],
                ADD_PYWIN32_SUPPORT=str(
                    options.get('add_pywin32_support', False)),
                MODULE_PATHS=str(_ext_paths),
                # DEFAULT_CONF='default.pkl',
            )
        
        with wopen(abs_paths['launch_file']) as f:
            f.write(code)
    
    def _generate_bat():
        with ropen(prj_model.launch_bat) as f:
            template = f.read()
            
            if _is_depsland_mode:
                code = template.format(
                    PYTHON='{PYTHON}',  # remain placeholder for the client
                    #   side, this value will be filled when user runs depsland
                    #   installer.
                    #   see `~/template/setup_for_depsland.txt > section
                    #   :generate launcher`
                    PYLAUNCHER=rel_paths['launch_file'],
                    PYCONF='%*' if is_main_entry else rel_paths['conf_file']
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
                    PYTHON=rel_paths['venv_python'].replace('/', '\\'),
                    PYLAUNCHER=rel_paths['launch_file'],
                    PYCONF='%*' if is_main_entry else rel_paths['conf_file']
                )
            else:
                code = template.format(
                    PYTHON='python',  # use system python which is defined in
                    #   global environment variable (PATH).
                    PYLAUNCHER=rel_paths['launch_file'],
                    PYCONF='%*' if is_main_entry else rel_paths['conf_file']
                )
        
        with wopen(abs_paths['bat_file']) as f:
            f.write(code)
    
    def _generate_exe():
        if options.get('generate_exe', True) is False:
            return
        
        def _run(bat_file, exe_file, icon_file, *options):
            lk.loga('converting bat to exe ... '
                    '(it may take several seconds ~ one minute)')
            bat_2_exe(bat_file, exe_file, icon_file, *options)
            lk.loga('convertion bat-to-exe done')
        
        # this is a time-consuming operation (persists 1-10 seconds), we put it
        # in a sub thread_of_bat_2_exe.
        global thread_of_bat_2_exe
        thread_of_bat_2_exe = run_new_thread(
            _run, abs_paths['bat_file'], abs_paths['exe_file'], icon, '/x64',
            '' if options.get('enable_console', True) else '/invisible'
        )
        #   the thread_of_bat_2_exe will be recycled in `..step3_4.cleanup`.
    
    _generate_target_conf()
    _generate_pylauncher()
    _generate_bat()
    _generate_exe()
    
    return abs_paths['exe_file'] or abs_paths['bat_file']


def _create_depsland_setup(launcher_name, icon,
                           venv_name, venv_id, requirements,
                           enable_console=True, **kwargs):
    with ropen(prj_model.setup_for_depsland) as f:
        template = f.read()
        
        code = template.format(
            LAUNCHER=launcher_name,
            VENV_NAME=venv_name,
            VENV_ID=venv_id,
            REQUIREMENTS=requirements,
            OFFLINE=kwargs.get('offline', False),
            LOCAL_DIR=kwargs.get('local', ''),
            INVISIBLE='' if enable_console else '/invisible'
        )
    
    with wopen(dst_model.setup_py) as f:
        f.write(code)
    
    copyfile(
        prj_model.setup_for_depsland_bat,
        dst_model.setup_bat,
    )
    
    if icon:
        copyfile(icon, f'{dst_model.build}/launcher.ico')


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
