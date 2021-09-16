import os

from pyportable_installer import full_build


def main(full_offline=False):
    _precheck()
    
    if full_offline:
        conf = full_build('pyproject.json', {
            'build': {
                'attachments': {
                    './requirements_offline': 'assets,dist:build/{name}',
                },
                'venv': {
                    'enable_venv': True,
                    'mode'       : 'depsland',
                    'options'    : {
                        'depsland': {
                            'offline': True,
                            'local'  : 'dist:build/requirements_offline'
                        }
                    }
                }
            }
        })  # dist size: ~15MB
    else:
        conf = full_build('pyproject.json')  # dist size: ~10MB
        
    if full_offline:
        os.rename(conf['build']['dist_dir'],
                  conf['build']['dist_dir'] + '-win64-full')
    else:
        os.rename(conf['build']['dist_dir'],
                  conf['build']['dist_dir'] + '-win64-standard')


def _precheck():
    # from pyportable_installer.main import Misc
    # if Misc.log_level != 0:
    #     raise CheckFailed(Misc.log_level)
    pass


class CheckFailed(Exception):
    pass


if __name__ == '__main__':
    main(full_offline=False)
    # main(full_offline=True)
