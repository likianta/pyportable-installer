import os
import shutil
from os import path as ospath

from lk_logger import lk
from lk_utils import filesniff
from lk_utils.read_and_write import dumps, loads


class GlobalConf:
    # 对于一些修改较为频繁, 但用途很小的参数, 放在了这里. 您可以按需修改
    # 使用 Pycharm 的搜索功能查看它在哪里被用到
    proj_required_python_version = '3.8'
    app_version_to_suffix = True  # True|False
    create_checkup_tool = True  # True|False
    #   如果您在实现增量更新 (仅发布 src 文件夹), 请设为 False
    create_launch_bat = True  # True|False
    create_venv_shell = True
    #   如果您在实现增量更新 (仅发布 src 文件夹), 请设为 False


def full_build(file):
    GlobalConf.app_version_to_suffix = True
    GlobalConf.create_checkup_tool = True
    GlobalConf.create_launch_bat = True
    main_from_pyproject(file)


def min_build(file):
    GlobalConf.app_version_to_suffix = True
    GlobalConf.create_checkup_tool = False
    GlobalConf.create_venv_shell = False
    GlobalConf.create_launch_bat = False
    main_from_pyproject(file)


def main_from_pyproject(file):
    """
    Args:
        file: see 'template/pyproject.json'
    """
    from copy import deepcopy
    
    def pretty_path(p):
        return p.replace('\\', '/')
    
    def formatify_path(p: str):
        if p == '':  # empty
            return ''
        elif p[1] == ':':  # absolute path
            return pretty_path(p)
        else:  # relative path
            return pretty_path(f'{adir}/{p}')
    
    adir = pretty_path(ospath.abspath(f'{file}/../'))
    lk.loga(adir)
    
    ikwargs = loads(file)
    if GlobalConf.app_version_to_suffix:
        ikwargs['odir'] += '_' + ikwargs['manifest']['app_version']
    okwargs = deepcopy(ikwargs)  # type: dict
    if 'note' in okwargs: okwargs.pop('note')
    
    # --------------------------------------------------------------------------
    
    # 1/2
    node = []
    for p in ikwargs['idirs']:
        node.append(formatify_path(p))
    okwargs['idirs'] = node
    
    # 2/2
    okwargs['odir'] = formatify_path(okwargs['odir'])
    okwargs['readme'] = formatify_path(okwargs['readme'])
    # noinspection PyTypeChecker
    okwargs['manifest']['venv'] = formatify_path(okwargs['manifest']['venv'])
    
    lk.logp(okwargs)
    main(**okwargs)


