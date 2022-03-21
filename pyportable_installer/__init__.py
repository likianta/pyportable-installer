import lk_logger

lk_logger.setup(show_varnames=True)

from .main import debug_build
from .main import full_build
from .main import min_build

__version__ = '4.3.1'
