from os.path import basename
from uuid import uuid1

from .path_formatter import PathFormatter
from ...path_model import prj_model
from ...typehint import *


def indexing_paths(conf: TConf, path_fmt: Union[PathFormatter, Callable]):
    """
    Args:
        conf
        path_fmt:
            - PathFormatter: map path node from dir_i to dir_o.
                - the default dir_i is dirname of pyproj_file.
                - the default dir_o is dist dir from conf['build']['dist_dir'].
            - Callable: receives one argument as path_i, returns path_o. the
                typical pattern is: `lambda path_i: path_o`.
    """
    interpolations = {
        'app_name'      : conf['app_name'],
        'app_name_lower': conf['app_name'].lower().replace(' ', '_'),
        'app_version'   : conf['app_version'],
    }
    
    conf['build']['proj_dir'] = path_fmt(
        conf['build']['proj_dir']
    )
    
    conf['build']['dist_dir'] = path_fmt(
        conf['build']['dist_dir'].format(**interpolations)
    )
    
    conf['build']['launcher_name'] = (
        conf['build']['launcher_name'].format(**interpolations)
    )
    
    conf['build']['icon'] = path_fmt(
        conf['build']['icon'] or
        prj_model.python_ico
    )
    
    conf['build']['readme'] = path_fmt(
        conf['build']['readme']
    )
    
    for t in conf['build']['target']:  # type: TTarget
        t['file'] = path_fmt(
            t['file'].format(dist_dir=conf['build']['dist_dir'])
        )
    
    # --------------------------------------------------------------------------
    
    # note: `conf['build']['attachments']` and `conf['build']['module_paths']`
    # may include keyword `dist:xxx`, it requires `path_fmt.dir_o` provided. so
    # here we must make sure `path_fmt.dir_o` to be defined.
    path_fmt.dir_o = conf['build']['dist_dir']
    
    temp = {}  # type: TAttachments
    for k, v in conf['build']['attachments'].items():
        # lk.logt('[D0510]', k, v)
        k = path_fmt(k)
        # noinspection PyUnresolvedReferences
        v = v.split(',')  # type: list[str]
        if v[-1].startswith('dist:'):
            assert len(v) > 1, (conf['build']['attachments'], k, v)
            path = path_fmt(v[-1].format(name=basename(k)))
            temp[k] = {'marks': tuple(v[:-1]), 'path': path}
        else:
            temp[k] = {'marks': tuple(v), 'path': ''}
    conf['build']['attachments'] = temp

    # noinspection PyTypedDict
    conf['build']['attachments_exclusions'] = tuple(
        map(path_fmt, conf['build']['attachments_exclusions'])
    )
    
    # --------------------------------------------------------------------------
    
    # OPTM: in current designed pattern, `conf['build']['module_paths']`
    #   accepts paths both from `src_root` and from `dst_root`. but we need to
    #   unify them to be all paths based on `dst_root`.
    module_paths = conf['build']['module_paths']
    for i, p in enumerate(module_paths):
        if p.startswith('dist:'):
            p = path_fmt(p)
        else:
            # FIXME: see `pyportable_installer/main_flow/step3/step3_3/create
            #   _launcher.py > _generate_pylauncher > vars:_ext_paths`
            # p = src_2_dst(
            #     path_fmt(p), conf['build']['proj_dir'], path_fmt.dir_o
            # )
            p = 'src:' + path_fmt(p)
        module_paths[i] = p
    conf['build']['module_paths'] = module_paths
    del module_paths
    
    # # conf['build']['module_paths'] = list(
    # #     map(path_fmt, conf['build']['module_paths'])
    # # )
    
    # --------------------------------------------------------------------------
    
    mode = conf['build']['venv']['mode']
    options = conf['build']['venv']['options'][mode]
    
    def _load_requirements(req: Union[str, list[str]]):
        if isinstance(req, str):
            if req:
                # FIXME: path_fmt must be 'abspath'
                if path_fmt.fmt == 'relpath':
                    # file = path_fmt.dir_i + '/' + path_fmt
                    return ['...']
                from lk_utils.read_and_write import load_list
                file = path_fmt(req)
                return [x for x in load_list(file)
                        if x and not x.startswith('#')]
            else:
                return []
        else:
            return req
    
    if mode == 'source_venv':
        options['path'] = path_fmt(options['path'])
    elif mode == 'pip':
        options['requirements'] = _load_requirements(options['requirements'])
        options['local'] = path_fmt(options['local'])
    elif mode == 'embed_python':
        options['path'] = path_fmt(options['path'])
    elif mode == 'depsland':
        options['requirements'] = _load_requirements(options['requirements'])
        options['venv_name'] = options['venv_name'].format(**interpolations)
        if not options['venv_id']:
            options['venv_id'] = str(uuid1()).replace('-', '')
        options['local'] = path_fmt(options['local'])
    else:
        raise ValueError(mode)
    
    return conf
