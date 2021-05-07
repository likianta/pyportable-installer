import os
import shutil
from os import path as ospath

from lk_utils import filesniff

from .global_dirs import global_dirs


def copy_checkup_tool(assets_dir, build_dir):
    """
    TODO: add `update.py`
    
    Args:
        assets_dir: `pyportable_installer/checkup`
        build_dir
    """
    dir_i, dir_o = assets_dir, build_dir
    shutil.copyfile(
        f'{dir_i}/doctor.py', f1 := f'{dir_o}/doctor.py'
    )
    shutil.copyfile(
        f'{dir_i}/pretty_print.py', f2 := f'{dir_o}/pretty_print.py'
    )
    return f1, f2


def copy_sources(proj_dir):
    """
    将 proj_dir 的内容全部拷贝到 src_dir 下, 并返回 src_dir 以及 src_dir 的所有
    子目录.
    
    Args:
        proj_dir: 'project directory'. see `prebuild.py > _build_pyproject >
            params:proj_dir`
    """
    yield from copy_assets({proj_dir: 'assets,compile'})


def copy_pytransform_runtime(dir_i, dir_o):
    if ospath.exists(dir_i):
        shutil.copytree(dir_i, dir_o)
    else:
        os.popen(f'pyarmor runtime -O "{dir_o}"')
        #   see `cmd:pyarmor runtime -h`


def copy_runtime(template_dir, src_dir, dirs_to_compile):  # DELETE
    """
    template_dir                             src_dir
    |= pytransform ========= copy =========> |= pytransform
        |- __init__.py                           |- __init__.py
        |- _pytransform.dll                      |- _pytransform.dll
    
    Args:
        template_dir: `{GlobalDirs.PyPortableDir}/template`
        src_dir: see `compiler.py > main > params:src_dir`
        dirs_to_compile: see `compiler.py > main > params:dirs_to_compile`
    """
    from lk_utils.read_and_write import loads, dumps
    
    if ospath.exists(f'{template_dir}/pytransform'):
        shutil.copytree(f'{template_dir}/pytransform', f'{src_dir}/pytransform')
    else:
        os.popen(f'pyarmor runtime -O "{src_dir}"')
        #   see `cmd:pyarmor runtime -h`
    
    pytransform_package_dir = f'{src_dir}/pytransform'
    #   this is an abspath
    pytransform_file_template = loads(f'{template_dir}/pytransform.txt')
    
    for d in dirs_to_compile:
        if os.listdir(d):
            dumps(
                data=pytransform_file_template.format(
                    PYTRANSFORM_RELPKG=ospath.relpath(
                        d, pytransform_package_dir
                    ).replace('../', '..', 1).replace('../', '.')
                ),
                file=f'{d}/pytransform.py'
            )


def copy_venv(src_venv_dir, dst_venv_dir, pyversion, embed_python_dir):
    """
    Args:
        src_venv_dir: 'source virtual environment directory'.
            tip: you can pass an empty to this argument, see reason at `Notes:3`
        dst_venv_dir: 'distributed virtual environment directory'
        pyversion: e.g. '3.8'. 请确保该版本与 pyportable_installer 所用的 Python
            编译器, 以及 src_venv_dir 所用的 Python 版本一致 (修订号可以不一样),
            否则 _compile_py_files 编译出来的 .pyc 文件无法运行!
        embed_python_dir:

    Notes:
        1. 本函数使用了 embed_python 独立安装包的内容, 而非简单地把 src_venv_dir
           拷贝到打包目录, 这是因为 src_venv_dir 里面的 Python 是不可独立使用的.
           也就是说, 在一个没有安装过 Python 的用户电脑上, 调用 src_venv_dir 下
           的 Python 编译器将失败! 所以我们需要的是一个嵌入版的 Python (在
           Python 官网下载带有 "embed" 字样的压缩包, 并解压, 我在 pyportable
           _installer 项目下已经准备了一份)
        2. 出于性能和成本考虑, 您不必提供有效 src_venv_dir 参数, 即您可以给该参
           数传入一个空字符串, 这样本函数会仅创建虚拟环境的框架 (dst_venv_dir),
           并让 '{dst_venv_dir}/site-packages' 留空. 稍后您可以手动地复制, 或剪
           切所需的依赖到 '{dst_venv_dir}/site-packages'

    Results:
        copy source dir to target dir:
            lib/python-{version}-embed-amd64 -> {dst_venv_dir}
            {src_venv_dir}/Lib/site-packages -> {dst_venv_dir}/site-packages
    """
    # TODO
    # create venv shell
    from lk_utils.read_and_write import loads
    conf = loads(f'{embed_python_dir}/conf.json')
    embed_python_dir = {
        # see: 'embed_python/README.md'
        '3.6': f'{embed_python_dir}/{conf["PY36"]}',
        '3.8': f'{embed_python_dir}/{conf["PY38"]}',
        '3.9': f'{embed_python_dir}/{conf["PY39"]}'
    }[pyversion]
    
    shutil.copytree(embed_python_dir, dst_venv_dir)
    
    # copy site-packages
    if ospath.exists(src_venv_dir):
        shutil.copytree(f'{src_venv_dir}/Lib/site-packages',
                        f'{dst_venv_dir}/site-packages')
    else:  # just create an empty folder
        os.mkdir(f'{dst_venv_dir}/site-packages')


