def _precheck():
    from pyportable_installer.main import Misc
    if Misc.log_level != 0:
        raise CheckFailed(Misc.log_level)


class CheckFailed(Exception):
    pass
