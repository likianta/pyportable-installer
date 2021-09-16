import sys

current_pyversion = "python{}{}".format(
    sys.version_info.major, sys.version_info.minor
)
target_pyversion = "python38"
if current_pyversion != target_pyversion:
    raise Exception(
        "Python interpreter version doesn't matched!",
        "Required: {}, got {} ({})".format(
            target_pyversion, current_pyversion, sys.executable
        )
    )

from .encrypt import encrypt_data, encrypt_file
from .inject import inject

__version__ = "0.2.0-trial"

