"""
https://github.com/tokyoneon/B2E

Command:
    bat_to_exe_converter /bat {file.bat} /exe {file.exe} {options}

Options:
    see: open 'lkdist/bat_2_exe/bat_to_exe_converter.exe' -> menu bar -> tool
    -> cmd interface

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
    
    Notes:
        the caller is 'lkdist/prebuild.py', so the bat_to_exe_converter.exe path
        should be 'bat_2_exe/bat_to_exe_converter.exe'
    """
    if icon: assert icon.endswith('.ico')
    popen('{} /bat {} /exe {} {} {}'.format(
        _bat_2_exe_converter,
        bat_file,
        exe_file,
        '' if not icon else '/icon ' + icon,
        ' '.join(options)
    )).read()
