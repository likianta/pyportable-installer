import shutil

from pyportable_installer import full_build


def main():
    # _precheck()
    conf = full_build('pyproject.json')
    
    dir_i = '../../pyportable_installer/template/pyportable_crypto'
    dir_o = conf['build']['dist_dir'] + '/src/pyportable_installer/template/pyportable_crypto'
    shutil.rmtree(dir_o)
    shutil.copytree(dir_i, dir_o)


def _precheck():
    from pyportable_installer.main import Misc
    if Misc.log_level != 0:
        raise CheckFailed(Misc.log_level)


class CheckFailed(Exception):
    pass


if __name__ == '__main__':
    main()
