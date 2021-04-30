from os import path as ospath

from lk_logger import lk
from lk_utils.read_and_write import loads

from .global_dirs import global_dirs, pretty_path


def main(pyproj_file: str):
    """

    Args:
        pyproj_file: see template at `../template/pyproject.json`

    References:
        docs/pyproject-template.md
        docs/devnote/difference-between-roots.md > h2:pyproj_root
    """
    pyproj_root = pretty_path(ospath.abspath(f'{pyproj_file}/../'))
    lk.loga(pyproj_root)
    
    conf = loads(pyproj_file)  # type: dict
    conf = _format_with_abspath(conf, PathFormatter(pyproj_root))
    
    return conf


def _format_with_abspath(conf: dict, path_fmt: 'PathFormatter'):
    # tip: read the following code together with `./template/pyproject.json`
    
    conf['build']['proj_dir'] = path_fmt(
        conf['build']['proj_dir']
    )
    conf['build']['dist_dir'] = path_fmt(
        conf['build']['dist_dir'].format(
            app_name=conf['app_name'],
            app_name_lower=conf['app_name'].lower().replace(' ', '_'),
            app_version=conf['app_version']
        )
    )
    conf['build']['icon'] = path_fmt(
        conf['build']['icon'] or
        ospath.abspath(global_dirs.template('python.ico'))
    )
    conf['build']['readme'] = path_fmt(
        conf['build']['readme']
    )
    
    conf['build']['target']['file'] = path_fmt(
        conf['build']['target']['file'].format(
            dist_dir=conf['build']['dist_dir']
        )
    )
    conf['build']['required']['venv'] = path_fmt(
        conf['build']['required']['venv']
    )
    
    conf['build']['module_paths'] = list(
        map(path_fmt, conf['build']['module_paths'])
    )
    conf['build']['attachments'] = {
        path_fmt(k): v
        for (k, v) in conf['build']['attachments'].items()
    }
    
    # from lk_utils.read_and_write import dumps
    # dumps(conf, '../tests/test.json')
    
    return conf


class PathFormatter:
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
    
    def __call__(self, path):
        if path == '':
            return ''
        elif len(path) > 1 and path[1] == ':':
            # FIXME: support only windows platform
            return pretty_path(path)
        else:
            return pretty_path(ospath.abspath(f'{self.root_dir}/{path}'))
