encrypt = None
decrypt = None


def _init_check():
    import sys

    current_pyversion = sys.version_info[:2]  # type: tuple
    target_pyversion = (3, 10)
    if current_pyversion != target_pyversion:
        raise Exception(
            "Python interpreter version doesn't matched!",
            "Required: Python {}, got {} ({})".format(
                ', '.join(map(str, target_pyversion)),
                ', '.join(map(str, current_pyversion)),
                sys.executable
            )
        )


_init_check()
del _init_check

from .cipher import decrypt  # noqa
from .cipher import encrypt  # noqa

__version__ = '1.0.0'