def main(idir, odir, main_script,
         readme='', extra_sys_paths=None, extra_idirs=None,
         manifest=None):
    """
    
    Args:
        idir: 文件夹的绝对路径或相对路径. 路径分隔符使用正斜杠
        odir (str): 'output directory'. 建议填 '../dist/xxx' (xxx 为你要发布的项
            目的名字, 可以带上版本号. 例如 '../dist/ufs_testcases_0.1.0')
        main_script (str): 主脚本的路径
            要求:
                1. 必须是相对路径. 相对于 f'{odir}/src' 的路径
                2. 该脚本的启动函数必须是 `main` (即 `def main(): ...`)
            示例:
                假设有项目:
                    myproj
                    |- src
                        |- main.py
                    |- pyproject.json
                则 main_script 的相对路径为 'src/main.py' (相对于 'pyproject
                .json' 所在的目录)
        readme (str): str endswith '.md'. 读我文档, 请确保后缀是 .md (markdown
            格式的文件), 本程序会把它转换为 html 格式并放在 odir 目录下
        extra_sys_paths: see `_create_launcher()`
        extra_idirs (dict): 其他要加入的目录
        manifest (dict): see `_save_build_info()`
    """
    # adjust args
    if extra_sys_paths is None: extra_sys_paths = ()
    if extra_idirs is None: extra_idirs = {}
    if manifest is None: manifest = {}
    idirs = (idir, *extra_idirs)
    
    # precheck
    _precheck_args(idirs, manifest)
    
    # gen dirs
    rootdir, srcdir, buildir = odir, f'{odir}/src', f'{odir}/build'
    #   'root directory', 'source code directory', and 'build (noun.) directory'
    filesniff.force_create_dirpath(buildir)
    filesniff.force_create_dirpath(srcdir)
    
    module_path, module_name = main_script[:-3].replace('/', '.').rsplit('.', 1)
    #   main_script: 'xxx/yyy/zzz.py' -> 'xxx/yyy/zzz' -> 'xxx.yyy.zzz'
    #   -> ('xxx.yyy', 'zzz') -> module_path: 'xxx.yyy', module_name: 'zzz'
    
    # --------------------------------------------------------------------------
    
    # copy 1/2
    _copy_sources(idirs, srcdir)
    
    # create 1/3
    if GlobalConf.create_checkup_tool:
        _copy_checkup_tool(buildir)
    # create 2/3
    _create_launcher(
        target_path=module_path,
        target_name=module_name,
        rootdir=rootdir,
        extra_sys_paths=extra_sys_paths,
        enable_venv=manifest['enable_venv']
    )
    # create 3/3
    _create_readme(readme, rootdir)
    
    # compile 1/1
    _compile_py_files(odir)
    _cleanup_py_files(odir)
    # ↑ You can comment this line to remain .py files for debugging
    
    # copy 2/2: 注意这一步必须放在 `_compile_py_files` 步骤之后
    if manifest['enable_venv'] and GlobalConf.create_venv_shell:
        _copy_venv(manifest['venv'], f'{rootdir}/venv')
    
    # save 1/1
    _save_build_info(buildir, manifest or {})
    
    lk.logt("[I2501]", f'See distributed project at \n\t"{rootdir}:0"')


# ------------------------------------------------------------------------------

def _precheck_args(idirs, manifest):
    assert all(map(ospath.exists, idirs))
    assert manifest['app_name'] and manifest['app_version']
    
    from checkup import check_pyversion
    curr_ver, result = check_pyversion(*map(
        int,
        (target_ver := GlobalConf.proj_required_python_version).split('.')
    ))
    assert result is True, \
        f'prebuild 使用的 Python 版本 ({curr_ver}) ' \
        f'不符合目标编译版本 ({target_ver})!'
    #   如遇到此报错, 请切换 pyinstaller_for_intranet 项目的 Python 版本至
    #   target_ver. 示意图: 'docs/如何切换pycharm编译器版本.png'


def _copy_sources(idirs, srcdir, force_rebuild=False):
    """ 将选择的 idirs 全部拷贝到 odir.
    
    Args:
        idirs: see `main()`
        srcdir: 'source code dir'. 传入 f'{odir}/src' <- x: `main:args:odir`
        force_rebuild:
            True: 删除 odir 中已存在的内容, 再创建 odir 空文件夹
    """
    if force_rebuild and os.listdir(srcdir):
        # 预先清空 '~/build/sources' 中的全部内容
        if input('您确认删除文件夹 "{}" 吗? 请注意确认删除后内容无法恢复! '
                 '(y/n): '.format(srcdir)) == 'y':
            shutil.rmtree(srcdir)
            os.mkdir(srcdir)
    
    # --------------------------------------------------------------------------
    
    import re
    pattern = re.compile(r'/(\.|__?)\w+')
    
    valid_dirs = []
    for idir0 in idirs:
        odir0 = f'{srcdir}/{ospath.basename(idir0)}'
        valid_dirs.append((idir0, odir0))
        
        for idir1 in filesniff.findall_dirs(idir0):
            if pattern.search(idir1):
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


def _copy_checkup_tool(buildir):
    shutil.copyfile('../pyinstaller_for_intranet/checkup.py',
                    f'{buildir}/checkup.py')
    shutil.copyfile('../pyinstaller_for_intranet/pretty_print.py',
                    f'{buildir}/pretty_print.py')


