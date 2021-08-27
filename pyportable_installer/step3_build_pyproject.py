import pickle
from uuid import uuid1

from lk_utils.read_and_write import ropen, wopen

from .assets_copy import *
from .compiler import get_compiler
from .embed_python import EmbedPythonManager
from .typehint import *
from .utils import runnin_new_thread
from .venv_builder import create_venv

thread = None


def main(
        launcher_name, proj_dir: TPath, dist_dir: TPath,
        target: TTarget,
        side_utils: list[TTarget],
        venv: TVenvBuildConf,
        compiler: TCompiler,
        module_paths: list[TPath],
        attachments: TAttachments,
        **misc
):
    """
    
    Project Structure Example:
        hello_world_project
        |= hello_world  # <- `params:proj_dir`
            |- main.py  # <- script launcher
        |= dist
            |= hello_world_1.0.0  # <- `params:dist_dir`
                |= build  # <- `vars:build_dir`
                |= lib    # <- `vars:lib_dir`
                |= src    # <- `vars:src_dir`
                |= venv   # <- `vars:venv_dir`
                |- ...
    
    Args:
        launcher_name: launcher name
        proj_dir: See `this_docstring: Project Structure Example`.
        dist_dir: See `this_docstring: Project Structure Example`.
            Note this directory is equivalent to `global_dirs.py::global_vars
            :global_dirs::attrs:dst_root`, this is the parent dir of that.
        target: See `docs/pyproject-template.md::build:target`
        side_utils:
        module_paths: See `func:_create_launcher`
        attachments: See `assets_copy.py::copy_assets::docstring:attachments`
        venv: See `docs/pyproject-template.md::build:venv`
        compiler: Literal['pyarmor', 'pyc', 'pycrypto']. Compiler name.
        **misc: See `typehint.TMisc`
            Some keys are from `main.py:main:conf['build']` (e.g. 'readme',
            'icon', 'enable_console'), the others are from `main.py::class:Misc
            ::dump`.
    
    Warnings:
        请勿随意更改本函数的参数名, 这些名字与 `template/pyproject.json` 的诸多
        键名有关系, 二者名字需要保持一致.
    """
    # init args
    readme_file = misc.get('readme', '')
    
    # precheck
    _precheck(proj_dir, dist_dir, readme_file, attachments)
    
    # see `../docs/devnote/dist-folders-structure.md`
    # these dirs already exist, see creation at `no2_prebuild_pyproject.py:cmt
    # :'create build_dir, lib_dir, src_dir'`
    root_dir, build_dir, src_dir, lib_dir = (
        dist_dir, f'{dist_dir}/build', f'{dist_dir}/src', f'{dist_dir}/lib'
    )
    #   root_dir    'root directory'
    #   build_dir   'build (noun.) directory'
    #   src_dir     'source directory'. note: this is equivalent to
    #               `global_dirs.py::global_vars:global_dirs::attrs:dst_root`
    
    # --------------------------------------------------------------------------
    
    # build_dir
    if misc.get('create_checkup_tools', True):
        copy_checkup_tool(global_dirs.local('checkup'), build_dir)
    
    # readme_file
    if readme_file:
        create_readme(readme_file, f'{root_dir}/{ospath.basename(readme_file)}')
    
    # venv
    embed_py_mgr = EmbedPythonManager(venv['python_version'])
    # FIXME
    if venv['enable_venv']:
        if venv['mode'] == 'depsland':
            pass
        elif venv['mode'] == 'embed_python':
            options = venv['options'][venv['mode']]
            shutil.copytree(
                options['path'], f'{root_dir}/venv'
            )
        else:
            create_venv(
                embed_py_mgr, venv, root_dir,
                misc.get('how_venv_created', 'copy')
            )
    
    # --------------------------------------------------------------------------
    # compile
    
    # get a compiler
    if venv['enable_venv']:
        pyinterpreter = embed_py_mgr.get_embed_python_interpreter()
    else:
        pyinterpreter = 'python'  # default python in system environment
    from .utils import set_pyinterpreter
    set_pyinterpreter(pyinterpreter)
    
    compiler = get_compiler(
        compiler['name'], pyinterpreter,
        lib_dir=lib_dir, pyversion=embed_py_mgr.pyversion
    )
    
    pyfiles_to_compile = []  # type: TPyFilesToCompile
    pyfiles_to_compile.extend(copy_sources(proj_dir))
    pyfiles_to_compile.extend(copy_assets(attachments))
    
    # noinspection PyUnusedLocal
    for i, options in enumerate((target, *side_utils)):
        # module_paths.insert(0, ospath.dirname(proj_dir))
        _is_depsland_mode = bool(venv['mode'] == 'depsland')
        _icon = misc.get('icon', '') if i == 0 else ''
        
        _bat_file = _create_launcher(
            root_dir, ospath.dirname(global_dirs.to_dist(proj_dir)),
            launcher_name, _icon, options,
            is_main_conf=bool(i == 0),
            extend_sys_paths=module_paths,
            enable_venv=venv['enable_venv'],
            enable_console=misc.get('enable_console', True),
            generate_bat=misc.get('create_launch_bat', True),
            generate_exe=not _is_depsland_mode,
            depsland_mode=_is_depsland_mode
        )
        
        if _is_depsland_mode:
            options = venv['options']['depsland']
            _create_depsland_setup(
                root_dir, launcher_name, _icon, **options,
                enable_console=misc.get('enable_console', True)
            )
            shutil.move(_bat_file, f'{root_dir}/build/{launcher_name}.bat')
            # do not generate side utils in depsland mode
            break  # FIXME
    
    # lk.logp('[D2021]', pyfiles_to_compile)
    if misc.get('compile_scripts', True):
        compiler.compile_all(pyfiles_to_compile)
    else:
        for src_file, dst_file in pyfiles_to_compile:
            shutil.copyfile(src_file, dst_file)
    
    return root_dir


