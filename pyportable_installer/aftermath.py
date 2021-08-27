import os
from os import path as ospath

from lk_utils.read_and_write import dumps

from .typehint import *


def main(pyproj_file, prj_conf: TConf, dst_root: TPath):
    _cleanup_scaffold_files(dst_root, prj_conf)
    _generate_manifest(pyproj_file, f'{dst_root}/build')


def _cleanup_scaffold_files(dst_root, prj_conf: TConf):
    from .step3_build_pyproject import thread
    # wait for thread of 'generating exe from bat file' complete
    if thread is not None:
        thread.join()
    # remove bat file
    if ospath.exists(
            f := f'{dst_root}/{prj_conf["build"]["launcher_name"]}.bat'
    ):
        os.remove(f)


def _generate_manifest(pyproj_file, dir_o: TPath):
    from . import step1_extract_pyproject
    conf = step1_extract_pyproject.main(pyproj_file, refmt_to='relpath')
    # 保存配置信息到 `{dir_o}/manifest.json`
    dumps(conf, f'{dir_o}/manifest.json')