def _copy_venv(src_venv_dir, dst_venv_dir):
    """
    Args:
        src_venv_dir: 'source virtual environment directory'.
            tip: you can pass an empty to this argument, see reason at `Notes:3`
        dst_venv_dir: 'distributed virtual environment directory'
    
    Notes:
        1. 如果您使用了虚拟环境, 则确保本项目 (lkdist) 的 Python 编译器版本与虚
           拟环境的 Python 版本 (即 GlobalConf.proj_required_python_version) 一
           致! 否则 _compile_py_files 编译出来的 .pyc 文件无法运行!
        2. 不能简单地把源 venv 拷贝到打包目录, 因为源 venv 里面的 Python 是不可
           独立使用的. 这意味着, 在一个没有安装过 Python 的用户电脑上, 调用此
           venv 下的 Python 将失败! 我们需要的是一个嵌入版的 Python (在 Python
           官网下载带有 "embed" 字样的压缩包, 并解压, 我在 lib 目录下已经做到
           了), 并且需要在 launch_core.py (see `_create_launcher`) 中显式地引入
           launch_core.py 所在的目录路径和 venv 下的 site-packages 目录的路径 --
           源 venv/Lib/site-packages 拷贝到此处
        3. 出于性能和成本考虑, 您不必提供有效 src_venv_dir 参数, 即您可以给该参
           数传入一个空字符串, 这样本函数会仅创建虚拟环境的框架 (dst_venv_dir),
           但 '{dst_venv_dir}/site-packages' 会留空. 稍后您可以手动地复制, 或剪
           切所需的依赖到 '{dst_venv_dir}/site-packages'
           
    Results:
        copy source dir to target dir:
            lib/python-{version}-embed-amd64 -> {dst_venv_dir}
            {src_venv_dir}/Lib/site-packages -> {dst_venv_dir}/site-packages
    """
    # create venv shell
    if (v := GlobalConf.proj_required_python_version) == '3.8':
        embed_python_dir = '../lib/python-3.8.5-embed-amd64'
    elif v == '3.9':
        embed_python_dir = '../lib/python-3.9.0-embed-amd64'
    else:
        raise Exception('Unsupported target python version!', v)
    shutil.copytree(embed_python_dir, dst_venv_dir)
    
    # copy site-packages
    if ospath.exists(src_venv_dir):
        shutil.copytree(f'{src_venv_dir}/Lib/site-packages',
                        f'{dst_venv_dir}/site-packages')
    else:  # just create a empty dir
        os.mkdir(f'{dst_venv_dir}/site-packages')


def _create_launcher(target_path, target_name, rootdir, extra_sys_paths=None,
                     enable_venv=False):
    """
    创建一个启动器, 启动器分为两部分, 一个位于 '{rootdir}' 目录, 一个位于
    '{rootdir}/src' 目录. 前者生成的文件是 '{rootdir}/launcher.bat', 后者生成的
    文件是 '{rootdir}/src/launcher_core.py' (后面会编译成 launcher_core.pyc). 我
    们可从 '{rootdir}/launcher.bat' 双击启动程序.
    
    Notes:
        1. 启动器的名字暂不支持自定义
        2. 启动器的目录与 target_path 的目录可能不一样, 需要修改为 target_path
           的目录 (即在启动器中调用 `os.chdir` 切换到 target_path 的目录)
           为什么? -- 源码中的相对路径都是相对 target_path 而言的, 所以我们必须
           确保 Python 能把 target_path 所在的目录认作 current working dir (通过
           `os.getcwd` 来验证)
    
    Args:
        target_path: see `main:args:main_script`
        target_name: see `main:args:main_script`
        rootdir: 建议放在发布包的根目录下, 创建名为 'launcher.py' (推荐) 的文件
        extra_sys_paths: tuple|list|None. 该路径会被作为 sys.path 添加到启动模块.
            当使用 空元祖/空列表/None 时, 表示没有额外的导入路径要添加.
            当使用元组/列表时, 每个元素都需要符合以下要求:
                1. 文件夹的路径 (str)
                2. 必须是相对路径. 相对于 srcdir 的路径
        enable_venv: 推荐为 True
    
    References:
        template/launch_by_system.bat
        template/launch_by_venv.bat
        template/launch_core.txt
        
    Results:
        在 '{rootdir}/src' 目录生成一个 launch_core.py (后面会编译成 launch_core
        .pyc); 在  '{rootdir}' 目录生成一个 launch.bat. 然后我们可从 '{rootdir}/
        launch.bat' 双击启动.
    """
    bat_name = 'launch'
    core_name = 'launch_core'
    
    template = loads('template/launch_core.txt')
    launch_code = template.format(
        SITE_PACKAGES='../venv/site-packages' if enable_venv else '',
        EXTRA_SYS_PATHS=str(extra_sys_paths),
        TARGET_PATH=target_path,
        TARGET_DIR=target_path.replace('.', '/'),
        TARGET_NAME=target_name,
    )
    dumps(launch_code, f'{rootdir}/src/{core_name}.py')
    
    # --------------------------------------------------------------------------
    
    if not GlobalConf.create_launch_bat:
        return
    
    if enable_venv:  # suggest
        template = loads('template/launch_by_venv.bat')
    else:
        # 注意: 这个不太安全, 因为我们不能确定用户系统安装默认的 Python 版本是否
        # 与当前编译的 pyc 版本相同.
        template = loads('template/launch_by_system.bat')
    bat_code = template.format(
        LAUNCHER=f'{core_name}.pyc'
        #   注意是 'launch_core.pyc' 而不是 'launch_core.cpython-38.pyc', 原因见
        #   `_compile_py_files:vars:ofp`
    )
    dumps(bat_code, f'{rootdir}/{bat_name}.bat')


