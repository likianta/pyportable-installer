from lk_utils.read_and_write import dumps, loads

from .assets_copy import *
from .compiler import get_compiler
from .typehint import *
from .utils import runnin_new_thread
from .venv_builder import main as handle_venv

thread = None


def main(
        app_name: str,
        proj_dir: TPath, dist_dir: TPath,
        target: TTarget,
        venv: TConfBuildVenv,
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
        app_name: Use normal case. e.g. 'Hello World'
        proj_dir: See `Project Structure Example`
        dist_dir: See `Project Structure Example`. Note this directory is
            equivalent to `global_dirs.py::global_vars:global_dirs::attrs
            :dst_root`, this is the parent dir of that.
        target: See `docs/pyproject-template.md::build:target`
        module_paths: See `func:_create_launcher`
        attachments: See `assets_copy.py::copy_assets::docstring:attachments`
        venv: See `docs/pyproject-template.md::build:venv`
        compiler: Literal['pyarmor', 'pyc', 'pycrypto']. Compiler name.
        **misc: Some keys are from `main.py::main::conf['build']` (e.g.
            'readme', 'icon', 'enable_console'), the others are from `main.py
            ::class:Misc.dump`
    
    Warnings:
        请勿随意更改本函数的参数名, 这些名字与 `template/pyproject.json` 的诸多
        键名有关系, 二者名字需要保持一致.
    """
    # init args
    readme_file = misc.get('readme', '')
    
    # precheck
    _precheck(proj_dir, dist_dir, readme_file, attachments)
    
    # see `docs/devnote/dist-folders-structure.md`
    # these dirs already exist, see creation at `no2_prebuild_pyproject.py::cmt
    # :'create build_dir, lib_dir, src_dir'`
    root_dir, build_dir, src_dir, lib_dir = (
        dist_dir, f'{dist_dir}/build', f'{dist_dir}/src', f'{dist_dir}/lib'
    )
    #   root_dir : 'root directory'
    #   build_dir: 'build (noun.) directory'
    #   src_dir  : 'source directory'. note: this is equivalent to
    #       `global_dirs.py::global_vars:global_dirs::attrs:dst_root`
    
    # --------------------------------------------------------------------------
    
    # build_dir
    if misc.get('create_checkup_tools', True):
        copy_checkup_tool(global_dirs.local('checkup'), build_dir)
    
    # readme_file
    if readme_file:
        create_readme(readme_file, f'{root_dir}/{ospath.basename(readme_file)}')
    
    # venv
    venv_builder = handle_venv(
        venv, root_dir,
        create_venv_shell=misc.get('create_venv_shell', True)
    )
    
    # --------------------------------------------------------------------------
    # compile
    
    # get a compiler
    pyversion = venv['python_version']
    if venv['enable_venv']:
        pyinterpreter = venv_builder.get_embed_python_interpreter(pyversion)
    else:
        pyinterpreter = 'python'  # default python in system environment
    from .utils import set_pyinterpreter
    set_pyinterpreter(pyinterpreter)
    
    compiler = get_compiler(
        compiler['name'], pyinterpreter,
        lib_dir=lib_dir, pyversion=pyversion
    )
    
    pyfiles_to_compile = []
    pyfiles_to_compile.extend(copy_sources(proj_dir))
    pyfiles_to_compile.extend(copy_assets(attachments))
    
    # noinspection PyUnusedLocal
    launch_file = _create_launcher(
        app_name, misc.get('icon', ''), target, root_dir,
        pyversion=pyversion,
        extend_sys_paths=module_paths,
        enable_venv=venv['enable_venv'],
        enable_console=misc.get('enable_console', True),
        create_launch_bat=misc.get('create_launch_bat', True),
    )
    # pyfiles_to_compile.append(launch_file)
    
    if misc.get('compile_scripts', True):
        compiler.compile_all(pyfiles_to_compile)
    else:
        for src_file, dst_file in zip(
                pyfiles_to_compile,
                map(global_dirs.to_dist, pyfiles_to_compile)
        ):
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


def _create_launcher(app_name, icon, target, root_dir, pyversion,
                     extend_sys_paths=None, enable_venv=True,
                     enable_console=True, create_launch_bat=True):
    """ Create launcher ({srcdir}/bootloader.py).

    Args:
        app_name (str): application name, this will be used as exe file's name:
            e.g. ``app_name = 'Hello World'`` -> will generate 'Hello World.exe'
        icon (str): *.ico file
        target (dict): {
            'file': filepath,
            'function': str,
            'args': [...],
            'kwargs': {...}
        }
        root_dir (str):
        pyversion (str): e.g. '3.8'
        extend_sys_paths (list[str]): 模块搜索路径, 该路径会被添加到 sys.path.
            列表中的元素是相对于 src_dir 的文件夹路径 (必须是相对路径格式. 参考
            `process_pyproject:conf_o['build']['module_paths']`)
        enable_venv (bool):
        enable_console (bool):
        create_launch_bat (bool):
    
    详细说明
        启动器分为两部分, 一个是启动器图标, 一个引导装载程序.
        启动器图标位于: '{root_dir}/{app_name}.exe'
        引导装载程序位于: '{root_dir}/src/bootloader.pyc'
    
        1. 二者的体积都非常小
        2. 启动器本质上是一个带有自定义图标的 bat 脚本. 它指定了 Python 编译器的
           路径和 bootloader 的路径, 通过调用编译器执行 bootloader.pyc
        3. bootloader 主要完成了以下两项工作:
            1. 向 sys.path 中添加当前工作目录和自定义的模块目录
            2. 对主脚本加了一个 try catch 结构, 以便于捕捉主程序报错时的信息, 并
               以系统弹窗的形式给用户. 这样就摆脱了控制台打印的需要, 使我们的软
               件表现得更像是一款软件

    Notes
        1. 启动器在调用主脚本 (``main:args:main_script``) 之前, 会通过
           ``os.chdir`` 切换到主脚本所在的目录, 这样我们项目源代码中的所有相对路
           径, 相对引用都能正常工作

    References
        - template/launch_by_system.bat
        - template/launch_by_venv.bat
        - template/bootloader.txt
    
    Returns:
        launch_file: ``{root_dir}/src/{bootloader_name}.py``.

    """
    launcher_name = app_name
    bootloader_name = 'bootloader'
    
    target_path = target['file']  # type: str
    target_dir = global_dirs.to_dist(ospath.dirname(target_path))
    launch_dir = ospath.dirname(target_dir)
    #   the launcher dir is parent of target dir, i.e. we put the launcher file
    #   in the parent folder of target file's folder.
    
    # target_reldir: 'target relative directory' (starts from `launch_dir`)
    # PS: it is equivalent to f'{target_dir_name}/{target_file_name}'
    target_reldir = global_dirs.relpath(target_dir, launch_dir)
    target_pkg = target_reldir.replace('/', '.')
    target_name = filesniff.get_filename(target_path, suffix=False)
    
    extend_sys_paths = list(map(
        lambda d: global_dirs.relpath(
            global_dirs.to_dist(d) if not d.startswith('dist:')
            else d.replace('dist:', f'{root_dir}/').rstrip('/'),
            launch_dir
        ),
        extend_sys_paths
    ))
    
    template = loads(global_dirs.template('bootloader.txt'))
    code = template.format(
        # see `template/bootloader.txt > docstring:placeholders`
        LIB_RELDIR=global_dirs.relpath(f'{root_dir}/lib', launch_dir),
        SITE_PACKAGES='../venv/site-packages' if enable_venv else '',
        EXTEND_SYS_PATHS=str(extend_sys_paths),
        TARGET_RELDIR=target_reldir,
        TARGET_PKG=target_pkg,
        TARGET_NAME=target_name,
        TARGET_FUNC=target['function'],
        TARGET_ARGS=str(target['args']),
        TARGET_KWARGS=str(target['kwargs']),
    )
    dumps(code, launch_file := f'{launch_dir}/{bootloader_name}.py')
    
    # --------------------------------------------------------------------------
    
    # template = loads(global_dirs.template('pytransform.txt'))
    # code = template.format(
    #     LIB_PARENT_RELDIR='../'
    # )
    # dumps(code, f'{root_dir}/src/pytransform.py')
    
    # --------------------------------------------------------------------------
    
    if create_launch_bat is False:
        return launch_file
    
    if enable_venv:  # suggest
        template = loads(global_dirs.template('launch_by_venv.bat'))
    else:
        template = loads(global_dirs.template('launch_by_system.bat'))
    code = template.format(
        PYVERSION=pyversion.replace('.', ''),  # ...|'37'|'38'|'39'|...
        VENV_RELDIR=global_dirs.relpath(f'{root_dir}/venv', launch_dir)
            .replace('/', '\\'),
        LAUNCHER_RELDIR=global_dirs.relpath(launch_dir, root_dir)
            .replace('/', '\\'),
        LAUNCHER_NAME=f'{bootloader_name}.py',
    )
    bat_file = f'{root_dir}/{launcher_name}.bat'
    # lk.logt('[D3432]', code)
    dumps(code, bat_file)
    
    # 这是一个耗时操作 (大约需要 10s), 我们把它放在子线程执行
    def generate_exe(bat_file, exe_file, icon_file, *options):
        from .bat_2_exe import bat_2_exe
        lk.loga('converting bat to exe... '
                'it may take several seconds ~ one minute...')
        bat_2_exe(bat_file, exe_file, icon_file, *options)
        lk.loga('convertion bat-to-exe done')
    
    global thread
    thread = runnin_new_thread(
        generate_exe,
        bat_file, f'{root_dir}/{launcher_name}.exe', icon, '/x64',
        '' if enable_console else '/invisible'
    )
    
    return launch_file
