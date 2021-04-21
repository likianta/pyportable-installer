from threading import Thread

from lk_utils.read_and_write import dumps, loads

from .aftermath import main as aftermath
from .assets_copy import *
from .compiler import compile1

curr_dir = ospath.dirname(__file__).replace('\\', '/')


class GlobalConf:
    # 对于一些修改较为频繁, 但用途很小的参数, 放在了这里. 您可以按需修改
    # 使用 Pycharm 的搜索功能查看它在哪里被用到
    create_checkup_tools = True  # True|False
    #   如果您在实现增量更新 (仅发布 src 文件夹), 请设为 False
    create_venv_shell = True
    #   如果您在实现增量更新 (仅发布 src 文件夹), 请设为 False
    create_launch_bat = True  # True|False


def full_build(file):
    GlobalConf.create_checkup_tools = True
    GlobalConf.create_venv_shell = True
    GlobalConf.create_launch_bat = True
    main(file)


def min_build(file):
    GlobalConf.create_checkup_tools = False
    GlobalConf.create_venv_shell = False
    GlobalConf.create_launch_bat = True  # True(suggest)|False
    main(file)


def main(file):
    conf_o = extract_pyproject(file)
    root_dir = build_pyproject(app_name=conf_o['app_name'], **conf_o['build'])
    
    m, n = ospath.split(root_dir)
    lk.logt("[I2501]", f'See distributed project at \n\t"{m}:0" >> {n}')
    
    dumps(conf_o, f'{root_dir}/build/manifest.json')
    aftermath(root_dir)


def extract_pyproject(pyproj_file):
    """
    Args:
        pyproj_file: pyproject.json.
        
    References:
        docs/pyproject template.md
        pyportable_installer/template/pyproject.json
    """
    
    def pretty_path(p):
        return p.replace('\\', '/')
    
    def abspath(p: str):
        if p == '': return ''
        if p[1] == ':': return pretty_path(p)  # FIXME: doesn't work in macOS
        return pretty_path(ospath.abspath(f'{pyproj_dir}/{p}'))
    
    def relpath(p: str, start):
        # 注意: pyproj_dir 与 start 可能是不同的. 在 conf_i 中, 所有相对路径均是
        # 指相对于 pyproj_dir 的, 而在本函数中, 相对路径的计算是相对于
        # conf_i['build']['proj_dir'] 的父目录而言 (该目录相当于
        # `build_pyproject:vars:src_dir`)
        # 当 pyproject.json 位于要打包的项目源代码的父目录时, pyproj_dir 与
        # start 相同 (这是推荐的放置位置); 如果 pyproject.json 放置不当, 比如放
        # 在了其他目录, 那么就会不同.
        if p == '': return ''
        if p[1] == ':': return pretty_path(ospath.relpath(p, start))
        return pretty_path(ospath.relpath(abspath(p), start))
    
    pyproj_dir = pretty_path(ospath.abspath(f'{pyproj_file}/../'))
    lk.loga(pyproj_dir)
    
    # --------------------------------------------------------------------------
    
    conf_i = loads(pyproj_file)
    conf_o = loads(f'{curr_dir}/template/pyproject.json')  # type: dict
    #   conf_o has the same struct with conf_i
    
    # check conf_i
    assert conf_i['app_version']
    
    # pyver: 'python version'
    if pyver := conf_i['build']['required']['python_version']:
        assert pyver.replace('.', '').isdigit() and len(pyver.split('.')) == 2
    
    proj_dir = abspath(conf_i['build']['proj_dir'])
    proj_dir_parent = ospath.dirname(proj_dir)
    #   该值相当于 `funcs:build_pyproject:vars:src_dir`
    # # del proj_dir
    
    # --------------------------------------------------------------------------
    
    # conf_o.update(conf_i)
    conf_o['app_name'] = conf_i['app_name']
    conf_o['app_version'] = conf_i['app_version']
    conf_o['description'] = conf_i['description']
    conf_o['author'] = conf_i['author']
    
    conf_o['build']['proj_dir'] = abspath(conf_i['build']['proj_dir'])
    conf_o['build']['dist_dir'] = abspath(conf_i['build']['dist_dir'].format(
        app_name=conf_i['app_name'],
        app_name_lower=conf_i['app_name'].lower().replace(' ', '_'),
        app_version=conf_i['app_version']
    ))
    conf_o['build']['icon'] = abspath(
        conf_i['build']['icon'] or
        ospath.abspath(f'{curr_dir}/template/python.ico')
    )
    conf_o['build']['readme'] = abspath(
        conf_i['build']['readme']
    )
    conf_o['build']['module_paths'] = [
        relpath(p, proj_dir_parent)
        for p in conf_i['build']['module_paths']
    ]
    conf_o['build']['attachments'] = {
        abspath(k): v
        for (k, v) in conf_i['build']['attachments'].items()
    }
    conf_o['build']['enable_console'] = conf_i['build']['enable_console']
    
    conf_o['build']['target'] = conf_i['build']['target']
    conf_o['build']['target']['file'] = relpath(
        conf_i['build']['target']['file'].format(
            dist_dir=conf_o['build']['dist_dir']
        ),
        proj_dir_parent
    )
    
    conf_o['build']['required'] = conf_i['build']['required']
    conf_o['build']['required']['venv'] = abspath(
        conf_i['build']['required']['venv']
    )
    
    conf_o['note'] = conf_i['note']
    
    return conf_o


