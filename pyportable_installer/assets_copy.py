import os
import re
import shutil
from os import path as ospath

from lk_logger import lk
from lk_utils import filesniff

CURR_DIR = ospath.dirname(__file__).replace('\\', '/')


# def _fmt_curr_dir(func):
#     """
#     Notes:
#         All public functions in this module support a plug-in keyword for path:
#
#         `{CURR_DIR}/some/subfolder/name/bla/bla`
#
#         `{CURR_DIR}` points to `(this_project)/pyportable_installer`, i.e. the
#         directory this module belongs to.
#     """
#     
#     def wrap(*args, **kwargs):
#         new_args = []
#         for e in args:
#             if isinstance(e, str) and '{CURR_DIR}' in e:
#                 new_args.append(e.format(CURR_DIR=CURR_DIR))
#             else:
#                 new_args.append(e)
#                 
#         new_kwargs = {}
#         for k, v in kwargs:
#             if isinstance(v, str) and '{CURR_DIR}' in v:
#                 new_kwargs[k] = v.format(CURR_DIR=CURR_DIR)
#             else:
#                 new_kwargs[k] = v
#                 
#         return func(*new_args, **new_kwargs)
#     
#     return wrap


def copy_checkup_tool(assets_dir, build_dir):
    """
    Args:
        assets_dir: `pyportable_installer/checkup`
        build_dir
    """
    dir_i, dir_o = assets_dir, build_dir
    shutil.copyfile(f'{dir_i}/doctor.py', f1 := f'{dir_o}/doctor.py')
    shutil.copyfile(f'{dir_i}/pretty_print.py', f2 := f'{dir_o}/pretty_print.py')
    return f1, f2


def copy_sources(proj_dir, src_dir):
    """
    将 proj_dir 的内容全部拷贝到 src_dir 下, 并返回 src_dir 以及 src_dir 的所有
    子目录.
    
    Args:
        proj_dir: 'project directory'. see `prebuild.py:_build_pyproject:params
            :proj_dir`
        src_dir: 'source code directory'. 传入 `prebuild.py:_build_pyproject
            :vars:src_dir`
    """
    yield from copy_assets({proj_dir: 'assets,compile'}, src_dir)


def copy_runtime(template_dir, src_dir, dirs_to_compile):
    """
    template_dir                             src_dir
    |= pytransform ========= copy =========> |= pytransform
        |- __init__.py                           |- __init__.py
        |- _pytransform.dll                      |- _pytransform.dll
    
    Args:
        template_dir: `{globals:CURR_DIR}/template`
        src_dir: see `pyarmor_compile.py > main > params:src_dir`
        dirs_to_compile: see `pyarmor_compile.py > main > params:dirs_to_compile`
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


def copy_assets(attachments, src_dir) -> str:
    """
    Args:
        attachments (dict): {dir_i: type_, ...}
            dir_i (str)
            type_ (str):
                ('assets' |
                 'root_assets' |
                 'only_folder' |
                 'only_folders' |
                 'assets,compile' |
                 'root_assets,compile')
                note: 当 type_ 为 'assets' 时, 需要判断是 file 还是 dir. (其他情
                况均是 dir, 不用判断)
        src_dir

    Yields:
        dirpath which needs to be compiled
    """
    
    for dir_i, type_ in attachments.items():
        dirname = ospath.basename(dir_i)
        dir_o = f'{src_dir}/{dirname}'
        
        type_ = tuple(type_.split(','))
        
        if 'root_assets' in type_:
            if not ospath.exists(dir_o): os.mkdir(dir_o)
            for fp, fn in filesniff.find_files(dir_i, fmt='zip'):
                shutil.copyfile(fp, f'{dir_o}/{fn}')
        elif 'assets' in type_:
            if 'compile' in type_:
                _copy_tree_exclude_protected_folders(dir_i, dir_o)
            elif ospath.isfile(dir_i):
                file_i, file_o = dir_i, dir_o
                shutil.copyfile(file_i, file_o)
            else:
                filesniff.force_create_dirpath(ospath.dirname(dir_o))
                shutil.copytree(dir_i, dir_o)
        elif 'only_folders' in type_:
            if not ospath.exists(dir_o): os.mkdir(dir_o)
            for dp, dn in filesniff.findall_dirs(dir_i, fmt='zip'):
                os.mkdir(dp.replace(dir_i, dir_o, 1))
        elif 'only_folder' in type_:
            os.mkdir(dir_o)
        
        if 'compile' in type_:
            yield dir_o
            for d in filesniff.findall_dirs(dir_o):
                yield d


def _copy_tree_exclude_protected_folders(rootdir_i, rootdir_o):
    invalid_pattern = re.compile(r'/(\.|__?)\w+')
    #   e.g. '/.git', '/__pycache__'
    
    valid_dirs = [(rootdir_i, rootdir_o)]  # [(i, o), ...]
    # FIXME: 1.4.4 版本的 lk-utils.filesniff.findall_dirs 不完善, 无法完全地过滤
    #   掉需要被排除的文件, 所以我们自定义一个 invalid_pattern 来处理
    for dir_i in filesniff.findall_dirs(rootdir_i):
        if invalid_pattern.match(dir_i):
            continue
        dir_o = f'{rootdir_o}/{dir_i.replace(rootdir_i + "/", "", 1)}'
        valid_dirs.append((dir_i, dir_o))
    lk.reset_count()
    
    for (i, o) in valid_dirs:
        filesniff.force_create_dirpath(o)
        for fp, fn in filesniff.find_files(i, fmt='zip'):
            fp_i, fp_o = fp, f'{o}/{fn}'
            shutil.copyfile(fp_i, fp_o)
    del valid_dirs


def create_readme(file_i: str, distdir):
    file_o = f'{distdir}/{ospath.basename(file_i)}'
    shutil.copyfile(file_i, file_o)
