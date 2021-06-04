from os import path as ospath

from lk_logger import lk
from lk_utils.read_and_write import loads

from .global_dirs import global_dirs, pretty_path
from .typehint import *


def main(pyproj_file: str) -> TConf:
    """

    Args:
        pyproj_file: see template at `./template/pyproject.json`

    References:
        docs/pyproject-template.md
        docs/devnote/difference-between-roots.md > h2:pyproj_root
    """
    pyproj_root = pretty_path(ospath.dirname(pyproj_file))
    lk.loga(pyproj_root)
    
    conf = loads(pyproj_file)  # type: TConf
    conf = reformat_paths(conf, PathFormatter(pyproj_root))
    
    return conf


def reformat_paths(conf: TConf, path_fmt: 'PathFormatter'):
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
    
    conf['build']['attachments'] = {
        path_fmt(k): path_fmt(v) if 'dist:' in v else v
        for (k, v) in conf['build']['attachments'].items()
    }
    
    conf['build']['module_paths'] = list(
        map(path_fmt, conf['build']['module_paths'])
    )
    
    # --------------------------------------------------------------------------
    
    options = conf['build']['venv']['options']
    
    options['source_venv']['path'] = path_fmt(
        options['source_venv']['path']
    )
    
    options['pip']['local'] = path_fmt(
        options['pip']['local']
    )
    
    if isinstance((x := options['depsland']['requirements']), str):
        options['depsland']['requirements'] = path_fmt(x)
    
    if isinstance((x := options['pip']['requirements']), str):
        options['pip']['requirements'] = path_fmt(x)
    
    # from lk_utils.read_and_write import dumps
    # dumps(conf, '../tests/test.json')
    
    return conf


class PathFormatter:
    
    def __init__(self, root_dir, refmt_to='abspath'):
        self.root_dir = root_dir
        self.refmt_to = refmt_to
    
    def _refmt_to_abspath(self, path: str):
        if path == '':
            return ''
        elif 'dist:root' in path:
            return pretty_path(path.replace('dist:root', 'dist:'))
        elif 'dist:' in path:
            return pretty_path(path)
        elif len(path) > 1 and path[1] == ':':
            # FIXME: support only windows platform
            return pretty_path(path)
        else:
            return pretty_path(ospath.abspath(f'{self.root_dir}/{path}'))
    
    def _refmt_to_relpath(self, path: str):
        if path == '':
            return ''
        elif 'dist:root' in path:
            return pretty_path(path.replace('dist:root', 'dist:'))
        elif 'dist:' in path:
            return pretty_path(path)
        elif len(path) > 1 and path[1] == ':':
            # FIXME: support only windows platform
            return pretty_path(ospath.relpath(path, self.root_dir))
        else:
            return path
    
    def __call__(self, path: str):
        if self.refmt_to == 'abspath':
            return self._refmt_to_abspath(path)
        else:
            return self._refmt_to_relpath(path)
