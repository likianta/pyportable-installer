from os import path as ospath

from ..global_dirs import curr_dir as _parent_dir
from ..typehint import *
from ..utils import mkdirs

curr_dir = f'{_parent_dir}/embed_python'


class EmbedPythonManager:
    
    def __init__(self, pyversion: TPyVersion):
        self.pyversion = pyversion
        
        from platform import system
        self.sys = system().lower()  # -> 'windows'|'linux'|'macos'|etc.
        
        download_dir = f'{curr_dir}/download'
        if not ospath.exists(f'{download_dir}/{self.sys}'):
            mkdirs(curr_dir, 'download', self.sys)
        
        self.options = {
            'windows': {
                'local' : {
                    '3.5'   : f'{download_dir}/windows/'
                              f'python-3.5.4-embed-amd64',
                    '3.5-32': f'{download_dir}/windows/'
                              f'python-3.5.4-embed-win32',
                    '3.6'   : f'{download_dir}/windows/'
                              f'python-3.6.8-embed-amd64',
                    '3.6-32': f'{download_dir}/windows/'
                              f'python-3.6.8-embed-win32',
                    '3.7'   : f'{download_dir}/windows/'
                              f'python-3.7.9-embed-amd64',
                    '3.7-32': f'{download_dir}/windows/'
                              f'python-3.7.9-embed-win32',
                    '3.8'   : f'{download_dir}/windows/'
                              f'python-3.8.10-embed-amd64',
                    '3.8-32': f'{download_dir}/windows/'
                              f'python-3.8.10-embed-win32',
                    '3.9'   : f'{download_dir}/windows/'
                              f'python-3.9.5-embed-amd64',
                    '3.9-32': f'{download_dir}/windows/'
                              f'python-3.9.5-embed-win32',
                },
                # https://www.python.org/downloads/windows/
                'server': {
                    '3.5'   : 'https://www.python.org/ftp/python/'
                              '3.5.4/python-3.5.4-embed-amd64.zip',
                    '3.5-32': 'https://www.python.org/ftp/python/'
                              '3.5.4/python-3.5.4-embed-win32.zip',
                    '3.6'   : 'https://www.python.org/ftp/python/'
                              '3.6.8/python-3.6.8-embed-amd64.zip',
                    '3.6-32': 'https://www.python.org/ftp/python/'
                              '3.6.8/python-3.6.8-embed-win32.zip',
                    '3.7'   : 'https://www.python.org/ftp/python/'
                              '3.7.9/python-3.7.9-embed-amd64.zip',
                    '3.7-32': 'https://www.python.org/ftp/python/'
                              '3.7.9/python-3.7.9-embed-win32.zip',
                    '3.8'   : 'https://www.python.org/ftp/python/'
                              '3.8.10/python-3.8.10-embed-amd64.zip',
                    '3.8-32': 'https://www.python.org/ftp/python/'
                              '3.8.10/python-3.8.10-embed-win32.zip',
                    '3.9'   : 'https://www.python.org/ftp/python/'
                              '3.9.5/python-3.9.5-embed-amd64.zip',
                    '3.9-32': 'https://www.python.org/ftp/python/'
                              '3.9.5/python-3.9.5-embed-win32.zip',
                }
            },
            # TODO: more system options
        }[self.sys]
    
    def get_embed_python_dir(self, pyversion=''):
        pyversion = pyversion or self.pyversion
        
        try:
            path = self.options['local'][pyversion]
        except KeyError:
            raise Exception('未支持或未能识别的 Python 版本', pyversion)
        
        if not ospath.exists(path):
            self._download_help(pyversion)
            raise SystemExit
        
        return path
    
    def get_embed_python_interpreter(self, pyversion=''):
        pyversion = pyversion or self.pyversion
        return self.get_embed_python_dir(pyversion) + '/python.exe'
    
    def _download_help(self, pyversion=''):
        pyversion = pyversion or self.pyversion
        path = self.options['local'][pyversion]
        link = self.options['server'][pyversion]
        print('''
            未找到嵌入式 Python 解释器离线资源, 本次运行将中止!

            请按照以下步骤操作, 之后重新运行本程序:

            1. 从该链接下载嵌入式 Python 安装包: {link}
            2. 将下载到的压缩文件解压, 获得 {name} 文件夹
            3. 将该文件夹放到此目录: {path}

            现在, 您可以重新运行本程序以继续打包工作.
        '''.format(
            link=link,
            name=ospath.basename(path),
            path=ospath.abspath(path)
        ))
        return path, link


def download_embed_python(pyversion: TPyVersion):
    """ See animated gif `../../.assets/downloading_embed_python.gif`
    
    Args:
        pyversion:

    References:
        python standard libraries:
            urllib
            zipfile
    """
    from time import strftime
    from urllib import request
    from zipfile import ZipFile
    
    manager = EmbedPythonManager(pyversion)
    
    path = manager.options['local'][pyversion]
    link = manager.options['server'][pyversion]
    
    if ospath.exists(path):
        raise FileExistsError(path)

    # download
    if not ospath.exists(file := f'{path}.zip'):
        print('download:', link)
        
        def update_progress(block_num, block_size, total_size):
            """
            
            Args:
                block_num: 已下载的数据块
                block_size: 数据块的大小
                total_size: 远程文件的大小
            """
            percent = block_size * block_num / total_size * 100
            if percent > 100: percent = 100
            
            # `print::params:end='\r'` not working in pycharm (solution):
            #   https://stackoverflow.com/questions/34950201/pycharm-print-end-r
            #   -statement-not-working
            print('\r{}\t{:.2f}%'.format(strftime('%H:%M:%S'), percent), end='')
            # # print('{}\t{:.2f}%'.format(strftime('%H:%M:%S'), percent),
            # #       end='\r')
        
        # https://blog.csdn.net/weixin_39790282/article/details/90170218
        request.urlretrieve(link, file, update_progress)
        print(' -> done!')
    
    # unzip
    file_handle = ZipFile(file)
    file_handle.extractall(path)
    print('see unzipped result:', path)

    # delete zip file
    pass
