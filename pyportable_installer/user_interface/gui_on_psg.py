"""
requirements:
    pip install pysimplegui
"""
import os.path

import PySimpleGUI as Gui

import pyportable_installer

Gui.theme('SandyBeach')


class GuiEx:
    """ extended gui components. """
    
    # noinspection PyPep8Naming
    @staticmethod
    def FormGroup(title='', data: dict = None, key: str = None,
                  use_prefix=True):
        # data: dict[str key, str value]
        
        if use_prefix and key:
            prefixify = lambda k: f'{key}.{k}'
        else:
            prefixify = lambda k: k
        
        _best_key_width = max(map(len, data.keys()))
        
        def unpack_dict():
            for k, v in data.items():
                yield [  # this is a row
                    Gui.Text(k, size=(_best_key_width, 1),
                             justification='right'),
                    Gui.Input(default_text=v, key=prefixify(k))
                ]
        
        return Gui.Frame(title, list(unpack_dict()), key=key)


def main():  # TODO: add `default_file` parameter.
    layout = [
        [  # row 0: welcome message
            Gui.Text('Welcome using PyPortable Installer!\n'
                     'Input a pyproject.json file to start...'),
            # Gui.Text('Input a pyproject.json file to start...'),
        ],
        
        [  # row 1: pyproj conf file input
            Gui.Input(change_submits=True, key='file'),
            Gui.FileBrowse('Browse', key='file_browse'),
        ],
        
        [  # row 2: most modified configurations, change them here will
            # override the ones in the pyproj conf file.
            GuiEx.FormGroup('Most modified options', {
                'app_name'   : '',
                'app_version': '',
                'proj_dir'   : '',
                'dist_dir'   : '',
            }, key='options')
        ],
        
        [  # row 3: buttons
            Gui.Button('Reload', key='reload'),
            Gui.Button('Overwrite', key='overwrite'),
            Gui.Button('Run', key='run'),
            Gui.Text('', key='short_info')
        ],
        
        [  # row 4: open result
            Gui.Text('', key='result'),
            Gui.Button('Open', visible=False, key='result_open')
        ]
    ]
    
    win = Gui.Window('PyPortable Installer', layout)
    mainloop(win)


def mainloop(win: Gui.Window):
    import os.path
    
    pyproj_conf = PyProjConf()
    controls = {'get_ready_to_run': False}
    
    while True:
        evt, val = win.read()
        # lk.logp(evt, val)
        
        if evt in (None, 'Exit'):
            break
        
        elif evt == 'file':
            file = val[evt]
            if file == pyproj_conf.file:
                continue
            else:
                # FIXME:
                #   win['file_browse'].update(initial_folder=os.path.dirname(file))
                win['result'].update('')
                win['result_open'].update(visible=False)
            
            if file.endswith('.json') and os.path.exists(file):
                pyproj_conf.load(file)
                try:
                    win['options.app_name'].update(pyproj_conf.app_name)
                    win['options.app_version'].update(pyproj_conf.app_version)
                    win['options.proj_dir'].update(pyproj_conf.proj_dir)
                    win['options.dist_dir'].update(pyproj_conf.dist_dir)
                    win['short_info'].update('Pyproj file loaded.')
                    controls['get_ready_to_run'] = True
                except KeyError:
                    win['short_info'].update('Invalid pyproj file!')
                    controls['get_ready_to_run'] = False
        
        elif evt == 'reload':
            pyproj_conf.load(pyproj_conf.file)
            win['options.app_name'].update(pyproj_conf.app_name)
            win['options.app_version'].update(pyproj_conf.app_version)
            win['options.proj_dir'].update(pyproj_conf.proj_dir)
            win['options.dist_dir'].update(pyproj_conf.dist_dir)
            win['short_info'].update('Reload successful!')
        
        elif evt == 'overwrite':
            pyproj_conf.overwrite({
                'app_name'   : win['options.app_name'].get(),
                'app_version': win['options.app_version'].get(),
                'proj_dir'   : win['options.proj_dir'].get(),
                'dist_dir'   : win['options.dist_dir'].get(),
            })
            win['short_info'].update('Modification saved!')
        
        elif evt == 'run':
            if not controls['get_ready_to_run']:
                win['short_info'].update(
                    'Program is not ready to run. Please check your '
                    'configuration.'
                )
                continue
            try:
                result = pyportable_installer.full_build(
                    val['file'], additional_conf={
                        'app_name'   : win['options.app_name'].get(),
                        'app_version': win['options.app_version'].get(),
                        'build'      : {
                            'proj_dir': win['options.proj_dir'].get(),
                            'dist_dir': win['options.dist_dir'].get(),
                        }
                    }
                )
            except Exception as e:  # noqa
                # import sys
                from traceback import format_exc
                # from traceback import format_exception
                err_win = Gui.Window('Build Failed', [
                    [Gui.Text(format_exc())],
                ])
                while True:
                    evt, _ = err_win.read()
                    if evt in (None, 'Exit'):
                        break
                win['short_info'].update('')
                continue
            
            win['short_info'].update('Packaging done!')
            win['result'].update(result['build']['dist_dir'])
            win['result_open'].update(visible=True)
        
        elif evt == 'result_open':
            path = win['result'].get()
            if os.path.exists(path):
                from lk_utils import run_cmd_args
                run_cmd_args('start', path)
                #   note: do not use `explorer <path>`, it will raise an error.
                #        (ps: the error message shows empty, so i don't known
                #         why this happens.)
                win['short_info'].update('')
            else:
                win['short_info'].update('Target dir not exists!')


class PyProjConf:
    from pyportable_installer.typehint import TConf
    file: str = ''
    dir_: str = ''
    conf: TConf = None
    
    def load(self, file):
        from lk_utils import loads
        self.file = file
        self.dir_ = os.path.dirname(file)
        self.conf = loads(file)
    
    reload = load
    
    @property
    def app_name(self):
        return self.conf['app_name']
    
    @property
    def app_version(self):
        return self.conf['app_version']
    
    @property
    def proj_dir(self):
        return self.conf['build']['proj_dir']
    
    @property
    def dist_dir(self):
        # note: the dist_dir is not the really existed in the system. because
        #   it contains '../' (which is relative to pyporj file), and some
        #   placeholders (e.g. '{app_name}', '{app_name_lower}',
        #   '{app_version}', etc.).
        return self.conf['build']['dist_dir']
    
    def overwrite(self, options):
        self.conf['app_name'] = options['app_name']
        self.conf['app_version'] = options['app_version']
        self.conf['build']['proj_dir'] = options['proj_dir']
        self.conf['build']['dist_dir'] = options['dist_dir']
        from lk_utils import dumps
        dumps(self.conf, self.file, pretty_dump=True)
        return True


if __name__ == '__main__':
    main()
