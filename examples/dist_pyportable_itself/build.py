import os

from lk_logger import lk

from pyportable_installer import full_build


def main(full_version=False):
    _precheck(full_version)
    
    if full_version:
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
        
    if full_version:
        os.rename(conf['build']['dist_dir'],
                  conf['build']['dist_dir'] + '-win64-full')
    else:
        os.rename(conf['build']['dist_dir'],
                  conf['build']['dist_dir'] + '-win64-standard')


def _precheck(full_version):
    if full_version:
        assert len(os.listdir('./requirements_offline')) > 1, '''
            The offline packages are not downloaded, please run the following
            commands:
                1) `cd {}`
                2) `pip download -r requirements.txt -d examples/dist_pyportable
                    _itself/requirements_offline`
        '''.format(os.path.abspath('../'))
    
    from pyportable_installer.main import Misc
    if Misc.log_level == 2:
        lk.logt('[W5033]', 'suggest downgrading `pyportable_installer.main.Misc'
                           '.log_level` to 1 or 0 before packaging start.')


if __name__ == '__main__':
    main(full_version=False)
    main(full_version=True)
