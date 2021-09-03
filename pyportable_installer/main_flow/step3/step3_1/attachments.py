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


def copy_attchments(attachments: TAttachments) -> Iterator[tuple[TPath, TPath]]:
    """ Specific for handling assets in datatype:`~.typehint.TAttachments`.
    
    Attachments Marks (`TAttachments._TAttachmentsValue.marks`):
        
        Single Mark
        -----------
        
        asset:
            Assert path type is file, and copy the single file.
        assets:
            If path type is directory, copy the whole tree.
            If path type is file, the same behavior with `asset`.
        root_assets:
            Assert path type is directory, and copy only root assets (files and
            (creating) empty folders) in it.
        only_folder:
            Create an empty folder in dist side.
        only_folders:
            Create empty folders tree in dist side.
        
        Double Mark
        -----------
        
        asset, compile:
            Inherit `asset` behavior, and assert the path ends with '.py', and
            yield to the caller.
        assets, compile:
            Inherit `assets` behavior, and find python files from them, and
            yield to the caller.
        root_assets, compile:
            pass
        
    
    关于 `attachments` 的标记:
        FIXME (2021-08-18): 下述描述中涉及 'dist:xxx' 的部分已过时, 请及时更新.

        `attachments` 的结构为 `{file_or_dirpath: mark, ...}`. 其中键都是原始路
        径下的文件 (夹) (assert exist). 值 mark 有以下可选:

        单标记:

        'assets'            复制目录下的全部文件 (夹)
        'root_assets'       只复制根目录下的文件
        'only_folder'       只复制根目录, 相当于在 `dst_dir` 创建相应的空目录
        'only_folders'      只复制根目录和全部子目录, 相当于在 `dst_dir` 创建相
                            应的空目录树

        双标记:

        'assets,compile'            复制目录下的全部文件 (夹), 但对 *.py 文件不
                                    复制, 而是作为待编译的文件 yield 给调用者
        'root_assets,compile'       只复制根目录下的文件, 但对 *.py 文件不复制,
                                    而是作为待编译的文件 yield 给调用者
        'assets,dist:lib'           复制目录下的全部文件 (夹), 复制到打包目录下
                                    的 'lib' 文件夹中
        'assets,dist:root'          同上, 将目标目录 `dst_dir/lib` 改为 `dit_dir`
        'root_assets,dist:lib'      只复制根目录下的文件, 复制到打包目录下的
                                    'lib' 文件夹中
        'root_assets,dist:root'     同上, 将目标目录 `dst_dir/lib` 改为 `dit_dir`
        'only_folder,dist:lib'      只复制根目录, 复制到打包目录下的 'lib' 文件
                                    夹中 (相当于在 `dst_dir/lib` 创建相应的空目
                                    录)
        'only_folder,dist:root'     同上, 将目标目录 `dst_dir/lib` 改为 `dit_dir`
        'only_folders,dist:lib'     只复制根目录和全部子目录, 复制到打包目录下的
                                    'lib' 文件夹中 (相当于在 `dst_dir/lib` 创建
                                    相应的空目录树)
        'only_folders,dist:root'    同上, 将目标目录 `dst_dir/lib` 改为 `dit_dir`

        三标记:

        'assets,compile,dist:lib'           复制目录下的全部文件 (夹), 复制到打
                                            包目录下的 'lib' 文件夹中, 但对 *.py
                                            文件不复制, 而是作为待编译的文件
                                            yield 给调用者
        'assets,compile,dist:root'          同上, 将目标目录 `dst_dir/lib` 改为
                                            `dit_dir`
        'root_assets,compile,dist:lib'      只复制根目录下的文件, 复制到打包目录
                                            下的 'lib' 文件夹中, 但对 *.py 文件
                                            不复制, 而是作为待编译的文件 yield
                                            给调用者
        'root_assets,compile,dist:root'     同上, 将目标目录 `dst_dir/lib` 改为
                                            `dit_dir`

        *注: 上表内容可能过时, 最终请以 `docs/pyproject-template.md` 为准!*

    注意:
        `attachments.keys` 在 `./main.py > func:main > step2` (i.e.
        `./no2_prebuild_pyproject.py > func:main`) 期间就全部建立了 (空文件夹),
        所以没必要再创建; 剩下没创建的是各目录下的 "子文件夹" ('assets',
        'assets,compile', 'only_folders' 这三种情况).

    Args:
        attachments (dict):

    Yields:
        tuple[src_pyfile, dst_pyfile]
    """
    global _excludes
    
    def handle_assets(dir_i, dir_o):
        copytree(dir_i, dir_o, dirs_exist_ok=True)
    
    def handle_assets_and_compile(dir_i, dir_o):
        # first handle roots'
        yield from handle_root_assets_and_compile(dir_i, dir_o)
        # then handle subdirs'
        for dp_i, dp_o in handle_only_folders(dir_i, dir_o):
            yield from handle_root_assets_and_compile(dp_i, dp_o)
    
    def handle_root_assets_and_compile(dir_i, dir_o):
        for fp, fn in find_files(dir_i, fmt='zip'):
            if _excludes.is_protected(fn, fp, 'file'):
                lk.logt('[D1408]', 'skip making file', fp)
                continue
            fp_i, fp_o = fp, f'{dir_o}/{fn}'
            if fn.endswith('.py'):
                yield fp_i, fp_o
            else:
                copyfile(fp_i, fp_o)
    
    def handle_root_assets(dir_i, dir_o):
        for fp, fn in find_files(dir_i, fmt='zip'):
            if _excludes.is_protected(fn, fp, 'file'):
                lk.logt('[D1408]', 'skip making file', fp)
                continue
            copyfile(fp, f'{dir_o}/{fn}')
    
    # noinspection PyUnusedLocal
    def handle_only_folder(dir_i, dir_o):
        assert exists(dir_o)
    
    def handle_only_folders(dir_i, dir_o):
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
    
    def handle_asset(file_i, file_o):
        copyfile(file_i, file_o)
    
    # noinspection PyUnusedLocal
    def handle_compile(file_i, file_o):
        assert file_i.endswith('.py')
        yield file_i, file_o
    
    # --------------------------------------------------------------------------
    
    for k, v in attachments.items():
        path_i = k
        path_o = v['path'] or src_2_dst(path_i)
        marks = v['marks']  # e.g. ('assets', 'compile')
        
        is_yield_pyfile = 'compile' in marks  # type: bool
        #   True: yield pyfile; False: copy pyfile
        
        # 1. `path_i` is file
        if 'asset' in marks or isfile(path_i):
            if is_yield_pyfile:
                yield from handle_compile(path_i, '')
            else:
                handle_asset(path_i, path_o)
            continue
        
        # 2. `path_i` is dir
        dir_i = path_i
        dir_o = path_o
        
        if not exists(dir_o):
            mkdir(dir_o)
        
        if 'root_assets' in marks:
            if is_yield_pyfile:
                yield from handle_root_assets_and_compile(dir_i, dir_o)
            else:
                handle_root_assets(dir_i, dir_o)
        
        elif 'assets' in marks:
            if is_yield_pyfile:
                yield from handle_assets_and_compile(dir_i, dir_o)
            else:
                handle_assets(dir_i, dir_o)
        
        elif 'only_folders' in marks:
            assert is_yield_pyfile is False
            handle_only_folders(dir_i, dir_o)
        
        elif 'only_folder' in marks:
            assert is_yield_pyfile is False
            handle_only_folder(dir_i, dir_o)
        
        else:
            raise ValueError('unknown mark or incomplete mark', marks)


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
