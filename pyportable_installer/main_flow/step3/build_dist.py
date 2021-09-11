from .step3_1 import main as step3_1
from .step3_2 import main as step3_2
from .step3_3 import main as step3_3
from ...typehint import *


def main(conf: TConf):
    """

    Project Structure Example:
        
        # from pyportable_installer.path_model src_model, dst_model
        
        hello_world_project # src_model.src_root
        |= hello_world      # src_model.prj_root
            |- main.py      # source project entry
        |= dist
            |= hello_world_1.0.0    # dst_model.dst_root
                |= build            # dst_model.build
                |= lib              # dst_model.lib
                |= src              # dst_model.src (aka. dst_model.prj_root)
                |= venv             # dst_model.venv
                |- ...
    """
    pyfiles = step3_1(conf)
    
    name = conf['build']['compiler']['name']
    options = conf['build']['compiler']['options'][name]
    step3_2(name, pyfiles, options)
    
    step3_3(conf['build'])


__all__ = ['main']
