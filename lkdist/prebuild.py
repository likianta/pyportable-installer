import re
import os
import shutil
from os import path as ospath

from lk_logger import lk
from lk_utils import filesniff
from lk_utils.read_and_write import dumps, loads


class GlobalConf:
    # 对于一些修改较为频繁, 但用途很小的参数, 放在了这里. 您可以按需修改
    # 使用 Pycharm 的搜索功能查看它在哪里被用到
    create_checkup_tool = True  # True|False
    #   如果您在实现增量更新 (仅发布 src 文件夹), 请设为 False
    create_venv_shell = True
    #   如果您在实现增量更新 (仅发布 src 文件夹), 请设为 False
    create_launcher = True  # True|False


def full_build(file):
    GlobalConf.create_checkup_tool = True
    GlobalConf.create_venv_shell = True
    GlobalConf.create_launcher = True
    process_pyproject(file)


def min_build(file):
    GlobalConf.create_checkup_tool = False
    GlobalConf.create_venv_shell = False
    GlobalConf.create_launcher = False
    process_pyproject(file)


def process_pyproject(pyproj_file):
    """
    Args:
        pyproj_file: pyproject.json.
        
    References:
        docs/pyproject template.md
        lkdist/template/pyproject.json
    """
    
    def pretty_path(p):
        return p.replace('\\', '/')
    
    pyproj_dir = pretty_path(ospath.abspath(f'{pyproj_file}/../'))
    lk.loga(pyproj_dir)
    
    def abspath(p: str):
        if p == '': return ''
        if p[1] == ':': return pretty_path(p)  # FIXME: doesn't work in macOS
        return pretty_path(f'{pyproj_dir}/{p}')
    
    def relpath(p: str):
        if p == '': return ''
        if p[1] == ':': return pretty_path(ospath.relpath(p, pyproj_dir))
        return pretty_path(p)
    
    # --------------------------------------------------------------------------
    
    conf_i = loads(pyproj_file)
    conf_o = loads('template/pyproject.json')  # type: dict
    #   conf_o has the same struct with conf_i
    
    # check conf_i
    assert conf_i['app_version']
    if pyver := conf_i['required']['python_version']:
        assert pyver.isdecimal() and len(pyver.split('.')) == 2
    
    # assign conf_i to conf_o
    conf_o['app_name'] = conf_i['app_name']
    conf_o['app_version'] = conf_i['app_version']
    conf_o['icon'] = abspath(conf_i['icon'])
    conf_o['author'] = conf_i['author']
    
    conf_o['build']['idir'] = abspath(conf_i['build']['idir'])
    conf_o['build']['odir'] = abspath(conf_i['build']['odir'].format(
        app_name=conf_i['app_name'], app_version=conf_i['app_version']
    ))
    conf_o['build']['readme'] = abspath(conf_i['build']['readme'])
    conf_o['build']['module_paths'] = [
        relpath(p) for p in conf_i['build']['module_paths']
    ]
    conf_o['build']['attachments'] = {
        abspath(k): v for (k, v) in conf_i['build']['attachments'].items()
    }
    
    conf_o['build']['target'] = conf_i['build']['target']
    conf_o['build']['target']['file'] = relpath(
        conf_i['build']['target']['file']
    )
    
    conf_o['build']['required'] = conf_i['build']['required']
    conf_o['build']['required']['venv'] = abspath(
        conf_i['build']['target']['venv']
    )
    
    conf_o['note'] = conf_i['note']
    
    # run conf_o
    lk.logp(conf_o)
    _apply_config(conf_o['app_name'], **conf_o['build'], icon=conf_o['icon'])


