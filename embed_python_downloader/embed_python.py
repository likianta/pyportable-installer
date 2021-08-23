"""
Download embedded python executables.
"""
import os
from os.path import basename, dirname
from time import strftime
from urllib import request
from zipfile import ZipFile

from lk_logger import lk

from .support import platform


def download_embed_python(pyversion, download_dir, platform=platform):
    """
    
    Args:
        pyversion:
        download_dir: the directory to put '{downloaded_embed_python}.zip' and
            '{extracted_embed_python}'. make sure it already exists.
        platform:

    Returns:

    """
    manager = EmbedPythonManager(pyversion, download_dir, platform=platform)
    file = manager.download()
    dir_ = extract_embed_python(file)
    manager.test()
    _disable_pth(pyversion, dir_)
    return file


def extract_embed_python(src_file, dst_dir='', pyversion=''):
    if not dst_dir:
        dst_dir = '{}/{}'.format(
            dirname(src_file), basename(src_file).removesuffix('.zip')
        )
    file_handle = ZipFile(src_file)
    file_handle.extractall(dst_dir)
    _disable_pth(pyversion, dst_dir)
    return dst_dir


def _disable_pth(pyversion, dir_):
    if not pyversion:
        try:
            pth_file = [
                x for x in os.listdir(dir_)
                if x.startswith('python') and x.endswith('._pth')
            ][0]
        except IndexError:
            return
    else:
        pth_file = f'{dir_}/{pyversion}._pth'
    if os.path.exists(pth_file):
        os.rename(pth_file, pth_file + '.bak')


class EmbedPythonManager:
    
    def __init__(self, pyversion, download_dir, platform=platform):
        self.pyversion = pyversion
        self.platform = platform
        self.bin_dir = download_dir
        self.download_dir = download_dir
    
    def download(self):
        """
        Download embed python file (.zip) to `path_mgr.curr_home`, then unzip
        file to `path_mgr.bin`
        """
        link = get_download_link(self.pyversion, self.platform)
        file = self.download_dir + '/' + link.rsplit("/")[-1]
        self._download(link, file, exist_ok=True)
        return file
    
    @staticmethod
    def _download(link, file, exist_ok=True):
        """ See animated gif `~/docs/.assets/downloading-embed-python-anim.gif`
        """
        if os.path.exists(file):
            if exist_ok:
                lk.loga('file already exists (pass)', file)
                return
            else:
                raise FileExistsError(file)
        
        def _update_progress(block_num, block_size, total_size):
            """

            Args:
                block_num: downloaded data blocks number
                block_size: size of each block
                total_size: total size of remote file in url
            """
            percent = block_size * block_num / total_size * 100
            if percent > 100: percent = 100
            print('\r{}\t{:.2f}%'.format(strftime('%H:%M:%S'), percent), end='')
            #   why put `\r` in the first param?
            #       because it doesn't work in pycharm if we pass it to `params:end`
            #       ref: https://stackoverflow.com/questions/34950201/pycharm-print-end
            #            -r-statement-not-working
        
        lk.loga('downloading', link)
        lk.loga('waiting for downloader starts...')
        # https://blog.csdn.net/weixin_39790282/article/details/90170218
        request.urlretrieve(link, file, _update_progress)
        lk.loga('done')
    
    def test(self):
        from lk_utils import send_cmd
        lk.loga(send_cmd(f'{self.interpreter} -V'))
    
    @property
    def interpreter(self):
        return f'{self.bin_dir}/python.exe'


def get_download_link(pyversion, platform=platform):
    urls = {
        'windows': {
            # https://www.python.org/downloads/windows/
            'python35'   : 'https://www.python.org/ftp/python/'
                           '3.5.4/python-3.5.4-embed-amd64.zip',
            'python35-32': 'https://www.python.org/ftp/python/'
                           '3.5.4/python-3.5.4-embed-win32.zip',
            'python36'   : 'https://www.python.org/ftp/python/'
                           '3.6.8/python-3.6.8-embed-amd64.zip',
            'python36-32': 'https://www.python.org/ftp/python/'
                           '3.6.8/python-3.6.8-embed-win32.zip',
            'python37'   : 'https://www.python.org/ftp/python/'
                           '3.7.9/python-3.7.9-embed-amd64.zip',
            'python37-32': 'https://www.python.org/ftp/python/'
                           '3.7.9/python-3.7.9-embed-win32.zip',
            'python38'   : 'https://www.python.org/ftp/python/'
                           '3.8.10/python-3.8.10-embed-amd64.zip',
            'python38-32': 'https://www.python.org/ftp/python/'
                           '3.8.10/python-3.8.10-embed-win32.zip',
            'python39'   : 'https://www.python.org/ftp/python/'
                           '3.9.5/python-3.9.5-embed-amd64.zip',
            'python39-32': 'https://www.python.org/ftp/python/'
                           '3.9.5/python-3.9.5-embed-win32.zip',
        },
        # TODO: more platforms needed
    }
    try:
        return urls[platform][pyversion]
    except KeyError:
        raise Exception('Unexpected Python version', platform, pyversion)