def build_pyproject(
        app_name, proj_dir, dist_dir, target, required,
        module_paths=None, attachments=None, **misc
):
    """
    
    Args:
        app_name (str)
        proj_dir (str): abspath of dir
        dist_dir (str): abspath of dir
        target (dict)
        module_paths (list): see `_create_launcher()`
        attachments (dict): 附件和资产
        required (dict)
        **misc:
            readme: abspath *.md|*.html|*.pdf|...
            icon: abspath *.icon
            enable_console: bool
    """
    # adjust args
    if module_paths is None: module_paths = []
    if attachments is None: attachments = {}
    readme = misc.get('readme', '')
    
    # precheck
    _precheck_args(proj_dir, dist_dir, readme, attachments)
    
    # if output dirs not exist, create them
    root_dir, build_dir, src_dir, cache_dir = (
        dist_dir, f'{dist_dir}/build', f'{dist_dir}/src', f'{dist_dir}/cache'
    )
    #   root_dir : 'root directory'
    #   src_dir  : 'source code directory'
    #   build_dir: 'build (noun.) directory'
    filesniff.force_create_dirpath(build_dir)
    filesniff.force_create_dirpath(src_dir)
    filesniff.force_create_dirpath(cache_dir)
    
    # --------------------------------------------------------------------------
    
    if GlobalConf.create_checkup_tools:
        copy_checkup_tool(f'{curr_dir}/checkup', build_dir)
    
    if readme:
        create_readme(readme, root_dir)
    
    dirs_to_compile = []
    dirs_to_compile.extend(copy_sources(proj_dir, src_dir))
    dirs_to_compile.extend(copy_assets(attachments, src_dir))
    
    launch_file = _create_launcher(
        app_name, misc.get('icon'), target, root_dir,
        pyversion=required['python_version'],
        extend_sys_paths=module_paths,
        enable_venv=required['enable_venv'],
        enable_console=misc.get('enable_console', True),
    )
    dirs_to_compile.append(ospath.dirname(launch_file))
    
    # compile source code
    for i, d in enumerate(dirs_to_compile):
        files1 = filesniff.find_files(d, '.py')
        names1 = filesniff.find_filenames(d, '.py')
        if not files1:
            continue
        else:
            assert len(files1) == len(names1)
            os.mkdir(f'{cache_dir}/{i}')
        files2 = [f'{cache_dir}/{i}/{n}' for n in names1]
        [shutil.move(f1, f2) for f1, f2 in zip(files1, files2)]
        compile1(files2, d)
    
    copy_runtime(f'{curr_dir}/template', src_dir)
    
    if required['enable_venv'] and GlobalConf.create_venv_shell:
        copy_venv(
            required['venv'], f'{root_dir}/venv', required['python_version'],
            embed_python_dir=ospath.dirname(f'{curr_dir}/../embed_python')
        )
    
    return root_dir