def copy_assets(attachments) -> str:
    """ 将 `attachments` 中列出的 assets 类型的文件和文件夹复制到 `dst_dir`.
    
    关于 `attachments` 的标记:
        `attachments` 的结构为 `{file_or_dirpath: mark, ...}`. 其中键都是原始路
        径下的文件 (夹) (assert exist). 值 mark 有以下可选:
        
        'assets'                复制目录下的全部文件 (夹)
        'assets,compile'        复制目录下的全部文件 (夹), 但对 *.py 文件不复制,
                                而是作为待编译的文件 yield 给调用者
        'root_assets'           只复制根目录下的文件
        'root_assets,compile'   只复制根目录下的文件, 但对 *.py 文件不复制, 而是
                                作为待编译的文件 yield 给调用者
        'only_folder'           只复制根目录, 相当于在 `dst_dir` 创建相应的空目
                                录
        'only_folders'          只复制根目录和全部子目录, 相当于在 `dst_dir` 创
                                建相应的空目录树
        'compile'               此时它对应的路径必为 python 脚本文件. 对该文件不
                                复制, 而是作为待编译的文件 yield 给调用者
        'asset'                 此时它对应的路径必为一个文件. 将该文件复制到
                                `dst_dir` 对应的位置
                                注1: 这个标记我们一般不用, 而是用 'assets' 替代
                                注2: 如果有此情况, 则参数 `GlobalDirs.SourceRoot`
                                必须不为空
                                
        *注: 上表内容可能过时, 最终请以 `docs/pyproject-template.md` 为准!*

    注意:
        `attachments.keys` 在 `./main.py > func:main > step2` (i.e.
        `./no2_prebuild_pyproject.py > func:main`) 期间就全部建立了 (空文件夹),
        所以没必要再创建; 剩下没创建的是各目录下的 "子文件夹" ('assets',
        'assets,compile', 'only_folders' 这三种情况).
    
    Args:
        attachments (dict):

    Yields:
        *.py file which needs to be compiled
    """
    
    def handle_assets(dir_i, dir_o):
        shutil.copytree(dir_i, dir_o)

    # noinspection PyUnusedLocal
    def handle_assets_and_compile(dir_i, dir_o):
        for dp, dn in filesniff.findall_dirs(dir_i, fmt='zip'):
            os.mkdir(global_dirs.to_dist(dp))
            for fp, fn in filesniff.find_files(dp, fmt='zip'):
                if fn.endswith('.py'):
                    yield fp
                else:
                    shutil.copyfile(fp, global_dirs.to_dist(fp))
    
    def handle_root_assets_and_compile(dir_i, dir_o):
        for fp, fn in filesniff.find_files(dir_i, fmt='zip'):
            if fn.endswith('.py'):
                yield fp
            else:
                shutil.copyfile(fp, f'{dir_o}/{fn}')
    
    def handle_root_assets(dir_i, dir_o):
        for fp, fn in filesniff.find_files(dir_i, fmt='zip'):
            shutil.copyfile(fp, f'{dir_o}/{fn}')
    
    # noinspection PyUnusedLocal
    def handle_only_folder(dir_i, dir_o):
        assert ospath.exists(dir_o)
    
    def handle_only_folders(dir_i, dir_o):
        for dp, dn in filesniff.findall_dirs(dir_i, fmt='zip'):
            os.mkdir(dp.replace(dir_i, dir_o, 1))
    
    def handle_asset(file_i, file_o):
        shutil.copyfile(file_i, file_o)
    
    # noinspection PyUnusedLocal
    def handle_compile(file_i, file_o):
        yield file_i
    
    for path_i, mark in attachments.items():
        mark = tuple(mark.split(','))
        #   e.g. ('assets', 'compile')
        is_yield_pyfile = 'compile' in mark
        #   True: yield pyfile; False: copy pyfile
        
        if ospath.isfile(path_i):
            if is_yield_pyfile:
                yield from handle_compile(path_i, '')
            else:
                path_o = global_dirs.to_dist(path_i)
                handle_asset(path_i, path_o)
            continue
        
        # ----------------------------------------------------------------------
        
        dir_i = path_i
        dir_o = global_dirs.to_dist(path_i)
        
        if 'root_assets' in mark:
            if is_yield_pyfile:
                yield from handle_root_assets_and_compile(dir_i, dir_o)
            else:
                handle_root_assets(dir_i, dir_o)
        
        elif 'assets' in mark:
            if is_yield_pyfile:
                yield from handle_assets_and_compile(dir_i, dir_o)
            else:
                handle_assets(dir_i, dir_o)
        
        if 'only_folders' in mark:
            assert is_yield_pyfile is False
            handle_only_folders(dir_i, dir_o)
        
        elif 'only_folder' in mark:
            assert is_yield_pyfile is False
            handle_only_folder(dir_i, dir_o)
        
        # if set(mark) != {
        #     'asset', 'assets', 'compile', 'only_folder', 'only_folders',
        #     'root_assets',
        # }:
        #     raise ValueError('Unknown mark', mark)


def create_readme(file_i: str, file_o: str):
    # TODO: import a markdown_2_html converter
    shutil.copyfile(file_i, file_o)
