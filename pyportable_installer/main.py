from os import path as ospath

from lk_logger import lk

from .no1_extract_pyproject import main as step1
from .no2_prebuild_pyproject import main as step2
from .no3_build_pyproject import main as step3
from .typehint import TConf, TMisc, TPath


class Misc:
    # 是否将 `./checkup/*` 中的工具拷贝到打包目录.
    create_checkup_tools = True
    # 是否创建启动器.
    create_launch_bat = True
    # 创建 venv 的方式.
    # 注: 该选项仅在用户在配置文件中启用 venv 时才有效.
    how_venv_created = 'copy'
    # 是否混淆源代码.
    compile_scripts = True
    # 是否做善后工作. 如是, 详见 `aftermath.py` 模块.
    do_aftermath = True
    # 是否打印详细信息. 默认是 False (关闭). 注意即使是 False, 也会打印原本应该
    # 打印的内容, 只是 False 状态不会打印 sourcemap 信息.
    log_verbose = False
    
    @classmethod
    def dump(cls) -> TMisc:
        # noinspection PyTypeChecker
        return {
            'create_checkup_tools': cls.create_checkup_tools,
            'create_launch_bat'   : cls.create_launch_bat,
            'how_venv_created'    : cls.how_venv_created,
            'compile_scripts'     : cls.compile_scripts,
            'do_aftermath'        : cls.do_aftermath,
            'log_verbose'         : cls.log_verbose,
        }


def full_build(file, **kwargs):
    Misc.create_checkup_tools = True
    Misc.create_launch_bat = True
    Misc.how_venv_created = 'copy'
    return main(file, kwargs, Misc.dump())


def min_build(file, **kwargs):
    Misc.create_checkup_tools = False
    Misc.create_launch_bat = True
    #   True (suggest) | False
    Misc.how_venv_created = 'empty_folder'
    #   'empty_folder' (suggest) | 'symbolink'
    return main(file, kwargs, Misc.dump())


def debug_build(file, **kwargs):
    Misc.create_checkup_tools = False
    Misc.create_launch_bat = True
    Misc.how_venv_created = 'symbolink'
    Misc.compile_scripts = False
    Misc.do_aftermath = False
    Misc.log_verbose = True
    return main(file, kwargs, Misc.dump())


def main(pyproj_file: TPath, additional_conf: dict, misc: TMisc) -> TConf:
    """
    几个关键目录的区分和说明: `../docs/devnote/difference-between-roots.md`
    """
    # TODO: temply commented
    if misc.get('log_verbose', False) is False:
        lk.lite_mode = True
    
    prj_conf = step1(pyproj_file, additional_conf)
    ________ = step2(prj_conf)  # 下划线只是为了让代码看起来整齐, 无实际意义
    dst_root = step3(prj_conf['app_name'], **prj_conf['build'], **misc)
    
    m, n = ospath.split(dst_root)
    lk.logt("[I2501]", f'See distributed project at \n\t"{m}:0" >> {n}')
    #   this path link is clickable in pycharm console  ^-----^
    
    if misc.get('do_aftermath', True):
        from .aftermath import main as do_aftermath
        do_aftermath(pyproj_file, prj_conf, dst_root)
    
    return prj_conf
