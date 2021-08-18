from os import mkdir, makedirs
from os import path as ospath

from lk_logger import lk

from .typehint import *


def main(conf: TConf):
    """ Create dist-side tree (all empty folders under `dist_root`) """
    _precheck(conf)
    
    # create build_dir, lib_dir, src_dir
    mkdir(conf['build']['dist_dir'])
    mkdir(conf['build']['dist_dir'] + '/build')
    mkdir(conf['build']['dist_dir'] + '/lib')
    mkdir(conf['build']['dist_dir'] + '/src')
    
    dist_tree = DistTree()
    
    """
    Add to source dirs: 对相对路径敏感的目录需要保持原有的目录结构关系. 它们需要
    被加入到 source dirs. 如下所列 (见加号标识):
        pyproject
            build
                + proj_dir
                target
                    + file
                + attachments
                
    Do not add to source dirs (见减号标识):
        pyproject
            build
                - dist_dir
                - icon
                - readme
                - module_paths
    """
    dist_tree.add_src_dirs(
        conf['build']['proj_dir'],
        conf['build']['target']['file'],
        # *conf['build']['attachments'].keys(),
        *(k for k, v in conf['build']['attachments'].items() if v['path'] == ''),
        # *filter(
        #     None, (v['path'] for v in conf['build']['attachments'].values())),
    )
    
    src_root = dist_tree.suggest_src_root()
    lk.loga(src_root)
    dst_root = conf['build']['dist_dir']
    dist_tree.build_dst_dirs(src_root, f'{dst_root}/src')
    
    from .global_dirs import init_global_dirs
    init_global_dirs(src_root, f'{dst_root}/src')
    return src_root, dst_root


def _precheck(conf: TConf):
    assert not ospath.exists(conf['build']['dist_dir']), (
        'The target distribution directory already exists, please assign '
        'another (non-existent) folder to distribute.'
    )
    
    # from .global_dirs import curr_dir
    # if not ospath.exists(f'{curr_dir}/template/pytransform'):
    #     from os import popen
    #     popen('pyarmor runtime -O "{}"'.format(f'{curr_dir}/template')).read()
    
    if conf['build']['venv']['enable_venv']:
        from .embed_python import EmbedPythonManager
        builder = EmbedPythonManager(
            pyversion=conf['build']['venv']['python_version']
        )
        # try to get a valid embed python path, if failed, this method will
        # raise an exception to terminate process.
        builder.get_embed_python_dir()
        
        mode = conf['build']['venv']['mode']
        if mode == 'source_venv':
            if venv_path := conf['build']['venv']['options'][mode]['path']:
                if venv_path.startswith(src_path := conf['build']['proj_dir']):
                    lk.logt('[W2015]', f'''
                        Please do not put the Python virtual environment folder
                        in your source code folder! This will make the third-
                        party libraries to be encrypted, which usually leads to
                        unpredicatable errors.
                        You can put venv aside with the source code dir, this
                        is the recommended parctice.
                        
                        Current venv dir: {venv_path}
                        Suggest moved to: {ospath.dirname(src_path)}/venv
                    ''')
                    if input('Continue the process? (y/n): ').lower() != 'y':
                        raise SystemExit


class DistTree:
    
    def __init__(self):
        self.paths = []  # type: list[str]
        #   note all elements in `self.paths` are directories. see
        #   implementation in `method:self.add_src_dirs`.
    
    def add_src_dirs(self, *paths: str):
        for p in paths:
            if p:
                assert ospath.exists(p)
                self.paths.append(_get_dir(p))
                # lk.logt('[D1118]', p)
    
    def suggest_src_root(self):
        try:
            assert len(set(x.split(':', 1)[0] for x in self.paths)) == 1
            min_path = min(self.paths, key=lambda p: p.count('/'))
            return ospath.dirname(min_path)
        except AssertionError:
            return ''
    
    def build_dst_dirs(self, src_root: str, dst_root: str, src_dirs=None):
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
                    # mkdir(dir_)
                    makedirs(dir_)
        
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
        lk.logp(self.paths)
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