# ------------------------------------------------------------------------------

def _precheck(prj_dir, dst_dir, readme_file, attachments):
    assert ospath.exists(prj_dir)
    assert ospath.exists(dst_dir)
    assert ospath.exists(f'{dst_dir}/build')
    assert ospath.exists(f'{dst_dir}/lib')
    assert ospath.exists(f'{dst_dir}/src')
    assert readme_file == '' or ospath.exists(readme_file)
    assert all(map(ospath.exists, attachments.keys()))


def _create_launcher(
        root_dir, proj_dir,
        launcher_name, icon, target, is_main_conf: bool,
        extend_sys_paths=None, enable_venv=True, enable_console=True,
        generate_pylauncher=True, generate_bat=True, generate_exe=True,
        **kwargs
):
    """ Create launcher ({srcdir}/bootloader.py).
    
    详细说明
        启动器分为两部分, 一个是启动器图标, 一个引导装载程序.
        启动器图标位于: '{root_dir}/{app_name}.exe'
        引导装载程序位于: '{proj_dir}/pylauncher.py'
    
        1. 二者的体积都非常小
        2. 启动器本质上是一个带有自定义图标的 bat 脚本. 它指定了 Python 编译器的
           路径和 pylauncher.py 的路径, 通过调用编译器执行 pylauncher.py
        3. pylauncher.py 主要完成了以下两项工作:
            1. 更新 sys.path
            2. 获取 target 的相关信息
            3. 调用 target, 并捕获可能的报错, 并输出打印到控制台
    
    Returns:
        launch_file: '{root_dir}/src/pylauncher.py'
    """
    conf_filename = 'default' if is_main_conf else str(uuid1())
    
    abs_paths = {
        'target_file': target['file'],
        'target_dir' : global_dirs.to_dist(ospath.dirname(target['file'])),
        'launch_file': f'{proj_dir}/pylauncher.py',
        'launch_dir' : f'{proj_dir}',
        'conf_dir'   : f'{proj_dir}/.pylauncher_conf',
        'conf_file'  : f'{proj_dir}/.pylauncher_conf/{conf_filename}.pkl',
        'bat_file'   : f'{root_dir}/{launcher_name}.bat',
        'exe_file'   : f'{root_dir}/{launcher_name}.exe',
    }
    
    if not ospath.exists(d := abs_paths['conf_dir']):
        os.mkdir(d)
    
    _rel0 = lambda p: global_dirs.relpath(p, root_dir)
    _rel1 = lambda p: global_dirs.relpath(p, proj_dir)
    rel_paths = {
        'lib_dir'    : _rel1(f'{root_dir}/lib'),
        'launch_file': _rel0(abs_paths['launch_file']),
        'target_dir' : _rel1(abs_paths['target_dir']),
        'conf_file'  : _rel1(abs_paths['conf_file']),
        'venv_dir'   : _rel0(f'{root_dir}/venv'),
        'venv_python': _rel0(f'{root_dir}/venv/python.exe')
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
                filesniff.get_filename(abs_paths['target_file'], suffix=False)
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
        _ext_paths = list(map(
            lambda d: global_dirs.relpath(
                global_dirs.to_dist(d) if not d.startswith(root_dir) else d,
                start=abs_paths['launch_dir']
            ),
            extend_sys_paths
        ))
        
        with ropen(global_dirs.template('pylauncher.txt')) as f:
            template = f.read()
            code = template.format(
                # see `template/pylauncher.txt > docs:placeholders`
                PROJ_LIB_DIR=rel_paths['lib_dir'],
                EXTEND_PATHS=str(_ext_paths),
                # DEFAULT_CONF='default.pkl',
            )
        
        with wopen(abs_paths['launch_file']) as f:
            f.write(code)
    
    def _generate_bat():
        with ropen(global_dirs.template('launch.bat')) as f:
            template = f.read()
            if kwargs.get('depsland_mode', False):  # FIXME
                code = template.format(
                    PYTHON='{PYTHON}',
                    PYLAUNCHER=rel_paths['launch_file'],
                    PYCONF='%*' if is_main_conf else rel_paths['conf_file']
                )
            elif enable_venv:
                code = template.format(
                    PYTHON=rel_paths['venv_python'].replace('/', '\\'),
                    PYLAUNCHER=rel_paths['launch_file'],
                    PYCONF='%*' if is_main_conf else rel_paths['conf_file']
                    #   '%*' supports passing multiple arguments to python. for
                    #   example:
                    #       example.bat:
                    #           python test.py %*
                    #       test.py
                    #           import sys
                    #           print(sys.argv)
                    #       cmd:
                    #           example.bat hello world 1 2 3
                    #       output:
                    #           ['test.py', 'hello', 'world', '1', '2', '3']
                )
            else:
                code = template.format(
                    PYTHON='python',
                    PYLAUNCHER=rel_paths['launch_file'],
                    PYCONF='%*' if is_main_conf else rel_paths['conf_file']
                )
        
        with wopen(abs_paths['bat_file']) as f:
            f.write(code)
    
    def _generate_exe():
        def _run(bat_file, exe_file, icon_file, *options):
            from .bat_2_exe import bat_2_exe
            lk.loga('converting bat to exe... '
                    'it may take several seconds ~ one minute...')
            bat_2_exe(bat_file, exe_file, icon_file, *options)
            lk.loga('convertion bat-to-exe done')
        
        # 这是一个耗时操作 (大约需要 10s), 我们把它放在子线程执行
        global thread
        thread = runnin_new_thread(
            _run,
            abs_paths['bat_file'], abs_paths['exe_file'], icon, '/x64',
            '' if enable_console else '/invisible'
        )
    
    _generate_target_conf()
    if generate_pylauncher:
        _generate_pylauncher()
    if generate_bat:
        _generate_bat()
        if generate_exe:
            _generate_exe()
    
    if generate_exe:
        return abs_paths['exe_file']
    else:
        return abs_paths['bat_file']


def _create_depsland_setup(root_dir, launcher_name, icon,
                           venv_name, venv_id, requirements, **misc):
    with ropen(global_dirs.template('setup_for_depsland.txt')) as f:
        template = f.read()
        
        code = template.format(
            LAUNCHER=launcher_name,
            VENV_NAME=venv_name,
            VENV_ID=venv_id,
            REQUIREMENTS=requirements,
            INVISIBLE='' if misc.get('enable_console', True) else '/invisible'
        )
    
    with wopen(f'{root_dir}/build/setup.py') as f:
        f.write(code)
    
    shutil.copyfile(
        global_dirs.template('launch_for_depsland.bat'),
        f'{root_dir}/setup.bat'
    )
    
    if icon:
        shutil.copyfile(icon, f'{root_dir}/build/launcher.ico')
