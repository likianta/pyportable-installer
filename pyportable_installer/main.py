from shutil import copyfile
from os import path as ospath

from lk_logger import lk

from .no1_extract_pyproject import main as step1
from .no2_prebuild_pyproject import main as step2
from .no3_build_pyproject import main as step3


class Misc:
    # 对于一些修改较为频繁, 但用途很小的参数, 放在了这里. 您可以按需修改
    # 使用 Pycharm 的搜索功能查看它在哪里被用到
    create_checkup_tools = True  # True|False
    #   如果您在实现增量更新 (仅发布 src 文件夹), 请设为 False
    create_venv_shell = True
    #   如果您在实现增量更新 (仅发布 src 文件夹), 请设为 False
    create_launch_bat = True  # True|False
    compile_scripts = True
    do_aftermath = True
    
    @classmethod
    def dump(cls):
        return {
            'create_checkup_tools': cls.create_checkup_tools,
            'create_venv_shell'   : cls.create_venv_shell,
            'create_launch_bat'   : cls.create_launch_bat,
            'compile_scripts'     : cls.compile_scripts,
            'do_aftermath'        : cls.do_aftermath,
        }


def full_build(pyproj_file):
    Misc.create_checkup_tools = True
    Misc.create_venv_shell = True
    Misc.create_launch_bat = True
    main(pyproj_file, Misc.dump())


def min_build(file):
    Misc.create_checkup_tools = False
    Misc.create_venv_shell = False
    Misc.create_launch_bat = True  # True(suggest)|False
    main(file, Misc.dump())


def debug_build(file):
    Misc.create_checkup_tools = False
    Misc.create_venv_shell = False
    Misc.create_launch_bat = True
    Misc.compile_scripts = False
    Misc.do_aftermath = False
    main(file, Misc.dump())


def main(pyproj_file: str, misc: dict):
    """
    几个关键目录的区分和说明: `docs/devnote/difference-between-roots.md`
    """
    prj_conf = step1(pyproj_file)
    ________ = step2(prj_conf)
    dst_root = step3(prj_conf['app_name'], **prj_conf['build'], **misc)
    
    m, n = ospath.split(dst_root)
    lk.logt("[I2501]", f'See distributed project at \n\t"{m}:0" >> {n}')
    #   this path link is clickable via pycharm console ^-----^
    
    copyfile(pyproj_file, f'{dst_root}/build/manifest.json')
    
    if misc.get('do_aftermath', True):
        from .aftermath import cleanup_files
        cleanup_files(dst_root, prj_conf)