def _create_readme(ifile: str, distdir):  # TODO: generate a .html file
    if ifile:
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
        #   注意:
        #       1. 第一个 '../' 表示自身所在的目录, 第二个 '../' 指向上一级目录
        #       2. 不能直接使用 fn, 因为 fn 的后缀是 '.cpython-38.pyc', 会导致
        #          Python 的导入语法不能正常工作 (提示 "ImportError: No module
        #          named 'model'"), 为了解决此问题, 将后缀改为 '.pyc' 即可.
        shutil.move(ifp, ofp)


def _cleanup_py_files(idir):
    # delete __pycache__ folders (the folders are empty)
    for dp in filesniff.findall_dirs(  # dp: 'dirpath'
            idir, suffix='__pycache__',
            exclude_protected_folder=False
    ):
        os.rmdir(dp)
    
    # and delete .py files
    for fp in filesniff.findall_files(idir, suffix='.py'):
        os.remove(fp)


def _save_build_info(buildir, manifest: dict):
    """
    
    Args:
        buildir:
        manifest: {str k: str v, ...}
            见 `vars:default_manifest`. 其中 'suggest filling it' 的部分是推荐您
            传入的, 其他则推荐使用默认值或自动生成的值.
            关于每个键的解释, 见 `vars:default_manifest` 的注释
            See Also "template/manifest.json"
    """
    from sys import version_info as ver
    pyversion = f'{ver.major}.{ver.minor}.0'  # e.g. '3.9.0'
    #   注意是从 buildir 的父目录开始计算的. 它最终的目的是, 描述 launcher_file
    #   相对于 f'{odir}/setup.pyc' 的路径
    
    # update build manifest
    default_manifest = {
        # suggest filling it
        'app_name'      : '',  # 建议首字母大写, 空格分隔的标题命名法
        'app_version'   : '0.1.0',
        'icon'          : '',  # base64 string or bundled file
        'author'        : '',
        'venv'          : '',
        
        # suggest using default
        'enable_venv'   : True,
        'check_pip_repo': True,
        
        # auto generated
        'python_version': pyversion,
    }
    default_manifest.update(manifest)
    manifest = default_manifest
    
    # output
    dumps(manifest, f'{buildir}/manifest.json')


if __name__ == '__main__':
    # main_from_pyproject(
    #     r'D:\Likianta\workspace\com_huawei_likianta\autotest_visual_modeling\pyproject.json'
    # )
    main_from_pyproject(
        r'D:\Likianta\temp\test_20210201_202712\pyproject.json'
    )
