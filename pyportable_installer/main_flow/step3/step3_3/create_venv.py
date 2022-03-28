import re
from os import makedirs
from os import mkdir

from lk_utils import dumps
from lk_utils import run_cmd_args

from ..step3_1.attachments import copy_attachments
from ....global_conf import gconf
from ....path_model import dst_model
from ....path_model import prj_model
from ....typehint import TVenvMode


def create_venv(mode: TVenvMode, options):
    if mode == 'depsland':
        return
    
    elif mode == 'embed_python':
        if options['path']:
            _ = list(copy_attachments({
                options['path']: {
                    'marks': ('assets',),
                    'path' : dst_model.venv
                }
            }))
            # # copytree(options['path'], dst_model.venv)
        else:
            mkdir(dst_model.venv)
    
    elif mode in ('pip', 'source_venv'):
        # note that `copy_attachments` is an iterator, we need to exhaust it to
        # drive it processing.
        _ = list(copy_attachments({
            gconf.embed_python_dir: {
                'marks': ('root_assets',),
                'path' : dst_model.venv
            }
        }))
        
        if mode == 'pip' and options['requirements']:
            python = gconf.embed_python
            requirements = f'{prj_model.temp}/requirements.txt'
            target_dir = dst_model.venv + '/lib/site-packages'
            offline = options['offline'] or ''
            find_links = options['local']
            index_url = options['pypi_url']
            trusted_host = (
                re.search(r'(?:https?://)?([^/]+)', index_url).group(1)
                if index_url else ''
            )
            
            dumps(options['requirements'], requirements)
            makedirs(target_dir)
            run_cmd_args(python, '-m', 'pip', 'install',
                         '-r', requirements,
                         '-t', target_dir,
                         find_links and f'--find-links="{find_links}"',
                         offline and '--no-index',
                         index_url and f'--index-url={index_url}',
                         trusted_host and f'--trusted-host={trusted_host}',
                         '--no-python-version-warning',
                         '--no-input')
        
        elif mode == 'source_venv' and options['path']:
            if options['copy_venv']:
                _ = list(copy_attachments({
                    options['path'] + '/lib/site-packages': {
                        'marks': ('assets',),
                        'path' : dst_model.venv + '/lib/site-packages'
                    }
                }))
                # # copytree(options['path'] + '/lib/site-packages',
                # #          dst_model.venv + '/lib/site-packages')
            else:
                dst_model.venv = options['path']
                #   FIXME: black magic is not recommended!
                print(':v3', '[W0644]',
                      'The source venv is not copied, you may copy it later '
                      'after progress finished', options['path'])
    
    else:
        raise NotImplemented(mode, options)
