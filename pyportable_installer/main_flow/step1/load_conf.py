
from lk_utils.read_and_write import loads

from ...typehint import *


def load_conf(pyproj_file: TPath,
              addional_conf: Optional[TConf] = None) -> TConf:
    """

    Args:
        pyproj_file: see template at `~/pyportable_installer/template/pyproject
            .json`
        addional_conf: Optional[dict]. partial TConf.

    References:
        docs/pyproject-template.md
        docs/devnote/difference-between-roots.md > h2:pyproj_root
    """
    conf = loads(pyproj_file)
    if addional_conf:
        _update_additional_conf(conf, addional_conf)
    return conf


def _update_additional_conf(main_conf, additional):
    def _update(node: dict, subject: dict):
        for k, v in node.items():
            if isinstance(v, dict):
                _update(v, subject[k])
            elif isinstance(v, list):
                subject[k].extend(v)
            else:
                subject[k] = v
    
    _update(additional, main_conf)
    return main_conf
