import os
from os import path as ospath

from lk_utils.read_and_write import dumps, load_list

from .typehint import *


def main(pyprj_file: TPath, prj_conf: TConf, dst_root: TPath):
    cleanup_files(dst_root, prj_conf)
    
    # 如果 `conf:build:venv:...:requirements` 是文件, 则转为列表.
    if prj_conf['build']['venv']['enable_venv']:
        mode = prj_conf['build']['venv']['mode']
        # noinspection PyTypedDict
        options = prj_conf['build']['venv']['options'][mode]  # type: dict
        if req := options.get('requirements'):
            if isinstance(req, str):
                options['requirements'] = load_list(req)
    
    # 安全起见, 将 `prj_conf` 中所有涉及绝对路径的值全部改为相对路径, 以避免在客
    # 户端暴露这些内容.
    from .global_dirs import pretty_path
    from .no1_extract_pyproject import reformat_paths, PathFormatter
    prj_conf = reformat_paths(prj_conf, PathFormatter(
        pretty_path(ospath.dirname(pyprj_file)), 'relpath'
    ))
    
    # 保存配置信息到 `{dst_root}/build/manifest.json`
    dumps(prj_conf, f'{dst_root}/build/manifest.json')


def cleanup_files(dst_root, prj_conf):
    from .no3_build_pyproject import thread
    # wait for thread of 'generating exe from bat file' complete
    if thread is not None:
        thread.join()
    # remove bat file
    if ospath.exists(f := f'{dst_root}/{prj_conf["app_name"]}.bat'):
        os.remove(f)
