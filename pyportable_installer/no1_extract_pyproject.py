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
        """
        
        Args:
            root_dir:
            refmt_to: literal['abspath', 'relpath'].
                see abspath usages in `reformat_paths` and relpath usages
                in `aftermath.py:main`.
        """
        self.root_dir = root_dir
        self.refmt_to = refmt_to
    
    def __call__(self, path: str):
        if path == '':
            return ''
        elif 'dist:' in path:
            # related:
            #   `../assets_copy.py:copy_assets:[code]if mark[-1].startswith(
            #       'dist:'):[vars]path_o_root`
            #   `../no3_build_pyproject.py:_create_launcher:[vars]
            #       extend_sys_paths`
            if 'dist:root' not in path:
                path = path.replace('dist:', 'dist:root/')  # <──┐
            ''' 'dist:root'     ->  'dist:root'           │
                'dist:lib'      ->  'dist:root/lib' ──────┘
                'dist:root/lib' ->  'dist:root/lib'
            '''
            return pretty_path(path)
        elif len(path) > 1 and path[1] == ':':
            # FIXME: support only windows platform
            if self.refmt_to == 'abspath':
                return path
            else:
                return pretty_path(ospath.relpath(path, self.root_dir))
        else:
            if self.refmt_to == 'abspath':
                return pretty_path(ospath.abspath(f'{self.root_dir}/{path}'))
            else:
                return path
