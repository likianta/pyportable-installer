"""
注: 本模块不要有第三方依赖.
"""
from json import load
from os import popen

from .pretty_print import printer


def main(file='manifest.json'):
    """
    Args:
        file: 在发布时, doctor.py 会产生一个编译文件到 {dist}/build/checkup
            .pyc, 在同目录下还有一个 {dist}/build/manifest.json, 就是本参数要传
            入的文件
    
    References:
        template/manifest.json
        prebuild.save_build_info()
    """
    with open(file, 'r', encoding='utf-8') as f:
        conf = load(f)
    
    _check_and_set(conf)
    
    with printer.heading('Successfully finished'):
        input('    Checkup has finished, press enter to close the window. ')


def _check_and_set(conf: dict):
    with printer.heading('Python version checking'):
        target_version = conf['python_version']  # e.g. '3.8'
        current_version, result = check_pyversion(
            *map(int, target_version.split('.'))
            #   target_version: '3.8' -> ['3', '8'] -> (3, 8)
        )
        printer.info(
            f'Target version: >={target_version}',
            f'You version: {current_version}',
            status=result
        )
        if result is False:
            raise EnvironmentError(
                f'Python v{target_version} above is required!'
            )
    
    # --------------------------------------------------------------------------
    
    if conf['check_pip_repo']:
        with printer.heading('Pip repo config checking'):
            info, result = check_pip_conf()
            printer.info(*info.strip().split('\n'), status=result)
            if result is False:
                if printer.ask('The pip configuration is not correct!',
                               'Would you allow the program to fix it?'):
                    _fix_pip_repo_config()
                else:
                    raise EnvironmentError('Pip repo configuration failed')


# ------------------------------------------------------------------------------

def check_pyversion(major, minor, micro=0):
    """ Check Python version.
    
    编译后的 .pyc 文件对 python 版本的要求较高. 例如, 通过 python 3.8.x 编译的
    .pyc 只能通过 python 3.8.x 来运行.
    """
    from sys import version_info as info
    curr_ver = f'{info.major}.{info.minor}.{info.micro}'
    is_fullfilled = False
    if info.major == major:
        if info.minor > minor:
            is_fullfilled = False  # False (default) | True
            #   如果您发布的是源码文件 (.py), 则改为 True
            #   如果您发布的是编译后的文件 (.pyc), 则改为 False
        elif info.minor == minor:
            if info.micro >= micro:
                is_fullfilled = True
    return curr_ver, is_fullfilled


def check_pip_conf():
    """ Check pip configurations.
    
    判断 pip 的仓库地址是否设置为国内镜像.
    """
    ret = popen('pip config list').read()
    return ret, 'https://pypi.tuna.tsinghua.edu.cn/simple' in ret


# ------------------------------------------------------------------------------

def _fix_pip_repo_config():
    with printer.heading('Writing pip config to local pip'):
        printer.info(popen(
            'pip config set global.index-url '
            'https://pypi.tuna.tsinghua.edu.cn/simple'
        ).read())
        printer.info(popen(
            'pip config set global.trusted-host '
            'pypi.tuna.tsinghua.edu.cn'
        ).read())


if __name__ == '__main__':
    main()
