from os.path import dirname
from sys import version_info


class GlobalConf:
    """ Most attributes are initialized in `~.main_flow.step1.init_key_params`.
    """
    pyproj_file = ''
    pyproj_dir = ''
    
    current_pyversion = "python{}{}".format(
        version_info.major, version_info.minor
    )
    target_pyversion = ''  # format: 'python**', e.g. 'python38', 'python38-32'
    
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
