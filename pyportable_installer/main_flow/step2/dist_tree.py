from os import makedirs
from os.path import dirname
from os.path import exists
from os.path import isfile
from os.path import relpath

from lk_logger import lk
from lk_utils.filesniff import normpath


class DistTree:
    
    def __init__(self):
        self.paths = []  # type: list[str]
        #   note all elements in `self.paths` are directories. see
        #   implementation in `method:self.add_src_dirs`.
    
    def add_src_dirs(self, *paths: str):
        for p in filter(None, paths):
            assert exists(p), (
                'Source path doesn\'t exist, you may check path spelling '
                'in your pyproject file', p
            )
            self.paths.append(_get_dir(p))
    
    def suggest_src_root(self):
        try:  # check whether paths are from one hard driver.
            # FIXME: this scheme is only available in Windows platform.
            assert len(set(x.split(':', 1)[0] for x in self.paths)) == 1
        except AssertionError:
            return ''
        else:
            minimal_common_path = min(self.paths, key=lambda p: p.count('/'))
            return dirname(minimal_common_path)
    
    def build_dst_dirs(self, src_root: str, dst_root: str, src_dirs=None):
        """

        Args:
            src_root: see `self.suggest_src_root:returns`. note that the
                `src_root` maybe empty. (the caller doesn't need to do
                anything for it, we will take care of this case.)
            dst_root:
            src_dirs: files which starts with `src_root`.
                None: use `self.paths` instead.
        """
        assert exists(src_root) and exists(dst_root)
        if src_dirs is None:
            src_dirs = self.paths
        
        # part 1.
        existed = {dst_root, }  # set
        
        def _mkdir(dir_):
            if dir_ not in existed:
                existed.add(dir_)
                if not exists(dir_):
                    lk.logt('[D0604]', 'creat empty folder', dir_)
                    # mkdir(dir_)
                    makedirs(dir_)
        
        # part 2.
        if src_root == '':
            # FIXME: this is only available in Windows platform.
            src_2_dst = lambda src_path: \
                f'{dst_root}/{src_path.replace(":/", "/")}'
        else:
            src_2_dst = lambda src_path: \
                f'{dst_root}/{normpath(relpath(src_path, src_root))}'
        
        # part 3.
        src_dirs.sort()
        lk.logp(self.paths)
        for src_path in src_dirs:
            dst_path = src_2_dst(src_path)
            _mkdir(dst_path)
        
        del existed
    
    def clear(self):
        self.paths.clear()


def _get_dir(path: str):
    if isfile(path):
        return dirname(path)
    else:
        return path
