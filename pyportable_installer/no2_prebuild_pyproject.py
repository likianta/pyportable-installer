from os import mkdir
from os import path as ospath

from lk_logger import lk


def main(conf: dict):
    """ Create dist tree (all empty folders under dist root) """
    if ospath.exists(d := conf['build']['dist_dir']):
        raise FileExistsError(d)
    else:
        # create build_dir, lib_dir, src_dir
        mkdir(conf['build']['dist_dir'])
        mkdir(conf['build']['dist_dir'] + '/build')
        mkdir(conf['build']['dist_dir'] + '/lib')
        mkdir(conf['build']['dist_dir'] + '/src')
    
    dist_tree = DistTree()
    dist_tree.add_src_dirs(
        conf['build']['proj_dir'],
        # # conf['build']['dist_dir'],
        #   dist_dir 不属于 srd_dirs 范畴
        # # conf['build']['icon'],
        #   icon 仅用作生成 exe 时的图标, 不会加入到 src_dirs
        # # conf['build']['readme'],
        #   readme 文件会放在根目录, 所以不加入到 src_dirs
        conf['build']['target']['file'],
        conf['build']['required']['venv'],
        *conf['build']['module_paths'],
        *(k for k, v in conf['build']['attachments'].items()
          if 'dist_lib' not in v and 'dist_root' not in v),
    )
    
    src_root = dist_tree.suggest_src_root()
    lk.loga(src_root)
    dst_root = conf['build']['dist_dir']
    dist_tree.build_dst_dirs(src_root, f'{dst_root}/src')
    # dist_tree.build_dst_dirs(
    #     src_root, f'{dst_root}/lib',
    #     src_dirs=[_get_dir(k) for k, v in conf['build']['attachments'].items()
    #               if 'dist_lib' in v]
    # )
    
    from .global_dirs import init_global_dirs
    init_global_dirs(src_root, f'{dst_root}/src')
    return src_root, dst_root


class DistTree:
    
    def __init__(self):
        self.paths = []  # type: list[str]
        #   note all elements in `self.paths` are directories. see
        #   implementation at `method:self.add_src_dirs`.
    
    def add_src_dirs(self, *paths: str):
        for p in paths:
            if p == '':
                continue
            else:
                self.paths.append(_get_dir(p))
            # lk.logt('[D1118]', p)
    
    def suggest_src_root(self):
        try:
            assert len(set(x.split(':', 1)[0] for x in self.paths)) == 1
            min_path = min(self.paths, key=lambda p: p.count('/'))
            return ospath.dirname(min_path)
        except AssertionError:
            return ''
    
    def build_dst_dirs(self, src_root: str, dst_root: str,
                       src_dirs=None):
        """

        Args:
            src_root: see `self.suggest_src_root:returns`
            dst_root:
            src_dirs: files which starts with `src_root`.
                None: use `self.paths` instead.
        """
        if src_dirs is None: src_dirs = self.paths
        assert ospath.exists(dst_root)
        
        # part 1.
        existed = {dst_root, }  # set
        
        def _mkdir(dir_):
            if dir_ not in existed:
                existed.add(dir_)
                if not ospath.exists(dir_):
                    lk.logt('[D0604]', 'creat empty folder', dir_)
                    mkdir(dir_)
        
        # part 2.
        from .global_dirs import global_dirs
        if src_root == '':
            get_dst_path = lambda src_path: \
                f'{dst_root}/{src_path.replace(":/", "/")}'
        else:
            get_dst_path = lambda src_path: \
                f'{dst_root}/{global_dirs.relpath(src_path, src_root)}'
        
        # part 3.
        src_dirs.sort()
        # lk.logp(self.paths)
        for src_path in src_dirs:
            dst_path = get_dst_path(src_path)
            _mkdir(dst_path)
        
        del existed

    def clear(self):
        self.paths.clear()


def _get_dir(path: str):
    if ospath.isfile(path):
        return ospath.dirname(path)
    else:
        return path
