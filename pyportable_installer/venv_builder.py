from os import path as ospath
from .global_dirs import curr_dir


class VEnvBuilder:
    
    def __init__(self):
        from platform import system
        self.sys = system().lower()  # 'windows'|'linux'|etc.
        embed_python_dir = f'{curr_dir}/venv_assets/embed_python'
        
        # FIXME: `../../pyproject.toml` 的打包参数似乎没设好, 导致在发布为 whl
        #   时, 未包含 `embed_python_dir` 这个空文件夹.
        #   现在使用临时方法: 检查目录是否不存在, 如不存在则创建每个子节点.
        #   后面请尽快修复 pyproject.toml.
        if not ospath.exists(f'{embed_python_dir}/{self.sys}'):
            from .utils import mkdirs
            mkdirs(curr_dir, 'venv_assets', 'embed_python', self.sys)
        
        self.options = {
            'windows': {
                'embed_python'         : {
                    '3.5'   : f'{embed_python_dir}/windows/'
                              f'python-3.5.4-embed-amd64',
                    '3.5-32': f'{embed_python_dir}/windows/'
                              f'python-3.5.4-embed-win32',
                    '3.6'   : f'{embed_python_dir}/windows/'
                              f'python-3.6.8-embed-amd64',
                    '3.6-32': f'{embed_python_dir}/windows/'
                              f'python-3.6.8-embed-win32',
                    '3.7'   : f'{embed_python_dir}/windows/'
                              f'python-3.7.9-embed-amd64',
                    '3.7-32': f'{embed_python_dir}/windows/'
                              f'python-3.7.9-embed-win32',
                    '3.8'   : f'{embed_python_dir}/windows/'
                              f'python-3.8.10-embed-amd64',
                    '3.8-32': f'{embed_python_dir}/windows/'
                              f'python-3.8.10-embed-win32',
                    '3.9'   : f'{embed_python_dir}/windows/'
                              f'python-3.9.5-embed-amd64',
                    '3.9-32': f'{embed_python_dir}/windows/'
                              f'python-3.9.5-embed-win32',
                },
                # https://www.python.org/downloads/windows/
                'embed_python_download': {
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

    def get_embed_python(self, pyversion: str):
        try:
            path = self.options['embed_python'][pyversion]
        except KeyError:
            raise Exception('未支持或未能识别的 Python 版本', pyversion)
        
        if not ospath.exists(path):
            self._download_help(pyversion)
            raise SystemExit

        return path
        
    def _download_help(self, pyversion):
        path = self.options['embed_python'][pyversion]
        link = self.options['embed_python_download'][pyversion]
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


def download_embed_python(pyversion):
    builder = VEnvBuilder()
    
    path = builder.options['embed_python'][pyversion]
    link = builder.options['embed_python_download'][pyversion]
    
    if not ospath.exists(path):
        print('download', link)
        # TODO: download and unzip to `path` ...
