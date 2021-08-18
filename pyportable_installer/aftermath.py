import os
from os import path as ospath

from lk_utils.read_and_write import dumps, load_list

from .typehint import *


def main(prj_conf: TConf, dst_root: TPath):
    _cleanup_scaffold_files(dst_root, prj_conf)
    _generate_manifest(prj_conf, f'{dst_root}/build')


def _cleanup_scaffold_files(dst_root, prj_conf):
    from .no3_build_pyproject import thread
    # wait for thread of 'generating exe from bat file' complete
    if thread is not None:
        thread.join()
    # remove bat file
    if ospath.exists(f := f'{dst_root}/{prj_conf["app_name"]}.bat'):
        os.remove(f)


def _generate_manifest(prj_conf: TConf, dir_o: TPath):
    """
    
    Args:
        prj_conf:
        dir_o: `{dst_root}/build`
    """
    # 如果 `conf:build:venv:...:requirements` 是文件, 则转为列表.
    if prj_conf['build']['venv']['enable_venv']:
        mode = prj_conf['build']['venv']['mode']
        # noinspection PyTypedDict
        options = prj_conf['build']['venv']['options'][mode]  # type: dict
        if req := options.get('requirements'):
            if isinstance(req, str):
                options['requirements'] = load_list(req)
    
    # 将 `prj_conf` 中的所有路径的值改为基于 dist_root 的路径 (绝对路径)
    from .global_dirs import global_dirs
    from .no1_extract_pyproject import PathFormatter, reformat_paths
    
    prj_conf = reformat_paths(
        prj_conf, path_fmt=lambda p: global_dirs.to_dist(p) if p else ''
    )
    
    # 然后, 基于安全考虑, 再将这些绝对路径转换为相对路径 (相对于 `dir_o`, 即
    # `打包目录/build`)
    prj_conf = reformat_paths(prj_conf, PathFormatter(dir_o, 'relpath'))
    
    # 保存配置信息到 `{dir_o}/manifest.json`
    dumps(prj_conf, f'{dir_o}/manifest.json')