def _apply_config(app_name, idir, odir, target, required,
                  readme='', module_paths=None, attachments=None, **kwargs):
    """
    
    Args:
        app_name (str)
        idir (str): 文件夹的绝对路径或相对路径. 路径分隔符使用正斜杠
        odir (str): 'output directory'. 建议填 '../dist/xxx' (xxx 为你要发布的项
            目的名字, 可以带上版本号. 例如 '../dist/ufs_testcases_0.1.0')
        target (dict)
        readme (str): str endswith '.md'. 读我文档, 请确保后缀是 .md (markdown
            格式的文件), 本程序会把它转换为 html 格式并放在 odir 目录下
        module_paths (list): see `_create_launcher()`
        attachments (dict): 其他要加入的目录
        required (dict)
        **kwargs:
            icon
    """
    # adjust args
    if module_paths is None: module_paths = []
    if attachments is None: attachments = {}
    
    # precheck
    _precheck_args(idir, odir, attachments, required['python_version'])
    
    # if output dirs not exist, create them
    rootdir, srcdir = odir, f'{odir}/src'
    #   'root directory', 'source code directory'
    filesniff.force_create_dirpath(srcdir)
    
    # --------------------------------------------------------------------------
    
    dirs_to_compile = []
    
    dirs_to_compile.extend(_copy_sources(idir, srcdir))
    
    dirs_to_compile.extend(_copy_assets(attachments, srcdir))
    
    if GlobalConf.create_checkup_tool:
        os.mkdir(f'{odir}/build')
        _copy_checkup_tool(f'{odir}/build')
    
    _create_launcher(
        app_name, kwargs.get('icon', 'template/python.ico'), target, rootdir,
        extend_sys_paths=module_paths,
        enable_venv=required['enable_venv']
    )
    
    if readme:
        _create_readme(readme, rootdir)
    
    for d in dirs_to_compile:
        _compile_py_files(d)
        _cleanup_py_files(d)
        #   you can comment this line to remain .py files for debugging purpose
    
    if required['enable_venv'] and GlobalConf.create_venv_shell:
        os.mkdir(f'{odir}/venv')
        _copy_venv(required['venv'], f'{rootdir}/venv',
                   required['python_version'],
                   include_tkinter=True)
        #   include_tkinter: 考虑到我们的 bootloader 有用到 tkinter 的 msgbox, 所
        #   以这里选用有 tkinter 模块的版本
    
    lk.logt("[I2501]", f'See distributed project at \n\t"{rootdir}:0"')


# ------------------------------------------------------------------------------

def _precheck_args(idir, odir, attachments, pyversion):
    assert ospath.exists(idir)
    
    if ospath.exists(odir) and os.listdir(odir):
        if input(
                '警告: 要打包的目录已存在!\n'
                '您是否确认清空目标目录以重构: "{}"\n'
                '请注意确认删除后内容无法恢复! (y/n): '.format(odir)
        ).lower() == 'y':
            shutil.rmtree(odir)
            os.mkdir(odir)
        else:
            raise FileExistsError
    
    assert all(map(ospath.exists, attachments.keys()))
    
    from checkup import check_pyversion
    curr_ver, result = check_pyversion(*map(int, pyversion.split('.')))
    assert result is True, \
        f'prebuild 使用的 Python 版本 ({curr_ver}) ' \
        f'不符合目标编译版本 ({pyversion})!'


def _copy_sources(idir, srcdir):
    """ 将 idir 的内容全部拷贝到 srcdir 下.
    
    Args:
        idir: see `main()`
        srcdir: 'source code dir'. 传入 `main:vars:srcdir`
    """
    yield from _copy_assets({idir: 'assets,compile'}, srcdir)
    # odir = f'{srcdir}/{ospath.basename(idir)}'
    # shutil.copytree(idir, odir)
    # return odir


def _copy_assets(attachments, srcdir):
    """
    Args:
        attachments (dict): {idir: type, ...}
            idir (str)
            type (str): 'assets'|'root_folder'|'root_assets'|'tree_folders'
                |'compile'|'assets,compile,...' (多个值组合时, 用逗号分隔)
        srcdir
    
    Yields:
        dirpath
    """
    
    def copy_tree_excludes_protected_folders(idir, odir):
        invalid_pattern = re.compile(r'/(\.|__?)\w+')
        #   e.g. '/.git', '/__pycache__'
        
        valid_dirs = []  # [(i, o), ...]
        for idir0 in idir:
            odir0 = f'{odir}/{ospath.basename(idir0)}'
            valid_dirs.append((idir0, odir0))
            
            # FIXME: 1.4.4 版本的 lk-utils.filesniff.findall_dirs 不完善, 无法完
            #   全地过滤掉需要被排除的文件, 所以我们自定义一个 invalid_pattern 来
            #   处理
            for idir1 in filesniff.findall_dirs(idir0):
                if invalid_pattern.search(idir1):
                    continue
                odir1 = f'{odir0}/{idir1.replace(idir0 + "/", "", 1)}'
                lk.logax(idir1, odir1)
                valid_dirs.append((idir1, odir1))
        lk.reset_count()
        
        for (i, o) in valid_dirs:
            filesniff.force_create_dirpath(o)
            for fp, fn in filesniff.find_files(i, fmt='zip'):
                ifp, ofp = fp, f'{o}/{fn}'
                shutil.copyfile(ifp, ofp)
        del valid_dirs
    
    for idir, type_ in attachments.items():
        dirname = ospath.basename(idir)
        odir = f'{srcdir}/{dirname}'
        
        ''' pyswitch
        from pyswitch import switch
        
        switch(lambda v: bool(v in type_), """
            case 'assets':
                pass
            case 'root_folder':
                pass
            ...
        """)
        '''
        
        if 'assets' in type_:
            if 'compile' in type_:
                copy_tree_excludes_protected_folders(idir, odir)
            else:
                shutil.copytree(idir, odir)
        elif 'root_folder' in type_:
            os.mkdir(odir)
        elif 'root_assets' in type_:
            for fp, fn in filesniff.find_files(idir, fmt='zip'):
                shutil.copyfile(fp, f'{odir}/{fn}')
            for dp, dn in filesniff.find_dirs(idir, fmt='zip'):
                os.mkdir(f'{odir}/{dn}')
        elif 'tree_folders' in type_:
            for dp, dn in filesniff.findall_dirs(idir, fmt='zip'):
                os.mkdir(dp.replace(idir, odir, 1))
        
        if 'compile' in type_:
            yield odir


