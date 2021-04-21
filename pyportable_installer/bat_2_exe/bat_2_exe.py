"""
https://github.com/tokyoneon/B2E

Command:
    bat_to_exe_converter /bat {file.bat} /exe {file.exe} {options}

Options:
    see: open 'pyportable_installer/bat_2_exe/bat_to_exe_converter.exe'
         -> menu bar -> tools -> cmd tools

Examples:
    bat_to_exe_converter /bat xxx.bat /exe xxx.exe
    bat_to_exe_converter /bat xxx.bat /exe xxx.exe /icon xxx.ico
    bat_to_exe_converter /bat xxx.bat /exe xxx.exe /x64 /icon xxx.ico
    bat_to_exe_converter /bat xxx.bat /exe xxx.exe /x64 /icon xxx.ico
"""
from os import popen
from os.path import abspath

_bat_2_exe_converter = abspath(f'{__file__}/../bat_to_exe_converter.exe')


def main(bat_file, exe_file, icon='', *options):
    """
    
    Args:
        bat_file: abspath
        exe_file: abspath
        icon: abspath *.ico
        *options: suggested options below
            /x64
            /invisible
            /password {your_password}
            /uac-admin
            /uac-user
    """
    if icon: assert icon.endswith('.ico')
    cmd = '"{}" /bat "{}" /exe "{}" {} {}'.format(
        _bat_2_exe_converter,
        bat_file,
        exe_file,
        '' if not icon else f'/icon "{icon}"',
        ' '.join(options)
    ).strip()
    print('cmd', cmd)
    return popen(cmd).read()


if __name__ == '__main__':
    cmd = '{} /bat {} /exe {}'.format(
        _bat_2_exe_converter,
        abspath('../template/launch_by_venv.bat'),
        abspath('../../tests/test1.exe')
    )
    print(cmd)
    print(popen(cmd).read())
