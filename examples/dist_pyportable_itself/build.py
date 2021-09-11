from pyportable_installer import full_build


def main():
    # _precheck()
    full_build('pyproject.json')


def _precheck():
    from pyportable_installer.main import Misc
    if Misc.log_level != 0:
        raise CheckFailed(Misc.log_level)
    
    # noinspection PyProtectedMember
    from pyportable_installer.path_model import _STAND_ALONE_MODE
    if _STAND_ALONE_MODE is False:
        raise CheckFailed('The "stand alone mode" should be turn on.')


class CheckFailed(Exception):
    pass


if __name__ == '__main__':
    main()
