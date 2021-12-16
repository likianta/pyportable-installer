from os.path import basename

from .name_converter import NameConverter
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
    name_converter = NameConverter(conf['app_name'])
    placeholders = {
        'app_name'       : name_converter.raw,
        'app_name_lower' : name_converter.lower_case,
        'app_name_upper' : name_converter.upper_case,
        'app_name_title' : name_converter.title_case,
        'app_name_snake' : name_converter.snake_case,
        'app_name_kebab' : name_converter.kebab_case,
        'app_name_camel' : name_converter.camel_case,
        'app_name_pascal': name_converter.pascal_case,
        
        # new patterns (not complete)
        # 'app name'       : name_converter.lower_case,
        # 'App Name'       : name_converter.title_case,
        # 'APP NAME'       : name_converter.upper_case,
        # 'app_name': name_converter.snake_case,
        # 'app-name'       : name_converter.kebab_case,
        # 'appName'        : name_converter.camel_case,
        # 'AppName'        : name_converter.pascal_case,
        
        'app_version'    : conf['app_version'],
    }
    del name_converter
    
    conf['build']['proj_dir'] = path_fmt(
        conf['build']['proj_dir']
    )
    
    conf['build']['dist_dir'] = path_fmt(
        conf['build']['dist_dir'].format(**placeholders)
    )
    
    conf['build']['readme'] = path_fmt(
        conf['build']['readme']
    )
    
    def _reformat_launchers():
        old, new = conf['build']['launchers'], {}
        for k, v in old.items():
            new[k.format(**placeholders)] = v
        conf['build']['launchers'] = new
        
        for i, (k, v) in enumerate(conf['build']['launchers'].items()):
            v['file'] = path_fmt(
                v['file'].format(dist_dir=conf['build']['dist_dir'])
            )
            if i == 0:
                conf['build']['launcher_name'] = k
                v['icon'] = path_fmt(v['icon'] or prj_model.python_ico)
            else:
                v['icon'] = path_fmt(v['icon'])
    
    _reformat_launchers()
    
    # --------------------------------------------------------------------------
    
    # note: `conf['build']['attachments']` and `conf['build']['module_paths']`
    # may include keyword `dist:xxx`, it requires `path_fmt.dir_o`. so here we
    # must make sure `path_fmt.dir_o` has been defined.
    path_fmt.dir_o = conf['build']['dist_dir']
    
    temp0 = {}  # type: TAttachments
    for k, v in conf['build']['attachments'].items():
        # lk.logt('[D0510]', k, v)
        k = path_fmt(k)
        # noinspection PyUnresolvedReferences
        v = v.split(',')  # type: List[str]
        if v[-1].startswith('dist:'):
            assert len(v) > 1, ((k, v), conf['build']['attachments'])
            path = path_fmt(v[-1].format(name=basename(k)))
            temp0[k] = {'marks': tuple(v[:-1]), 'path': path}
        else:
            temp0[k] = {'marks': tuple(v), 'path': ''}
    conf['build']['attachments'] = temp0
    del temp0
    
    # noinspection PyTypedDict
    conf['build']['attachments_exclusions'] = tuple(
        map(path_fmt, conf['build']['attachments_exclusions'])
    )
    
    # --------------------------------------------------------------------------
    # build:module_paths
    
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
    # build:venv
    
    mode = conf['build']['venv']['mode']
    options = conf['build']['venv']['options'][mode]
    
    def _load_requirements(req: Union[str, List[str]]):
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
    
    if mode == 'depsland':
        options['venv_name'] = options['venv_name'].format(**placeholders)
        if options['venv_id'] in ('', '_random'):
            from secrets import token_urlsafe
            options['venv_id'] = token_urlsafe()
        options['requirements'] = _load_requirements(options['requirements'])
        options['local'] = path_fmt(options['local'])
    elif mode == 'embed_python':
        options['path'] = path_fmt(options['path'])
    elif mode == 'pip':
        options['requirements'] = _load_requirements(options['requirements'])
        options['local'] = path_fmt(options['local'])
    elif mode == 'source_venv':
        options['path'] = path_fmt(options['path'])
    else:
        raise ValueError(mode)
    
    # --------------------------------------------------------------------------
    # build:compiler
    
    name = conf['build']['compiler']['name']
    options = conf['build']['compiler']['options'][name]
    
    if name == 'pyportable_crypto':
        if '{random}' in options['key']:
            from secrets import token_urlsafe
            options['key'] = options['key'].format(random=token_urlsafe())
    
    return conf
