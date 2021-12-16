import os
import os.path as xpath

from lk_logger import lk
from lk_utils.filesniff import currdir
from lk_utils.filesniff import normpath

from ._env import ASSETS_ENTRY  # str['STANDALONE', 'PACKAGE']

lk.logt('[D2952]', ASSETS_ENTRY)

_cur_dir = currdir()


def src_2_dst(src_path, src_dir='', dst_dir=''):
    if not src_path:
        return ''
    if src_path.startswith('dist:'):
        return src_path.replace('dist:', dst_model.dst_root)
    
    if not src_dir: src_dir = src_model.src_root
    if not dst_dir: dst_dir = dst_model.src_root
    
    p = relpath(src_path, src_dir)
    p = f'{dst_dir}/{p}'
    return p


def relpath(path, start):
    if not path:
        return ''
    return normpath(xpath.relpath(path, start))


class PyPortablePathModel:
    # current dir based
    cur_root = _cur_dir
    # lk.logt('[D0957]', cur_root)
    
    (
        bat_2_exe_converter,
        checkup,
        template,
    ) = (
        f'{cur_root}/bat_2_exe/bat_to_exe_converter.exe',
        f'{cur_root}/checkup',
        f'{cur_root}/template',
    )
    
    (
        compilers_lib,
        pyportable_runtime_py38,
        pyportable_runtime_py39,
        pyportable_runtime_py310,
        pyportable_runtime_py38_linux,
    ) = (
        f'{cur_root}/compilers/lib',
        f'{cur_root}/compilers/lib/pyportable_runtime_py38/pyportable_runtime',
        f'{cur_root}/compilers/lib/pyportable_runtime_py39/pyportable_runtime',
        f'{cur_root}/compilers/lib/pyportable_runtime_py310/pyportable_runtime',
        f'{cur_root}/compilers/lib/linux/pyportable_runtime_py38/pyportable_runtime',
    )
    
    (
        launch_bat,
        pyarmor,
        pylauncher,
        pyproject,
        python_ico,
        pytransform,
    ) = (
        f'{cur_root}/template/launch.bat',
        f'{cur_root}/template/pyarmor',
        f'{cur_root}/template/pylauncher.txt',
        f'{cur_root}/template/pyproject.json',
        f'{cur_root}/template/python.ico',
        f'{cur_root}/template/pytransform.txt',
    )
    
    (
        depsland_launcher_part_a,
        depsland_launcher_part_b,
        depsland_setup_part_a,
        depsland_setup_part_b,
    ) = (
        f'{cur_root}/template/depsland/launcher_part_a.bat',
        f'{cur_root}/template/depsland/launcher_part_b.bat',
        f'{cur_root}/template/depsland/setup_part_a.bat',
        f'{cur_root}/template/depsland/setup_part_b.txt',
    )
    
    # --------------------------------------------------------------------------
    # project root
    
    if ASSETS_ENTRY == 'STANDALONE':
        prj_root = xpath.dirname(cur_root)
    else:
        prj_root = f'{cur_root}/assets'
    
    (
        dist,
        # lib,
        temp,
    ) = (
        f'{prj_root}/dist',
        # f'{prj_root}/lib',
        f'{prj_root}/temp',
    )
    
    # --------------------------------------------------------------------------
    
    def build_dirs(self):
        if ASSETS_ENTRY == 'STANDALONE':
            assert xpath.exists(self.dist)
            assert xpath.exists(self.temp)
        else:
            if not xpath.exists(self.prj_root):
                os.mkdir(self.prj_root)
                os.mkdir(self.dist)
                os.mkdir(self.temp)
    
    def create_temp_dir(self):
        from secrets import token_urlsafe
        _temp_dir = f'{self.temp}/{token_urlsafe()}'
        lk.loga('make temporary dir', _temp_dir)
        os.mkdir(_temp_dir)
        return _temp_dir


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
        self.src = f'{self.dst_root}/src'
        self.venv = f'{self.dst_root}/venv'
        
        # dst_root/*/*
        self.manifest = f'{self.build}/manifest.json'
        self.python = f'{self.venv}/python.exe'
        
        # other: depsland
        self.depsland_setup_part_a = f'{self.dst_root}/setup.bat'
        self.depsland_setup_part_b = f'{self.build}/setup.py'
        
        # other: kwargs
        launcher_name = kwargs['launcher_name']
        self.launcher_bat = f'{self.dst_root}/{launcher_name}.bat'
        self.launcher_exe = f'{self.dst_root}/{launcher_name}.exe'
        self.readme = src_2_dst(kwargs.get('readme', ''))
    
    def assert_ready(self):
        assert self.dst_root and self.src_root and self.prj_root


prj_model = PyPortablePathModel()
src_model = SourcePathModel()
dst_model = DistributedPathModel()

prj_model.build_dirs()

__all__ = [
    'src_2_dst', 'relpath',
    'prj_model', 'src_model', 'dst_model'
]
