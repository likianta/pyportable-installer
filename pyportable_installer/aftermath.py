import os
from os import path as ospath


def cleanup_files(dst_root, prj_conf):
    from .no3_build_pyproject import thread
    if thread is not None:
        thread.join()
    if ospath.exists(f := f'{dst_root}/{prj_conf["app_name"]}.bat'):
        os.remove(f)