# ------------------------------------------------------------------------------

def _precheck_args(proj_dir, dist_dir, readme, attachments):
    assert ospath.exists(proj_dir)
    
    if ospath.exists(dist_dir):
        if os.listdir(dist_dir):
            if input(
                    '警告: 要打包的目录已存在!\n'
                    '您是否确认清空目标目录以重构: "{}"\n'
                    '请注意确认删除后内容无法恢复! (y/n): '.format(dist_dir)
            ).lower() == 'y':
                shutil.rmtree(dist_dir)
            else:
                raise FileExistsError
    
    assert readme == '' or ospath.exists(readme)
    
    assert all(map(ospath.exists, attachments.keys()))


def _create_launcher(app_name, icon, target, root_dir, pyversion,
                     extend_sys_paths=None, enable_venv=True,
                     enable_console=True):
    """ Create launcher ({srcdir}/bootloader.py).
    
    :param str app_name: application name, this will be used as exe file's name:
        e.g. ``app_name = 'Hello World'`` -> will generate 'Hello World.exe'
    :param str icon: *.ico file
    :param dict target: {
            'file': filepath,
            'function': str,
            'args': [...],
            'kwargs': {...}
        }
    :param str root_dir:
    :param str pyversion: e.g. '3.8'
    :param list[str] extend_sys_paths: 模块搜索路径, 该路径会被添加到 sys.path.
            列表中的元素是相对于 src_dir 的文件夹路径 (必须是相对路径格式. 参考
            `process_pyproject:conf_o['build']['module_paths']`)
    :param bool enable_venv:
    :param bool enable_console:
    :return:
        launch_file: ``{root_dir}/src/{bootloader_name}.py``.
    
    详细说明
    ========

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
    =====
    
    1. 启动器在调用主脚本 (``main:args:main_script``) 之前, 会通过 ``os.chdir``
       切换到主脚本所在的目录, 这样我们项目源代码中的所有相对路径, 相对引用都能
       正常工作
    
    References
    ==========
    
    - template/launch_by_system.bat
    - template/launch_by_venv.bat
    - template/bootloader.txt
    """
    launcher_name = app_name
    bootloader_name = 'bootloader'
    
    target_path = target['file']  # type: str
    target_dir = target_path.rsplit('/', 1)[0]
    target_pkg = target_dir.replace('/', '.')
    target_name = filesniff.get_filename(target_path, suffix=False)
    
    template = loads(f'{curr_dir}/template/bootloader.txt')
    code = template.format(
        # see `template/bootloader.txt:Template placeholders`
        SITE_PACKAGES='../venv/site-packages' if enable_venv else '',
        EXTEND_SYS_PATHS=str(extend_sys_paths),
        TARGET_PATH=target_path,
        TARGET_DIR=target_dir,
        TARGET_PKG=target_pkg,
        TARGET_NAME=target_name,
        TARGET_FUNC=target['function'] or '_',  # if no function name defined,
        #   use underline instead
        TARGET_ARGS=str(target['args']),
        TARGET_KWARGS=str(target['kwargs']),
    )
    dumps(code, launch_file := f'{root_dir}/src/{bootloader_name}.py')
    
    # --------------------------------------------------------------------------
    
    if not GlobalConf.create_launch_bat:
        return launch_file
    
    if enable_venv:  # suggest
        template = loads(f'{curr_dir}/template/launch_by_venv.bat')
    else:
        template = loads(f'{curr_dir}/template/launch_by_system.bat')
    code = template.format(
        PYVERSION=pyversion.replace('.', ''),  # ...|'37'|'38'|'39'|...
        LAUNCHER=f'{bootloader_name}.py'
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
        # os.remove(bat_file)
    
    thread = Thread(
        target=generate_exe,
        args=(bat_file, f'{root_dir}/{launcher_name}.exe', icon,
              '/x64', '' if enable_console else '/invisible')
    )
    thread.start()
    
    return launch_file
