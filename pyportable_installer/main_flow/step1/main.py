from os.path import abspath
from os.path import dirname

from lk_utils.filesniff import normpath

from .indexing_paths import indexing_paths
from .init_key_params import init_key_params
from .load_conf import load_conf
from .path_formatter import PathFormatter
from ...typehint import *


def main(pyproj_file: TPath,
         addional_conf: Optional[TConf] = None,
         path_format: TPathFormat = 'abspath',
         _skip_init_key_params=False) -> TConf:
    pyproj_file = normpath(abspath(pyproj_file))
    pyproj_dir = dirname(pyproj_file)
    print(pyproj_dir)
    
    conf = load_conf(pyproj_file, addional_conf)
    conf = indexing_paths(conf, PathFormatter(pyproj_dir, fmt=path_format))
    if _skip_init_key_params is False:
        init_key_params(conf, pyproj_file=pyproj_file, pyproj_dir=pyproj_dir)
    
    return conf
