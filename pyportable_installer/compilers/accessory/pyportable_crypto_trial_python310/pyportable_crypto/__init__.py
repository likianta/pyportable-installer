import sys

current_pyversion = "python{}{}".format(
    sys.version_info.major, sys.version_info.minor
)
target_pyversion = "python310"
if current_pyversion != target_pyversion:
    raise Exception(
        "Python interpreter version doesn't matched!",
        "Required: {}, got {} ({})".format(
            target_pyversion, current_pyversion, sys.executable
        )
    )

__version__ = "0.2.1-trial"

from .inject import inject
from .inject import encrypt_data

