from os import path as ospath
from shutil import copyfile

from lk_logger import lk

from .no1_extract_pyproject import main as step1
from .no2_prebuild_pyproject import main as step2
from .no3_build_pyproject import main as step3


class Misc:
    # 是否将 `./checkup/*` 中的工具拷贝到打包目录.
    create_checkup_tools = True
    # 是否创建虚拟环境目录.
    # 该选项与项目配置中的 'enable_venv' 的区别在于, 'enable_venv' 决定了是否启
    # 用虚拟环境, 本选项决定了是否立即创建虚拟环境目录. 您可以选择启用虚拟环境但
    # 不立即创建目录 (考虑到第三方库体积较大的情况, 或者您在反复测试打包工作),
    # 稍后可通过手动复制/剪切/创建软链接等方式, 将自己事先准备好的虚拟环境添加到
    # 打包目录.
    create_venv_shell = True
    # 是否创建启动器.
    create_launch_bat = True
    # 是否混淆源代码.
    compile_scripts = True
    # 是否做善后工作. 如是, 详见 `aftermath.py` 模块.
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
    Misc.create_launch_bat = True  # suggest True
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
    ________ = step2(prj_conf)  # 这里用下划线作变量, 只是为了对齐, 使代码美观
    dst_root = step3(prj_conf['app_name'], **prj_conf['build'], **misc)
    
    m, n = ospath.split(dst_root)
    lk.logt("[I2501]", f'See distributed project at \n\t"{m}:0" >> {n}')
    #   this path link is clickable via pycharm console ^-----^
    
    copyfile(pyproj_file, f'{dst_root}/build/manifest.json')
    
    if misc.get('do_aftermath', True):
        from .aftermath import cleanup_files
        cleanup_files(dst_root, prj_conf)
