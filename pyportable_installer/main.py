from os import path as ospath

from lk_logger import lk

from . import main_flow
from .typehint import TConf
from .typehint import TMisc
from .typehint import TPath


class Misc:
    # whether to copy checkup tools (`~/pyportable_installer/checkup`) to dist
    # dir.
    copy_checkup_tools = True
    # whether to create launcher file (exe format).
    create_launch_bat = True
    # how to create venv.
    # note: this option only effects when user enables venv in config file.
    how_venv_created = 'copy'
    # whether to obfuscate source code.
    obfuscate_source_code = True
    # whether to do aftermath work. see `aftermath.py`.
    do_aftermath = True
    # how to print messages when pyportable-installer is processing.
    #   0: disable print function.
    #   1: print main messages (i.e. the built-in `print` behavior).
    #   2: print messages with sourcemap (i.e. default `lk-logger` behavior).
    #   suggestion:
    #       for pyportable-installer self distribution package, set to 0;
    #       for pyportable-installer open source package, set to 1 (default);
    #       for developing and debugging pyportable-installer project, set to 2.
    log_level = 2
    
    @classmethod
    def dump(cls) -> TMisc:
        # noinspection PyTypeChecker
        return {
            'copy_checkup_tools'   : cls.copy_checkup_tools,
            'create_launch_bat'    : cls.create_launch_bat,
            'how_venv_created'     : cls.how_venv_created,
            'obfuscate_source_code': cls.obfuscate_source_code,
            'do_aftermath'         : cls.do_aftermath,
            'log_level'            : cls.log_level,
        }


def full_build(file, additional_conf=None):
    Misc.copy_checkup_tools = True
    Misc.create_launch_bat = True
    Misc.how_venv_created = 'copy'
    return main(file, additional_conf or {}, Misc.dump())


def min_build(file, additional_conf=None):
    Misc.copy_checkup_tools = False
    Misc.create_launch_bat = True
    #   True (suggest) | False
    Misc.how_venv_created = 'empty_folder'
    #   'empty_folder' (suggest) | 'symbolink'
    return main(file, additional_conf or {}, Misc.dump())


def debug_build(file, additional_conf=None):
    Misc.copy_checkup_tools = False
    Misc.create_launch_bat = True
    Misc.how_venv_created = 'symbolink'
    Misc.obfuscate_source_code = False
    Misc.do_aftermath = False
    Misc.log_verbose = True
    
    if additional_conf is None:
        additional_conf = {'build': {'compiler': {
            'name': '_no_compiler',
            'options': {'_no_compiler': {}}
        }}}
    else:
        node = additional_conf.setdefault('build', {})
        node = node.setdefault('compiler', {})
        node['name'] = '_no_compiler'
        node = node.setdefault('options', {})
        node['_no_compiler'] = {}

    return main(file, additional_conf, Misc.dump())


def main(pyproj_file: TPath, additional_conf: dict, misc: TMisc) -> TConf:
    """
    Args:
        pyproj_file: basic configurations in 'pyproject.json'.
        additional_conf: partial congurations to override the basic one's. you
            can pass some dynamic configurations through a build script, this
            is convenient for developers to customize their own dist flow in a
            flexible way, which convers the shortage of using static pyproject
            file.
        misc:
    
    References:
        '~/docs/devnote/difference-between-roots.md'
    """
    lvl = misc.get('log_level', 0)
    if lvl == 0:
        lk.disable()
    elif lvl == 1:
        lk.enable_lite_mode()
    
    conf = main_flow.main(pyproj_file, additional_conf, **misc)
    
    m, n = ospath.split(conf['build']['dist_dir'])
    lk.logt("[I2501]", f'See distributed project at: \n\t"{m}:0" >> {n}')
    #   this path link is clickable in pycharm console   ^-----^
    
    lk.enable()
    
    return conf
