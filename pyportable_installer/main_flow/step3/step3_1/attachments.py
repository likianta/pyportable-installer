import os
from os import path as xpath
from shutil import copyfile

from lk_utils import filesniff

from .exclusions import attachments_exclusions_handler
from ....global_conf import gconf
from ....path_model import src_2_dst
from ....typehint import *

__all__ = ['copy_attachments']


def find_files(dir_i):
    for fp, fn in filter(
            lambda x: attachments_exclusions_handler.filter_files(*x),
            filesniff.find_files(dir_i, fmt='zip')
    ):
        yield fp, fn


def find_dirs(dir_i):
    for dp, dn in filter(
            lambda x: attachments_exclusions_handler.filter_dirs(*x),
            filesniff.find_dirs(
                dir_i, fmt='zip', exclude_protected_folders=False
                #                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                #   set this param to False, we will use `exclusions_handler`
                #   to filter the protected folders.
            )
    ):
        yield dp, dn


def _handle_file_exists(file_o, scheme=''):
    """
    Returns:
        str['go_on', 'done']
            'go_on': going on to do the left things.
            'done': all things have done, do not handle this file.
    """
    if scheme == '':  # see `TBuildConf.attachments_exist_scheme`
        scheme = gconf.attachments_exist_scheme
    
    if scheme == 'error':
        raise FileExistsError(file_o)
    elif scheme == 'override':
        os.remove(file_o)
        return 'go_on'
    elif scheme == 'skip':
        return 'done'
    else:
        raise Exception('Unknown scheme', scheme)


_created_dirs = set()


def copy_attachments(attachments: TAttachments) -> Iterator[Tuple[TPath, TPath]]:
    """ Specific for handling attachmets in format of `~.typehint.TAttachments`.
    
    Attachments Marks (`~.typehint.TAttachments._TAttachmentsValue.marks`):
        See complete docs at `~/docs/attachments-marks-demonstration.md`.
        Single Marks:
            asset
            assets
            root_assets
            only_folder
            only_folders
        Double Marks:
            asset,compile
            assets,compile
            root_assets,compile
            
    Args:
        attachments
        
    Notice:
        This function is a generator, if you just want to call and exhaust it,
        use this:
            _ = list(copy_attachments(...))
        See usages in `pyportable_installer.main_flow.step3.step3_3.create_venv
        .create_venv`.
    
    Yields:
        Tuple[src_pyfile, dst_pyfile]
    """
    global _created_dirs
    
    for k, v in attachments.items():
        path_i = k
        path_o = v['path'] or src_2_dst(path_i)
        #   there's no '{name}' placeholder in `path_i` and `path_o` because in
        #   `~.step1.indexing_paths.indexing_paths > attachments related code`
        #   we've handled them.
        marks = v['marks']  # e.g. ('assets', 'compile')
        
        is_yield_pyfile = 'compile' in marks  # type: bool
        #   True: yield pyfile; False: just copy pyfile
        
        # 1. `path_i` is file
        if 'asset' in marks or xpath.isfile(path_i):
            if attachments_exclusions_handler.monitor_transferring(
                    '', path_i, 'file') is False:
                print(':v', '[D4756]', 'the file is in exclusion list', path_i)
            else:
                if (d := xpath.dirname(path_o)) not in _created_dirs:
                    os.makedirs(d, exist_ok=True)
                    _created_dirs.add(d)
                if is_yield_pyfile:
                    yield from _handle_compile(path_i, path_o)
                else:
                    _handle_asset(path_i, path_o)
            continue
        
        # 2. `path_i` is dir
        dir_i = path_i
        dir_o = path_o
        if dir_o not in _created_dirs:
            os.makedirs(dir_o, exist_ok=True)
            _created_dirs.add(dir_o)
        
        if attachments_exclusions_handler.monitor_transferring(
                '', dir_i, 'dir') is False:
            print(':v', '[D4757]', 'the directory is in exclusion list', dir_i)
            continue
        if not xpath.exists(dir_o):
            os.mkdir(dir_o)
        
        if 'root_assets' in marks:
            if is_yield_pyfile:
                yield from _handle_root_assets_and_compile(dir_i, dir_o)
            else:
                _handle_root_assets(dir_i, dir_o)
        
        elif 'assets' in marks:
            if is_yield_pyfile:
                yield from _handle_assets_and_compile(dir_i, dir_o)
            else:
                _handle_assets(dir_i, dir_o)
        
        elif 'only_folders' in marks:
            assert is_yield_pyfile is False
            _handle_only_folders(dir_i, dir_o)
        
        elif 'only_folder' in marks:
            assert is_yield_pyfile is False
            _handle_only_folder(dir_i, dir_o)
        
        else:
            raise ValueError('Unknown or incomplete mark', marks)


# -----------------------------------------------------------------------------

def _handle_assets(dir_i, dir_o):
    _handle_root_assets(dir_i, dir_o)
    for dp, dn in find_dirs(dir_i):
        subdir_i, subdir_o = dp, f'{dir_o}/{dn}'
        os.mkdir(subdir_o)
        # # if not xpath.exists(subdir_o): mkdir(subdir_o)
        _handle_assets(subdir_i, subdir_o)


def _handle_root_assets(dir_i, dir_o):
    for fp, fn in find_files(dir_i):
        file_i, file_o = fp, f'{dir_o}/{fn}'
        copyfile(file_i, file_o)


def _handle_assets_and_compile(dir_i, dir_o):
    yield from _handle_root_assets_and_compile(dir_i, dir_o)
    for dp, dn in find_dirs(dir_i):
        subdir_i, subdir_o = dp, f'{dir_o}/{dn}'
        if not xpath.exists(subdir_o): os.mkdir(subdir_o)
        yield from _handle_assets_and_compile(subdir_i, subdir_o)


def _handle_root_assets_and_compile(dir_i, dir_o):
    for fp, fn in find_files(dir_i):
        file_i, file_o = fp, f'{dir_o}/{fn}'
        if fn.endswith('.py'):  # TODO: ~.endswith(('.py', '.pyw', ...))
            if xpath.exists(file_o) and _handle_file_exists(file_o) == 'done':
                continue
            yield file_i, file_o  # MARK: 20210913113649
        else:
            copyfile(file_i, file_o)


def _handle_only_folders(dir_i, dir_o):
    for dp, dn in find_dirs(dir_i):
        subdir_i, subdir_o = dp, f'{dir_o}/{dn}'
        _handle_only_folder(subdir_i, subdir_o)
        _handle_only_folders(subdir_i, subdir_o)


# noinspection PyUnusedLocal
def _handle_only_folder(dir_i, dir_o):
    if not xpath.exists(dir_o):
        os.mkdir(dir_o)


def _handle_asset(file_i, file_o):
    copyfile(file_i, file_o)


# noinspection PyUnusedLocal
def _handle_compile(file_i, file_o):
    assert file_i.endswith('.py')
    if xpath.exists(file_o) and _handle_file_exists(file_o) == 'done':
        return
    yield file_i, file_o  # MARK: 20210913113657
