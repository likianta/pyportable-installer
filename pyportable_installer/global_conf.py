from os.path import dirname


class GlobalConf:
    """ Most attributes are initialized in `~.main_flow.step1.init_key_params`.
    """
    pyproj_file = ''
    pyproj_dir = ''
    
    python_version = ''  # target python version
    full_python = ''
    embed_python = ''
    
    attachments_exclusions = None
    attachments_exist_scheme = 'error'
    
    @property
    def embed_python_dir(self):
        return dirname(self.embed_python)
    
    @property
    def full_python_dir(self):
        return dirname(self.full_python)


gconf = GlobalConf()

__all__ = ['gconf']
