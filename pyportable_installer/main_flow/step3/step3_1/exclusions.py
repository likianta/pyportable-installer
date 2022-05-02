from typing import Optional


class AttachmentsExclusions:
    
    def __init__(self):
        self.excluded_dirnames = (
            '__pycache__', '.git', '.idea', '.pytest_cache', '.svn', '.vscode',
            '.DS_Store',
        )
        self.excluded_filenames = (
            '.git', '.gitattributes', '.gitignore', '.gitkeep',
        )
        self.excluded_paths = None  # type: Optional[set[str]]
    
    def _indexing_global_exlusion_list(self):
        from ....global_conf import gconf
        
        if gconf.attachments_exclusions is None:
            print('[E4050]', '''
                The global attachments exclusions are not initialized!
                You can only import this module after `pyportable_installer
                .main_flow.step1.init_key_params` got executed.
                
                Related:
                    `~.main_flow.step1.init_key_params.init_key_params`
                    `.attachments`
            ''', ':v4p')
            raise Exception
        else:
            self.excluded_paths = set(
                p + '/' for p in gconf.attachments_exclusions
            )
        
        print(
            ':l', 'attachments exclusions overview',
            self.excluded_filenames,
            self.excluded_dirnames,
            self.excluded_paths,
        )
    
    def monitor_transferring(self, name: str, path: str, type_: str, h=1):
        if self.excluded_paths is None:
            self._indexing_global_exlusion_list()
        assert type_ in ('file', 'dir')
        
        pass_through = True
        
        if (path + '/').startswith(tuple(self.excluded_paths)):
            pass_through = False
        if name:
            if (
                    (type_ == 'file' and name in self.excluded_filenames) or
                    (type_ == 'dir' and name in self.excluded_dirnames)
            ):
                self.excluded_paths.add(path + '/')
                pass_through = False
        
        if not pass_through:
            if type_ == 'file':
                print('skip making file', path, f':vp{h}s')
            else:
                print('skip making dir', path, f':vp{h}s')
        return pass_through
    
    def filter_files(self, path: str, name: str):
        return self.monitor_transferring(name, path, 'file', h=2)
    
    def filter_dirs(self, path: str, name: str):
        return self.monitor_transferring(name, path, 'dir', h=2)


attachments_exclusions_handler = AttachmentsExclusions()
