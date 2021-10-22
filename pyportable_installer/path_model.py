import os
import os.path as xpath
from uuid import uuid1

from lk_logger import lk
from lk_utils.filesniff import normpath

from ._env import ASSETS_ENTRY  # str['STANDALONE', 'PACKAGE']

lk.logt('[D2952]', ASSETS_ENTRY)


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
    cur_root = normpath(xpath.dirname(__file__))
    
    if ASSETS_ENTRY == 'STANDALONE':
        prj_root = xpath.dirname(cur_root)
    else:
        prj_root = f'{cur_root}/assets'
    
    # prj_root/*
    dist = f'{prj_root}/dist'
    lib = f'{prj_root}/lib'
    temp = f'{prj_root}/temp'
    
    # prj_root/lib/*
    temp_lib = f'{lib}/temp_lib'
    
    # cur_root/*
    checkup = f'{cur_root}/checkup'
    template = f'{cur_root}/template'
    
    # cur_root/template/*
    launch_bat = f'{template}/launch.bat'
    pyarmor = f'{template}/pyarmor'
    pylauncher = f'{template}/pylauncher.txt'
    pyproject = f'{template}/pyproject.json'
    python_ico = f'{template}/python.ico'
    pytransform = f'{template}/pytransform.txt'
    
    # cur_root/template/depsland/*
    _depsland = f'{template}/depsland'
    depsland_launcher_part_a = f'{_depsland}/launcher_part_a.bat'
    depsland_launcher_part_b = f'{_depsland}/launcher_part_b.bat'
    depsland_setup_part_a = f'{_depsland}/setup_part_a.bat'
    depsland_setup_part_b = f'{_depsland}/setup_part_b.txt'
    
    # other
    accessory = f'{cur_root}/compilers/accessory'
    bat_2_exe_converter = f'{cur_root}/bat_2_exe/bat_to_exe_converter.exe'
    cythonize_required_packages_for_python3 = \
        f'{accessory}/cythonize_required_packages_for_python3.zip'
    
    # --------------------------------------------------------------------------
    
    def build_dirs(self):
        if ASSETS_ENTRY == 'STANDALONE':
            assert xpath.exists(self.dist)
            assert xpath.exists(self.lib)
            assert xpath.exists(self.temp_lib)
            assert xpath.exists(self.temp)
        else:
            if not xpath.exists(self.prj_root):
                os.mkdir(self.prj_root)
                os.mkdir(self.dist)
                os.mkdir(self.lib)
                os.mkdir(self.temp_lib)
                os.mkdir(self.temp)
        
        if not xpath.exists(self.temp_lib):
            os.mkdir(self.temp_lib)
        elif os.listdir(self.temp_lib):
            from shutil import rmtree
            rmtree(self.temp_lib)
            os.mkdir(self.temp_lib)
    
    def create_temp_dir(self):
        _temp_dir = f'{self.temp}/{uuid1()}'
        lk.loga('make temporary dir', _temp_dir)
        os.mkdir(_temp_dir)
        return _temp_dir
    
    def get_pyportable_crypto_trial_package(
            self, pyversion, assert_exists=True
    ):
        out = '/'.join((
            self.accessory,
            f'pyportable_crypto_trial_{pyversion}',
            'pyportable_crypto'
        ))
        if assert_exists:
            assert xpath.exists(out), '''
                Currently your requested [python_version][1] is not on the
                [supported trial-list][2].
                Please try the following options to resolve your problem:
                    a) Prompt your requested python_version to "3.8" or "3.9";
                    b) Use a custom pyportable_crypto key instead of trial key;
                       Note: you need to install Microsoft Visual Studio C++
                             Build Tools (2019) on your system.
                    c) Contact pyportable_installer project owner to extend
                       trial keys for requested [python_version][1].
                
                [1]: {0}
                [2]: {1}
            '''.format(
                pyversion,
                f'{self.accessory}/pyportable_crypto_trial_*'
            )
        return out


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
