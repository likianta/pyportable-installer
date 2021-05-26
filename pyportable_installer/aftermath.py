import os
from os import path as ospath


def cleanup_files(dst_root, prj_conf):
    if ospath.exists(f := f'{dst_root}/{prj_conf["app_name"]}.bat'):
        os.remove(f)
    pass