def _copy_checkup_tool(buildir):
    # buildir: 'build (noun.) directory'
    shutil.copyfile('checkup.py', f'{buildir}/checkup.py')
    shutil.copyfile('pretty_print.py', f'{buildir}/pretty_print.py')


def _copy_venv(src_venv_dir, dst_venv_dir, pyversion, include_tkinter=False):
    """
    Args:
        src_venv_dir: 'source virtual environment directory'.
            tip: you can pass an empty to this argument, see reason at `Notes:3`
        dst_venv_dir: 'distributed virtual environment directory'
        pyversion: e.g. '3.8'. 请确保该版本与 lkdist 所用的 Python 编译器, 以及
            src_venv_dir 所用的 Python 版本一致 (修订号可以不一样), 否则
            _compile_py_files 编译出来的 .pyc 文件无法运行!
        include_tkinter: 默认的 embed python 安装包是不带 tkinter 模块的, 如果需
            要, 则会使用一个修改过的 embed python 安装包 (修改只涉及复制了 tkinter
            相关的模块到原生 embed python 安装目录内)
    
    Notes:
        1. 本函数使用了 embed_python 独立安装包的内容, 而非简单地把 src_venv_dir
           拷贝到打包目录, 这是因为 src_venv_dir 里面的 Python 是不可独立使用的.
           也就是说, 在一个没有安装过 Python 的用户电脑上, 调用 src_venv_dir 下的
           Python 编译器将失败! 所以我们需要的是一个嵌入版的 Python (在 Python 官
           网下载带有 "embed" 字样的压缩包, 并解压, 我在 lkdist 项目下已经准备了一
           份)
        2. 出于性能和成本考虑, 您不必提供有效 src_venv_dir 参数, 即您可以给该参数
           传入一个空字符串, 这样本函数会仅创建虚拟环境的框架 (dst_venv_dir), 并让
           '{dst_venv_dir}/site-packages' 留空. 稍后您可以手动地复制, 或剪切所需
           的依赖到 '{dst_venv_dir}/site-packages'
           
    Results:
        copy source dir to target dir:
            lib/python-{version}-embed-amd64 -> {dst_venv_dir}
            {src_venv_dir}/Lib/site-packages -> {dst_venv_dir}/site-packages
    """
    # create venv shell
    embed_python_dir0 = '../python_embed/tkinter_edition' \
        if include_tkinter else '../python_embed'
    embed_python_dir = {
        # note: 我只准备了 amd64 版的 embed python, 如果您要生成 32 位的, 请手动
        # 修改这里! (暂不支持通过 pyproject.json 修改)
        '3.8': f'{embed_python_dir0}/python-3.8.5-embed-amd64',
        '3.9': f'{embed_python_dir0}/python-3.9.0-embed-amd64'
    }[pyversion]
    
    shutil.copytree(embed_python_dir, dst_venv_dir)
    
    # copy site-packages
    if ospath.exists(src_venv_dir):
        shutil.copytree(f'{src_venv_dir}/Lib/site-packages',
                        f'{dst_venv_dir}/site-packages')
    else:  # just create an empty folder
        os.mkdir(f'{dst_venv_dir}/site-packages')


