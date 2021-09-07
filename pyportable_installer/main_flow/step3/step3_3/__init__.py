"""
See demonstration in '~/pyportable_installer/main_flow/__init__.py'.
"""
from . import create_launcher
from . import create_venv
from ....typehint import TBuildConf


def main(build: TBuildConf):
    if build['venv']['enable_venv']:
        create_venv.main((m := build['venv']['mode']),
                         build['venv']['options'][m])
    create_launcher.main(build)


__all__ = ['main']
