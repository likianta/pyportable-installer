from os import mkdir
from os.path import exists

from lk_logger import lk

from .dist_tree import DistTree
from ...typehint import *


def main(conf: TConf):
    """ Create dist-side tree (all empty folders under `dst_root`) """
    _precheck(conf)
    
    # create main folders under dst_root.
    mkdir(conf['build']['dist_dir'])
    mkdir(conf['build']['dist_dir'] + '/' + 'build')
    mkdir(conf['build']['dist_dir'] + '/' + 'lib')
    mkdir(conf['build']['dist_dir'] + '/' + 'src')
    mkdir(conf['build']['dist_dir'] + '/' + 'src' + '/' + '.pylauncher_conf')
    
    dist_tree = DistTree()
    
    """
    Add to source dirs list:
        conf:
            build:
                + proj_dir
                + target
                + attachments

    Do not add to source dirs list:
        conf:
            build:
                - dist_dir
                - icon
                - readme
                - module_paths
    """
    dist_tree.add_src_dirs(
        conf['build']['proj_dir'],
        *(x['file'] for x in conf['build']['target']),
        *(k for k, v in conf['build']['attachments'].items()
          if v['path'] == ''),
    )
    
    src_root = dist_tree.suggest_src_root()
    dst_root = conf['build']['dist_dir']
    lk.loga(f'the suggest source root directory is: {src_root}')
    
    dist_tree.build_dst_dirs(src_root, f'{dst_root}/src')
    
    # init global path models
    _init_path_models(src_root, dst_root, conf)
    
    return src_root, dst_root


def _precheck(conf: TConf):
    assert not exists(conf['build']['dist_dir']), (
        'The target distribution directory already exists, please appoint '
        'another (non-existent) folder to distribute.'
    )
    
    paths_not_exist = []
    for src_path in conf['build']['attachments']:
        if not exists(src_path):
            paths_not_exist.append(src_path)
    if paths_not_exist:
        lk.logp(paths_not_exist)
        raise FileNotFoundError(
            'Please make sure all required paths in `conf["build"]'
            '["attachments"]` are existed.'
        )
    
    # if conf['build']['venv']['enable_venv']:
    #     from .embed_python import EmbedPythonManager
    #     builder = EmbedPythonManager(
    #         pyversion=conf['build']['venv']['python_version']
    #     )
    #     # try to get a valid embed python path, if failed, this method will
    #     # raise an exception to terminate process.
    #     builder.get_embed_python_dir()
    #
    #     mode = conf['build']['venv']['mode']
    #     if mode == 'source_venv':
    #         if venv_path := conf['build']['venv']['options'][mode]['path']:
    #             if venv_path.startswith(src_path := conf['build']['proj_dir']):
    #                 lk.logt('[W2015]', f'''
    #                     Please do not put the Python virtual environment folder
    #                     in your source code folder! This will make the third-
    #                     party libraries to be encrypted, which usually leads to
    #                     unpredicatable errors.
    #                     You can put venv aside with the source code dir, this
    #                     is the recommended parctice.
    #
    #                     Current venv dir: {venv_path}
    #                     Suggest moved to: {ospath.dirname(src_path)}/venv
    #                 ''')
    #                 if input('Continue the process? (y/n): ').lower() != 'y':
    #                     raise SystemExit


def _init_path_models(src_root, dst_root, conf: TConf):
    from ...path_model import dst_model
    from ...path_model import src_model
    from ...path_model import relpath
    
    src_model.init(
        src_root=src_root, prj_root=conf['build']['proj_dir'],
        readme=conf['build']['readme']
    )
    dst_model.init(
        dst_root=dst_root,
        prj_relroot=relpath(src_model.prj_root, src_model.src_root),
        launcher_name=conf['build']['launcher_name'],
        readme=conf['build']['readme']
    )
