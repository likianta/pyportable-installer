from os import path as ospath

from lk_logger import lk
from lk_utils.read_and_write import loads

from .global_dirs import global_dirs, pretty_path
from .typehint import *


def main(pyproj_file: str, **kwargs) -> TConf:
    """

    Args:
        pyproj_file: see template at `./template/pyproject.json`

    Keyword Args:
        refmt_to: Literal['abspath', 'relpath']

    References:
        docs/pyproject-template.md
        docs/devnote/difference-between-roots.md > h2:pyproj_root
    """
    pyproj_root = pretty_path(ospath.dirname(ospath.abspath(pyproj_file)))
    lk.loga(pyproj_root)
    
    conf = loads(pyproj_file)  # type: TConf
    conf = reformat_paths(
        conf, PathFormatter(
            pyproj_root, refmt_to=kwargs.get('refmt_to', 'abspath')
        )
    )
    
    return conf


def reformat_paths(conf: TConf, path_fmt: Union['PathFormatter', Callable]):
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
    
    # note: `conf['build']['attachments']` and `conf['build']['module_paths']`
    # requires processing keyword paths (dist:xxx), so `path_fmt.dir_o` needs
    # to be defined.
    path_fmt.dir_o = conf['build']['dist_dir']
    
    temp = {}  # type: TAttachments
    for k, v in conf['build']['attachments'].items():
        # lk.logt('[D0510]', k, v)
        k = path_fmt(k)
        v = v.split(',')  # type: list[str]
        if v[-1].startswith('dist:'):
            assert len(v) > 1, (conf['build']['attachments'], k, v)
            path = path_fmt(v[-1].format(name=ospath.basename(k)))
            temp[k] = {'marks': tuple(v[:-1]), 'path': path}
        else:
            temp[k] = {'marks': tuple(v), 'path': ''}
    conf['build']['attachments'] = temp
    
    # PERF: 目前的设计是, `conf['build']['module_paths']` 同时支持来自 src_root
    # 的路径和 dst_root 的路径 (这意味着 module_paths 接受 `dist:xxx` 关键词路
    # 径), 在 `no3_build_pyproject.py > _create_launcher > extend_sys_paths` 中
    # 兼容实现.
    # 这种设计兼容性强, 但不太规范, 后面会考虑改变设计.
    # 备忘: 基于 dst_root 的路径是不可忽略的, 因为某些情况 src_root 下不能提供所
    # 需的自定义的 (可以是事先不存在的) 路径.
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
    
    def __init__(self, dir_i, dir_o=None, refmt_to='abspath'):
        """
        
        Args:
            dir_i: TPath
            dir_o: Optional[TPath]
                if caller needs to process some paths containing keyword
                'dist:', this param cannot be omitted.
            refmt_to: Literal['abspath', 'relpath'].
                see abspath usages in `reformat_paths` and relpath usages
                in `aftermath.py:main`.
        """
        self.dir_i = dir_i
        self.dir_o = dir_o
        self.refmt_to = refmt_to
    
    def __call__(self, path: str):
        if path == '':
            return ''
        if 'dist:' in path:  # if path.startswith('dist:')
            return pretty_path(path.replace('dist:', self.dir_o + '/'))
        elif ospath.isabs(path):
            if self.refmt_to == 'abspath':
                return path
            else:
                return pretty_path(ospath.relpath(path, self.dir_i))
        else:
            if self.refmt_to == 'abspath':
                return pretty_path(ospath.abspath(f'{self.dir_i}/{path}'))
            else:
                return path