def _create_launcher(app_name, icon, target, rootdir,
                     extend_sys_paths=None, enable_venv=True):
    """ 创建启动器.
    
    Args:
        app_name (str)
        icon (str)
        target (dict): {
            'file': filepath,
            'function': str,
            'args': [...],
            'kwargs': {...}
        }
        rootdir (str): 打包的根目录
        extend_sys_paths (list):. 模块搜索路径, 该路径会被添加到 sys.path.
            列表中的元素是相对于 srcdir 的文件夹路径 (必须是相对路径格式. 参考
            `process_pyproject:conf_o['build']['module_paths']`)
        enable_venv (bool): 推荐为 True
    
    详细说明:
        启动器分为两部分, 一个是启动器图标, 一个引导装载程序.
        启动器图标位于: '{rootdir}/{app_name}.exe'
        引导装载程序位于: '{rootdir}/src/bootloader.pyc'
        
        1. 二者的体积都非常小
        2. 启动器本质上是一个带有自定义图标的 bat 脚本. 它指定了 Python 编译器的路
           径和 bootloader 的路径, 通过调用编译器执行 bootloader.pyc
        3. bootloader 主要完成了以下两项工作:
            1. 向 sys.path 中添加当前工作目录和自定义的模块目录
            2. 对主脚本加了一个 try catch 结构, 以便于捕捉主程序报错时的信息, 并以
               tkinter 弹窗的形式给用户. 这样就摆脱了控制台打印的需要, 使我们的软
               件表现得更像是一款软件
    
    Notes:
        1. 启动器在调用主脚本 (main:args:main_script) 之前, 会通过 `os.chdir` 切
           换到主脚本所在的目录, 这样我们项目源代码中的所有相对路径, 相对引用都能正
           常工作
    
    References:
        template/launch_by_system.bat
        template/launch_by_venv.bat
        template/bootloader.txt
    """
    launcher_name = app_name
    bootloader_name = 'bootloader'
    
    target_path = target['file']  # type: str
    target_pkg = target_path.rsplit('/', 1)[0].replace('/', '.')
    target_name = filesniff.get_filename(target_path, suffix=False)
    
    template = loads('template/bootloader.txt')
    code = template.format(
        # see `template/bootloader.txt:Template placeholders`
        SITE_PACKAGES='../venv/site-packages' if enable_venv else '',
        EXTEND_SYS_PATHS=str(extend_sys_paths),
        TARGET_PATH=target_path,
        TARGET_PKG=target_pkg,
        TARGET_NAME=target_name,
        TARGET_FUNC=target['function'],
        TARGET_ARGS=str(target['args']),
        TARGET_KWARGS=str(target['kwargs']),
    )
    dumps(code, f'{rootdir}/src/{bootloader_name}.py')
    
    # --------------------------------------------------------------------------
    
    if not GlobalConf.create_launcher:
        return
    
    if enable_venv:  # suggest
        template = loads('template/launch_by_venv.bat')
    else:
        # 注意: 这个不太安全, 因为我们不能确定用户系统安装默认的 Python 版本是否与
        # 当前编译的 pyc 版本相同.
        template = loads('template/launch_by_system.bat')
    code = template.format(
        LAUNCHER=f'{bootloader_name}.pyc'
        #   注意是 '{boot_name}.pyc' 而不是 '{boot_name}.cpython-38.pyc', 原因见
        #   `_compile_py_files:vars:ofp`
    )
    bat_file = f'{rootdir}/{launcher_name}.bat'
    dumps(code, bat_file)
    
    from lkdist.bat_2_exe import bat_2_exe
    bat_2_exe(bat_file, f'{rootdir}/{app_name}.exe',
              icon, '/x64', '/invisible')
    os.remove(bat_file)


def _create_readme(ifile: str, distdir):
    ofile = f'{distdir}/{ospath.basename(ifile)}'
    shutil.copyfile(ifile, ofile)


def _compile_py_files(idir):
    """
    References:
        https://blog.csdn.net/weixin_38314865/article/details/90443135
    """
    from compileall import compile_dir
    compile_dir(idir)
    
    for fp, fn in filesniff.findall_files(idir, suffix='.pyc', fmt='zip'):
        #   fp: 'filepath', fn: 'filename', e.g. 'xxx.cpython-38.pyc'
        ifp = fp
        ofp = f'{fp}/../../{fn.split(".", 1)[0]}.pyc'
        #   1. 第一个 '../' 表示自身所在的目录, 第二个 '../' 指向上一级目录
        #   2. 不能直接使用 fn, 因为 fn 的后缀是 '.cpython-38.pyc', 会导致 Python
        #      的导入语法不能正常工作 (提示 "ImportError: No module named
        #      'model'"), 为了解决此问题, 将后缀改为 '.pyc' 即可.
        shutil.move(ifp, ofp)


def _cleanup_py_files(idir):
    # delete __pycache__ folders (the folders are empty)
    for dp in filesniff.findall_dirs(  # dp: 'dirpath'
            idir, suffix='__pycache__',
            exclude_protected_folders=False
    ):
        os.rmdir(dp)
    
    # and delete .py files
    for fp in filesniff.findall_files(idir, suffix='.py'):
        os.remove(fp)
