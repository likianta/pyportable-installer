from os import mkdir
from os import remove
from os.path import exists
from os.path import isfile
from shutil import copyfile
from shutil import copytree

from lk_logger import lk
from lk_utils import find_files
from lk_utils import findall_dirs

from ....global_conf import gconf
from ....path_model import src_2_dst
from ....typehint import *

_file_exists_scheme = 'error'


def _handle_file_exists(file_o):
    """
    Returns:
        str['go_on', 'done']
            'go_on': going on to do the left things.
            'done': all things have done, do not handle this file.
    """
    if _file_exists_scheme == 'error':
        raise FileExistsError(file_o)
    elif _file_exists_scheme == 'override':
        remove(file_o)
        return 'go_on'
    elif _file_exists_scheme == 'skip':
        return 'done'
    else:
        raise Exception('Unknown scheme', _file_exists_scheme)


def copy_attachments(
        attachments: TAttachments, exists_scheme='error'
) -> Iterator[tuple[TPath, TPath]]:
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
        exists_scheme: see `TBuildConf.attachments_exist_scheme`
        
    Notice:
        This function is a generator, if you just want to call and exhaust it,
        use this:
            _ = list(copy_attachments(my_attachments))
    
    Yields:
        tuple[src_pyfile, dst_pyfile]
    """
    global _exclusion_handler, _file_exists_scheme
    _file_exists_scheme = exists_scheme
    
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
                yield from _handle_compile(path_i, path_o)
            else:
                _handle_asset(path_i, path_o)
            continue
        
        # 2. `path_i` is dir
        dir_i = path_i
        dir_o = path_o
        
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
        if _exclusion_handler.is_protected(fn, fp, 'file'):
            lk.logt('[D1408]', 'skip making file', fp)
            continue
        fp_i, fp_o = fp, f'{dir_o}/{fn}'
        if fn.endswith('.py'):  # TODO: ~.endswith(('.py', '.pyw', ...))
            if exists(fp_o) and _handle_file_exists(fp_o) == 'done':
                continue
            if _exclusion_handler.filter_yielding(fp_i):
                yield fp_i, fp_o  # MARK: 20210913113649
        else:
            copyfile(fp_i, fp_o)


def _handle_root_assets(dir_i, dir_o):
    for fp, fn in find_files(dir_i, fmt='zip'):
        if _exclusion_handler.is_protected(fn, fp, 'file'):
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
        if _exclusion_handler.is_protected(dn, dp, 'dir'):
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
    if exists(file_o) and _handle_file_exists(file_o) == 'done':
        return
    if _exclusion_handler.filter_yielding(file_i):
        yield file_i, file_o  # MARK: 20210913113657


# -----------------------------------------------------------------------------

class AttachmentsExclusions:
    
    def __init__(self):
        self.protected_dirnames = ('__pycache__', '.git', '.idea', '.svn')
        self.protected_filenames = ('.gitkeep', '.gitignore')
        self.excluded_paths = set()
        
    @staticmethod
    def filter_yielding(file: str):
        """
        This filter moniters and checks whether a file is yieldable.
        
        - The `param:file` comes from `TAttachments:keys`.
        - This method use global exclusions which is provided by `gconf
          .attachments_exclusions`.
            - `gconf.attachments_exclusions` is initialized at `~.main_flow
              .step1.init_key_params`.
        - The filter points are functions in this module and has a `yield`
          statement (note not `yield from` statement). See functions: `_handle
          _compile` (MARK@20210913113657) and `_handle_root_assets_and_compile`
          (MARK@20210913113649).
        
        Returns:
            True: pass through
            False: forbit yielding
        """
        if (file + '/').startswith(gconf.attachments_exclusions):
            lk.logt('[D5034]', 'AttchmentsExclusions monitor has intercepted '
                               'this yieldment', file, h='parent')
            return False
        else:
            return True
    
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


_exclusion_handler = AttachmentsExclusions()
