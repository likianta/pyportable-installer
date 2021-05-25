import os
from os import path as ospath

from lk_utils import filesniff


def main(dst_root, prj_conf):
    if ospath.exists(f := f'{dst_root}/{prj_conf["app_name"]}.bat'):
        os.remove(f)
    pass


def cleanup_py_files(dir_i, recursive=True):  # DELETE
    if recursive:
        # delete __pycache__ folders (the folders are empty)
        for dp in filesniff.findall_dirs(  # dp: 'dirpath'
                dir_i, suffix='__pycache__',
                exclude_protected_folders=False
        ):
            os.rmdir(dp)
        
        # and delete .py files
        for fp in filesniff.findall_files(dir_i, suffix='.py'):
            os.remove(fp)
    else:
        if ospath.exists(d := f'{dir_i}/__pycache__'):
            os.rmdir(d)
        for fp in filesniff.find_files(dir_i, suffix='.py'):
            os.remove(fp)
