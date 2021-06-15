from os import mkdir, path as ospath
from shutil import copytree

from lk_logger import lk

from .embed_python import EmbedPythonManager
from .typehint import *
from .utils import mkdirs, mklink, send_cmd


def create_venv(
        embed_py_mgr: EmbedPythonManager,
        venv_options: TVenvBuildConf,
        root_dir: TPath,
        mode: THowVenvCreated
):
    if mode == 'empty_folder':
        mkdirs(root_dir, 'venv', 'site-packages')
        return
    
    # 这里的 `src_venv_dir` 无实际意义, 只是为了让代码看起来整齐. 我们把它作为参
    # 数传到 `_copy_site_packages:[params]kwargs` 也无实际意义, 因为我们最终用到
    # 的是由 `venv_options` 提供的路径信息.
    src_venv_dir = ''
    dst_venv_dir = f'{root_dir}/venv'
    embed_py_dir = embed_py_mgr.get_embed_python_dir()
    
    if mode == 'copy':
        _copy_python_interpreter(embed_py_dir, dst_venv_dir)
        _copy_site_packages(
            venv_options, pyversion=embed_py_mgr.pyversion,
            #   `embed_py_mgr.pyversion` is equivalent to
            #   `venv_options['python_version']`
            src_venv_dir=src_venv_dir,
            dst_venv_dir=dst_venv_dir,
            embed_py_dir=embed_py_dir,
        )
        return
    
    if mode == 'symbolink':
        
        def _is_the_same_driver(a: TPath, b: TPath):
            return a.lstrip('/').split('/', 1)[0] == \
                   b.lstrip('/').split('/', 1)[0]
        
        if _is_the_same_driver(embed_py_dir, dst_venv_dir):
            mklink(embed_py_dir, dst_venv_dir, exist_ok=True)
        else:
            # noinspection PyUnusedLocal
            mode = 'copy'
            _copy_python_interpreter(embed_py_dir, dst_venv_dir)
        
        if _is_the_same_driver(src_venv_dir, dst_venv_dir):
            mklink(f'{src_venv_dir}/lib/site-packages',
                   f'{dst_venv_dir}/site-packages')
        else:
            # noinspection PyUnusedLocal
            mode = 'empty_folder'
            lk.logt(
                '[W3359]',
                ''' cannot create symbol link acrossing different drivers:
                        {} --x--> {}
                    will do nothing instead. you need to copy them by manual
                    after installer finished.
                '''.format(
                    f'{src_venv_dir}/lib/site-packages',
                    f'{dst_venv_dir}/site-packages'
                )
            )
        
        return
    
    raise Exception('Unexpected error, this code should be unreachable.', mode)


def _copy_python_interpreter(
        embed_python_dir: TPath, dst_venv_dir: TPath
):
    copytree(embed_python_dir, dst_venv_dir)
    # copytree(embed_python_dir, dst_venv_dir, dirs_exist_ok=True)


def _copy_site_packages(venv_options: TVenvBuildConf, **kwargs):
    mode = venv_options['mode']
    options = venv_options['options'][mode]
    
    if mode == 'depsland':
        _build_venv_by_depsland(**options)
    elif mode == 'pip':
        _build_venv_by_pip(pyversion=kwargs['pyversion'], **options)
    elif mode == 'source_venv':
        _build_venv_by_source_venv(
            kwargs.get('src_venv_dir') or options['path'],
            kwargs['dst_venv_dir']
        )
    else:
        raise ValueError('Unknown venv mode', mode)


def _build_venv_by_source_venv(
        src_venv_dir: TPath, dst_venv_dir: TPath
):
    """
    Args:
        src_venv_dir: 'source virtual environment directory'.
            tip: you can pass an empty to this argument, see reason at `Notes:3`
        dst_venv_dir: 'distributed virtual environment directory'

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
    # copy site-packages
    if ospath.exists(src_venv_dir):
        copytree(f'{src_venv_dir}/Lib/site-packages',
                 f'{dst_venv_dir}/site-packages')
    else:  # just create an empty folder
        mkdir(f'{dst_venv_dir}/site-packages')


# noinspection PyUnusedLocal
def _build_venv_by_depsland(requirements: TRequirements):
    raise NotImplementedError


def _build_venv_by_pip(requirements: TRequirements, pypi_url, local, offline,
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
