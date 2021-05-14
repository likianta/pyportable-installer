from os import path as ospath


def pretty_path(p):
    return p.replace('\\', '/')


class GlobalDirs:
    """
    References:
        docs/devnote/difference-between-roots.md
    """
    src_root = ''
    dst_root = ''
    curr_dir = pretty_path(ospath.dirname(__file__))
    
    def local(self, rel_path: str):
        out = f'{self.curr_dir}/{rel_path}'
        assert ospath.exists(out)
        return out
    
    def template(self, rel_path: str):
        return self.local(f'template/{rel_path}')
    
    def to_dist(self, src_path: str):
        assert self.src_root and self.dst_root
        rel_path = self.relpath(src_path, self.src_root)
        return f'{self.dst_root}/{rel_path}'
    
    @staticmethod
    def relpath(path, start):
        return pretty_path(ospath.relpath(path, start))


def init_global_dirs(src_root, dst_root):
    """
    References:
        no2_prebuild_pyproject.py > func:main
    """
    global global_dirs
    global_dirs.src_root = src_root
    global_dirs.dst_root = dst_root


global_dirs = GlobalDirs()
