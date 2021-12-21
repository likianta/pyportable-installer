from pathlib import Path

from genexe.generate_exe import generate_exe
from lk_utils.read_and_write import load_list
from lk_utils.subproc import format_cmd  # noqa


def bat_2_exe(file_i, file_o, icon='', show_console=True):
    data_r = load_list(file_i)
    # data_w = ' && '.join(format_cmd(*data_r))
    data_w = ' && '.join(data_r)
    
    # https://github.com/silvandeleemput/gen-exe
    # https://blog.csdn.net/qq981378640/article/details/52980741
    data_w = data_w.replace('%~dp0', '{EXE_DIR}')
    data_w = data_w.replace('%cd%', '{EXE_DIR}')
    
    generate_exe(
        target=Path(file_o),
        command=data_w,
        icon_file=Path(icon),
        show_console=show_console
    )
