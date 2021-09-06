from os import mkdir
from os.path import exists
from os.path import isfile
from shutil import copyfile
from shutil import copytree

from lk_logger import lk
from lk_utils import find_files
from lk_utils import findall_dirs

from ....path_model import src_2_dst
from ....typehint import *


def copy_attachments(attachments: TAttachments) -> Iterator[tuple[TPath, TPath]]:
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
    
    Yields:
        tuple[src_pyfile, dst_pyfile]
    """
    global _excludes
    
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
        if 'asset' in marks or isfile(path_i):
            if is_yield_pyfile:
                yield from _handle_compile(path_i, '')
            else:
                _handle_asset(path_i, path_o)
            continue
        
        # 2. `path_i` is dir
        dir_i = path_i
        dir_o = path_o
        
        # # assert exists(dir_o)
        if not exists(dir_o):
            mkdir(dir_o)
        
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
    copytree(dir_i, dir_o, dirs_exist_ok=True)


def _handle_assets_and_compile(dir_i, dir_o):
    # first handle roots'
    yield from _handle_root_assets_and_compile(dir_i, dir_o)
    # then handle subdirs'
    for dp_i, dp_o in _handle_only_folders(dir_i, dir_o):
        yield from _handle_root_assets_and_compile(dp_i, dp_o)


def _handle_root_assets_and_compile(dir_i, dir_o):
    for fp, fn in find_files(dir_i, fmt='zip'):
        if _excludes.is_protected(fn, fp, 'file'):
            lk.logt('[D1408]', 'skip making file', fp)
            continue
        fp_i, fp_o = fp, f'{dir_o}/{fn}'
        if fn.endswith('.py'):  # TODO: ~.endswith(('.py', '.pyw', ...))
            yield fp_i, fp_o
        else:
            copyfile(fp_i, fp_o)


def _handle_root_assets(dir_i, dir_o):
    for fp, fn in find_files(dir_i, fmt='zip'):
        if _excludes.is_protected(fn, fp, 'file'):
            lk.logt('[D1408]', 'skip making file', fp)
            continue
        copyfile(fp, f'{dir_o}/{fn}')


# noinspection PyUnusedLocal
def _handle_only_folder(dir_i, dir_o):
    assert exists(dir_o)


def _handle_only_folders(dir_i, dir_o):
    out = []
    for dp, dn in findall_dirs(
            dir_i, fmt='zip', exclude_protected_folders=False
            #                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #   set this param to False, we will use our own exclusion rule
            #   (i.e. `globals:_excludes.is_protected`) instead.
    ):
        if _excludes.is_protected(dn, dp, 'dir'):
            lk.logt('[D1409]', 'skip making dir', dp)
            continue
        subdir_i, subdir_o = dp, dp.replace(dir_i, dir_o, 1)
        if not exists(subdir_o): mkdir(subdir_o)
        out.append((subdir_i, subdir_o))
    return out


def _handle_asset(file_i, file_o):
    copyfile(file_i, file_o)


# noinspection PyUnusedLocal
def _handle_compile(file_i, file_o):
    assert file_i.endswith('.py')
    yield file_i, file_o


# -----------------------------------------------------------------------------

class ExcludedPaths:
    
    def __init__(self):
        self.protected_dirnames = ('__pycache__', '.git', '.idea', '.svn')
        self.protected_filenames = ('.gitkeep', '.gitignore')
        self.excluded_paths = set()
    
    def is_protected(self, name: str, path: str, ftype):
        if ftype == 'file':
            _protected_list = self.protected_filenames
        else:
            _protected_list = self.protected_dirnames
        
        if name in _protected_list or \
                path.startswith(tuple(self.excluded_paths)):
            self.excluded_paths.add(path + '/')
            return True
        return False


_excludes = ExcludedPaths()
