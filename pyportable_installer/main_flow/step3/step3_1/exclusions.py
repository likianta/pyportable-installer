from typing import Optional

from lk_logger import lk


class AttachmentsExclusions:
    
    def __init__(self):
        self.excluded_dirnames = ('__pycache__', '.git', '.idea', '.svn')
        self.excluded_filenames = ('.gitkeep', '.gitignore')
        self.excluded_paths = None  # type: Optional[set[str]]
    
    def _indexing_global_exlusion_list(self):
        from ....global_conf import gconf
        
        if gconf.attachments_exclusions is None:
            lk.logt('[E4050]', '''
                The global attachments exclusions are not initialized!
                You can only import this module after `pyportable_installer
                .main_flow.step1.init_key_params` got executed.
                
                Related:
                    `~.main_flow.step1.init_key_params.init_key_params`
                    `.attachments`
            ''', h='parent')
            raise Exception
        else:
            self.excluded_paths = set(
                p + '/' for p in gconf.attachments_exclusions
            )
        
        lk.logp(
            self.excluded_filenames,
            self.excluded_dirnames,
            self.excluded_paths,
            title='attachments exclusions overview'
        )
    
    def monitor_transferring(self, name: str, path: str, type_: str, h='parent'):
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
                lk.logt('[D5438]', 'skip making file', path, h=h)
            else:
                lk.logt('[D5439]', 'skip making dir', path, h=h)
        return pass_through
    
    def filter_files(self, path: str, name: str):
        return self.monitor_transferring(name, path, 'file', 'grand_parent')
    
    def filter_dirs(self, path: str, name: str):
        return self.monitor_transferring(name, path, 'dir', 'grand_parent')


attachments_exclusions_handler = AttachmentsExclusions()
