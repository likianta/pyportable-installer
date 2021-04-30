import os
from os import path as ospath

from lk_utils import filesniff


def main(root_dir):  # TODO
    # os.remove(f'{root_dir}/Test New PyProject.bat')
    # cleanup_py_files()
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
