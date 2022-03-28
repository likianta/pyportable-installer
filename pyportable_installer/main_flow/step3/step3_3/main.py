from .create_launcher import create_launcher
from .create_venv import create_venv
from ....typehint import TBuildConf


def main(build: TBuildConf):
    if build['venv']['enabled']:
        create_venv((m := build['venv']['mode']),
                    build['venv']['options'][m])
    create_launcher(build)
