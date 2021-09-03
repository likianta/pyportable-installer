import os.path

from lk_utils.filesniff import normpath


class PathFormatter:
    
    def __init__(self, dir_i, dir_o=None, fmt='abspath'):
        """

        Args:
            dir_i: TPath
            dir_o: Optional[TPath]
                if caller needs to process some paths containing keyword
                'dist:', this param cannot be omitted.
            fmt: Literal['abspath', 'relpath'].
                see abspath usages in `reformat_paths` and relpath usages
                in `aftermath.py:main`.
        """
        self.dir_i = dir_i
        self.dir_o = dir_o
        self.fmt = fmt
    
    def __call__(self, path: str):
        if path == '':
            return ''
        if 'dist:' in path:  # if path.startswith('dist:')
            return normpath(path.replace('dist:', self.dir_o + '/'))
        elif os.path.isabs(path):
            if self.fmt == 'abspath':
                return path
            else:
                return normpath(os.path.relpath(path, self.dir_i))
        else:
            if self.fmt == 'abspath':
                return normpath(os.path.abspath(f'{self.dir_i}/{path}'))
            else:
                return path
