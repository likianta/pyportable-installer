from os import popen


def main(files_i, dir_o):
    """
    References:
        `cmd:pyarmor obfuscate -h`
        `pyportable_installer/assets_copy.py:copy_runtime`
        
    Notes:
        `pyarmor obfuscate --bootstrap {0~4}` 的区别:
            `pyarmor obfuscate --bootstrap 0`
                每个混淆后的文件的顶部都有一个相对导入:
                    'from .pytransform import pyarmor_runtime'
            `pyarmor obfuscate --bootstrap 1`
                混淆后的文件中, 只有 __init__.py 是相对导入:
                    'from .pytransform import pyarmor_runtime'
                其他 py 文件是绝对导入:
                    'from pytransform import pyarmor_runtime'
            `pyarmor obfuscate --bootstrap 2`
                每个混淆后的文件的顶部都有一个绝对导入:
                    'from pytransform import pyarmor_runtime'
                这是我们想要的.
            `pyarmor obfuscate --bootstrap 3`
                未知
            `pyarmor obfuscate --bootstrap 4`
                未知
            
    """
    files_i = ' '.join([f'"{f}"' for f in files_i])
    r = popen(  # FIXME: 不要使用环境变量. 自带一个 pyarmor.exe
        f'pyarmor obfuscate '
        f'-O "{dir_o}" --bootstrap 2 --exact -n '
        f'{files_i}'
    )
    print(r.read())
