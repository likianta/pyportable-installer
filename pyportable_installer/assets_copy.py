import os
import shutil
from os import path as ospath

from lk_utils import filesniff

from .global_dirs import global_dirs
from .typehint import *


def copy_checkup_tool(assets_dir: TPath, build_dir: TPath):
    """
    TODO: add `update.py`
    
    Args:
        assets_dir: `pyportable_installer/checkup`
        build_dir
    """
    dir_i, dir_o = assets_dir, build_dir
    shutil.copyfile(
        f'{dir_i}/doctor.py', f1 := f'{dir_o}/doctor.py'
    )
    shutil.copyfile(
        f'{dir_i}/pretty_print.py', f2 := f'{dir_o}/pretty_print.py'
    )
    return f1, f2


def copy_sources(proj_dir: TPath):
    """
    将 proj_dir 的内容全部拷贝到 src_dir 下, 并返回 src_dir 以及 src_dir 的所有
    子目录.
    
    Args:
        proj_dir: 'project directory'. see `prebuild.py > _build_pyproject >
            params:proj_dir`
    """
    yield from copy_assets({proj_dir: 'assets,compile'})


def copy_assets(attachments: TAttachments) -> str:
    """ 将 `attachments` 中列出的 assets 类型的文件和文件夹复制到 `dst_dir`.
    
    关于 `attachments` 的标记:
        
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
    
    Notes:
        由于在 `pyportable_installer/no1_extract_pyproject.py:PathFormatter:
        __call__` 中对 'dist:root' 转换成了 'dist:', 所以 `args:attachments:
        values:each` 中不再有 'dist:root', 而是用 'dist:' 表示.

    Yields:
        *.py file which needs to be compiled
    """
    
    def handle_assets(dir_i, dir_o):
        shutil.copytree(dir_i, dir_o, dirs_exist_ok=True)
    
    def handle_assets_and_compile(dir_i, dir_o, to_dist):
        # first handle roots'
        yield from handle_root_assets_and_compile(dir_i, dir_o)
        # then handle subdirs'
        for dp_i, dp_o in handle_only_folders(dir_i, to_dist):
            for fp, fn in filesniff.findall_files(dp_i, fmt='zip'):
                if fn.endswith('.py'):
                    yield fp
                else:
                    fp_i, fp_o = fp, f'{dp_o}/{fn}'
                    shutil.copyfile(fp_i, fp_o)
    
    def handle_root_assets_and_compile(dir_i, dir_o):
        # if not ospath.exists(dir_o):
        #     os.mkdir(dir_o)
        for fp, fn in filesniff.find_files(dir_i, fmt='zip'):
            if fn.endswith('.py'):
                yield fp
            else:
                shutil.copyfile(fp, f'{dir_o}/{fn}')
    
    def handle_root_assets(dir_i, dir_o):
        for fp, fn in filesniff.find_files(dir_i, fmt='zip'):
            shutil.copyfile(fp, f'{dir_o}/{fn}')
    
    # noinspection PyUnusedLocal
    def handle_only_folder(dir_i, dir_o):
        assert ospath.exists(dir_o)
    
    def handle_only_folders(dir_i, to_dist):
        global _excludes
        for dp, dn in filesniff.findall_dirs(
                dir_i, fmt='zip', exclude_protected_folders=False
                #                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                #   set this param to False, we will use our own exclusion rule
                #   (i.e. `globals:PROTECTED_DIRS`) instead.
        ):
            if _excludes.is_protected(dn, dp):
                continue
            dp_i, dp_o = dp, to_dist(dp)
            os.mkdir(dp_o)
            yield dp_i, dp_o
    
    def handle_asset(file_i, file_o):
        shutil.copyfile(file_i, file_o)
    
    # noinspection PyUnusedLocal
    def handle_compile(file_i, file_o):
        assert file_i.endswith('.py')
        yield file_i
    
    # --------------------------------------------------------------------------
    
    for path_i, mark in attachments.items():
        mark = tuple(mark.split(','))
        #   e.g. ('assets', 'compile')
        is_yield_pyfile = 'compile' in mark
        #   True: yield pyfile; False: copy pyfile
        
        if mark[-1].startswith('dist:'):
            dst_root = ospath.dirname(global_dirs.dst_root)
            #   note `global_dirs.dst_root` is not a real root of dist dir. it
            #   points to `{dist}/src`. so we use `ospath.dirname(global_dirs
            #   .dst_root)` to get the real root of dist.
            src_to_dst = lambda _: mark[-1].replace(
                'dist:', f'{dst_root}/').rstrip('/')
            #   `dist:` 相当于 `{dst_root}`
            #   `dist:/xxx` 相当于 `{dst_root}/xxx`
            #   `dist:lib/xxx` 相当于 `{dst_root}/lib/xxx`
        else:
            src_to_dst = lambda p: global_dirs.to_dist(p)
        
        # 1. `path_i` is file
        if 'asset' in mark or ospath.isfile(path_i):
            if is_yield_pyfile:
                yield from handle_compile(path_i, '')
            else:
                path_o = src_to_dst(path_i)
                handle_asset(path_i, path_o)
            continue
        
        # 2. `path_i` is dir
        dir_i = path_i
        dir_o = src_to_dst(path_i)
        if not ospath.exists(dir_o):
            os.mkdir(dir_o)
        
        if 'root_assets' in mark:
            if is_yield_pyfile:
                yield from handle_root_assets_and_compile(dir_i, dir_o)
            else:
                handle_root_assets(dir_i, dir_o)
        
        elif 'assets' in mark:
            if is_yield_pyfile:
                yield from handle_assets_and_compile(dir_i, dir_o, src_to_dst)
            else:
                handle_assets(dir_i, dir_o)
        
        elif 'only_folders' in mark:
            assert is_yield_pyfile is False
            handle_only_folders(dir_i, src_to_dst)
        
        elif 'only_folder' in mark:
            assert is_yield_pyfile is False
            handle_only_folder(dir_i, dir_o)
        
        else:
            raise ValueError('unknown mark or incomplete mark', mark)


def create_readme(file_i: TPath, file_o: TPath):
    # TODO: import a markdown_2_html converter.
    #   e.g. https://github.com/likianta/markdown_images_to_base64
    # if file_i.endswith('.md'):
    #     try:
    #         from markdown_images_to_base64 import md_2_html_base64
    #         return md_2_html_base64(
    #             file_i, file_o.removesuffix('.md') + '.html'
    #         )
    #     except ImportError:
    #         pass
    shutil.copyfile(file_i, file_o)


class ExcludedPaths:
    
    def __init__(self):
        self.protected_dirnames = ('__pycache__', '.git', '.idea', '.svn')
        self.excluded_paths = set()
    
    def is_protected(self, name: str, path: str):
        if name in self.protected_dirnames or \
                path.startswith(tuple(self.excluded_paths)):
            self.excluded_paths.add(path + '/')
            return True
        return False


_excludes = ExcludedPaths()
