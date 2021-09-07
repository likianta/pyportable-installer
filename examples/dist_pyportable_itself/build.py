from pyportable_installer import full_build


def main():
    # _precheck()
    full_build('pyproject.json')


def _precheck():
    from pyportable_installer.main import Misc
    if Misc.log_level != 0:
        raise CheckFailed(Misc.log_level)


class CheckFailed(Exception):
    pass


if __name__ == '__main__':
    main()
