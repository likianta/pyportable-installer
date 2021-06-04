from os import mkdir, path as ospath
from shutil import copytree

from lk_logger import lk

from .global_dirs import curr_dir
from .typehint import *
from .utils import mkdirs, send_cmd


def main(venv_options: TConfBuildVenv, root_dir, create_venv_shell=True):
    builder = VEnvBuilder()
    pyversion = venv_options['python_version']
    
    if create_venv_shell:
        mode = venv_options['mode']
        options = venv_options['options'][mode]
        
        if mode == 'depsland':
            build_venv_by_depsland(**options)
        elif mode == 'pip':
            build_venv_by_pip(pyversion=pyversion, **options)
        elif mode == 'source_venv':
            build_venv_by_source_venv(
                options['path'], f'{root_dir}/venv',
                builder.get_embed_python_dir(pyversion)
            )
        else:
            raise ValueError('Unknown venv mode', mode)
    
    else:
        mkdirs(root_dir, 'venv', 'site-packages')
    
    return builder


def build_venv_by_source_venv(src_venv_dir: TPath, dst_venv_dir: TPath,
                              embed_python_dir: TPath):
    """
    Args:
        src_venv_dir: 'source virtual environment directory'.
            tip: you can pass an empty to this argument, see reason at `Notes:3`
        dst_venv_dir: 'distributed virtual environment directory'
        embed_python_dir:

    Notes:
        1. 本函数使用了 embed_python 独立安装包的内容, 而非简单地把 src_venv_dir
           拷贝到打包目录, 这是因为 src_venv_dir 里面的 Python 是不可独立使用的.
           也就是说, 在一个没有安装过 Python 的用户电脑上, 调用 src_venv_dir 下
           的 Python 编译器将失败! 所以我们需要的是一个嵌入版的 Python (在
           Python 官网下载带有 "embed" 字样的压缩包, 并解压, 我在 pyportable
           _installer 项目下已经准备了一份)
        2. 出于性能和成本考虑, 您不必提供有效 src_venv_dir 参数, 即您可以给该参
           数传入一个空字符串, 这样本函数会仅创建虚拟环境的框架 (dst_venv_dir),
           并让 '{dst_venv_dir}/site-packages' 留空. 稍后您可以手动地复制, 或剪
           切所需的依赖到 '{dst_venv_dir}/site-packages'

    Results:
        copy source dir to target dir:
            lib/python-{version}-embed-amd64 -> {dst_venv_dir}
            {src_venv_dir}/Lib/site-packages -> {dst_venv_dir}/site-packages
    """
    copytree(embed_python_dir, dst_venv_dir)
    
    # copy site-packages
    if ospath.exists(src_venv_dir):
        copytree(f'{src_venv_dir}/Lib/site-packages',
                 f'{dst_venv_dir}/site-packages')
    else:  # just create an empty folder
        mkdir(f'{dst_venv_dir}/site-packages')


# noinspection PyUnusedLocal
def build_venv_by_depsland(requirements: TRequirements):
    raise NotImplementedError


def build_venv_by_pip(requirements: TRequirements, pypi_url, local, offline,
                      pyversion, quiet=False):
    """
    
    Args:
        requirements:
        pypi_url: str.
            suggest list:
                official    https://pypi.python.org/simple/
                tsinghua    https://pypi.tuna.tsinghua.edu.cn/simple/
                aliyun      http://mirrors.aliyun.com/pypi/simple/
                ustc        https://pypi.mirrors.ustc.edu.cn/simple/
                douban      http://pypi.douban.com/simple/
                
        local:
        offline:
        pyversion:
        quiet:

    Warnings:
        请勿随意更改本函数的参数名, 这些名字与 `typehint.py:_TPipOptions` 的成员
        名有关系, 二者名字需要保持一致.
    """
    if not requirements:
        # `requirements` is empty string or empty list
        return
    
    if offline is False:
        assert pypi_url
        host = pypi_url \
            .removeprefix('http://') \
            .removeprefix('https://') \
            .split('/', 1)[0]
    else:
        host = ''
    
    find_links = f'--find-links={local}' if local else ''
    no_index = '--no-index' if offline else ''
    pypi_url = f'--index-url {pypi_url}' if not offline else ''
    quiet = '--quiet' if quiet else ''
    trusted_host = f'--trusted-host {host}' if host else ''
    
    if isinstance(requirements, str):
        assert ospath.exists(requirements)
        # see cmd help: `pip download -h`
        send_cmd(
            f'pip download'
            f' -r "{requirements}"'
            f' --disable-pip-version-check'
            f' --python-version {pyversion}'
            f' {find_links}'
            f' {no_index}'
            f' {pypi_url}'
            f' {quiet}'
            f' {trusted_host}',
            ignore_errors=True
        )
    else:
        for pkg in requirements:
            try:
                send_cmd(pkg)
            except:
                lk.logt('[W0835]', 'Pip installing failed', pkg)


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
    
    def get_embed_python_dir(self, pyversion: str):
        try:
            path = self.options['embed_python'][pyversion]
        except KeyError:
            raise Exception('未支持或未能识别的 Python 版本', pyversion)
        
        if not ospath.exists(path):
            self._download_help(pyversion)
            raise SystemExit
        
        return path
    
    def get_embed_python_interpreter(self, pyversion: str):
        return self.get_embed_python_dir(pyversion) + '/python.exe'
    
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
