from os.path import dirname
from os.path import relpath as _relpath

from lk_utils.filesniff import normpath


def src_2_dst(src_path, src_dir='', dst_dir=''):
    if not src_path: return ''
    
    if not src_dir: src_dir = src_model.src_root
    if not dst_dir: dst_dir = dst_model.src_root
    
    p = relpath(src_path, src_dir)
    p = f'{dst_dir}/{p}'
    return p


def relpath(path, start):
    return normpath(_relpath(path, start))


class PyPortablePathModel:
    cur_root = normpath(dirname(__file__))
    prj_root = dirname(cur_root)
    
    # prj_root/*
    temp = f'{prj_root}/temp'
    
    # cur_root/*
    checkup = f'{cur_root}/checkup'
    template = f'{cur_root}/template'
    
    # template/*
    launch_bat = f'{template}/launch.bat'
    launch_bat_for_depsland = f'{template}/launch_for_depsland.bat'
    pyarmor = f'{template}/pyarmor'
    pylauncher = f'{template}/pylauncher.txt'
    pyproject = f'{template}/pyproject.json'
    python_ico = f'{template}/python.ico'
    pytransform = f'{template}/pytransform.txt'
    setup_for_depsland = f'{template}/setup_for_depsland.txt'
    
    # specific files
    bat_2_exe_converter = f'{cur_root}/bat_2_exe/bat_to_exe_converter.exe'
    py_2_pyd = f'{cur_root}/compiler/py_2_pyd.bat'


class SourcePathModel:
    src_root = None
    prj_root = None
    
    # noinspection PyAttributeOutsideInit
    def init(self, src_root, prj_root, **kwargs):
        self.src_root = src_root
        self.prj_root = prj_root
        
        self.readme = kwargs.get('readme', '')
    
    def assert_ready(self):
        assert self.src_root and self.prj_root


class DistributedPathModel:
    """
    Tree:
        dist
        |= hello_world_0.1.0    # dst_root
        |                       # ↑ this node concept doesn't exist in `src_model`
            |= src              # src_root
            |                   # ↑ this is correspondent to `src_model.src_root`
                |= hello_world  # prj_root
                |               # ↑ this is correspondent to `src_model.prj_root`
                    |- main.py
                |- pylauncher.py
    """
    dst_root = None
    src_root = None
    prj_root = None
    
    # noinspection PyAttributeOutsideInit
    def init(self, dst_root: str, prj_relroot: str, **kwargs):
        self.dst_root = dst_root
        self.src_root = f'{self.dst_root}/src'
        self.prj_root = f'{self.src_root}/{prj_relroot}'
        #   prj_relroot: came from
        #       `relpath(src_model.prj_root, src_model.src_root)`
        
        # prj_root/*
        self.pylauncher = f'{self.src_root}/pylauncher.py'
        self.pylauncher_conf = f'{self.src_root}/.pylauncher_conf'
        
        # dst_root/*
        self.build = f'{self.dst_root}/build'
        self.lib = f'{self.dst_root}/lib'
        self.setup_bat = f'{self.dst_root}/setup.bat'
        self.src = f'{self.dst_root}/src'
        self.venv = f'{self.dst_root}/venv'
        
        # dst_root/*/*
        self.manifest = f'{self.build}/manifest.json'
        self.python = f'{self.venv}/python.exe'
        self.setup_py = f'{self.build}/setup.py'
        
        # kwargs
        launcher_name = kwargs['launcher_name']
        self.launcher_bat = f'{self.dst_root}/{launcher_name}.bat'
        self.launcher_exe = f'{self.dst_root}/{launcher_name}.exe'
        self.readme = src_2_dst(kwargs.get('readme', ''))
    
    def assert_ready(self):
        assert self.dst_root and self.src_root and self.prj_root


prj_model = PyPortablePathModel()
src_model = SourcePathModel()
dst_model = DistributedPathModel()

__all__ = [
    'src_2_dst', 'relpath',
    'prj_model', 'src_model', 'dst_model'
]
