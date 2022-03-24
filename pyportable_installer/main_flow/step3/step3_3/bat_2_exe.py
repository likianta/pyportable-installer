from pathlib import Path

try:
    from genexe.generate_exe import generate_exe
except ImportError:
    generate_exe = None
from lk_utils.read_and_write import load_list
from lk_utils.subproc import format_cmd  # noqa


def bat_2_exe(file_i, file_o, icon='', show_console=True):
    if generate_exe is None:
        print('cannot generate exe from bat: gen-exe is not installed', ':v4p')
        print('^ if you see this info in windows, plese `pip install gen-exe` '
              'then try again.', ':v2p')
        return
    
    data_r = load_list(file_i)
    # data_w = ' && '.join(format_cmd(*data_r))
    data_w = ' && '.join(data_r).strip()
    
    # https://github.com/silvandeleemput/gen-exe
    # https://blog.csdn.net/qq981378640/article/details/52980741
    data_w = data_w.replace('%~dp0', '{EXE_DIR}')
    data_w = data_w.replace('%cd%', '{EXE_DIR}')
    if data_w.endswith('%*'): data_w = data_w[:-3]
    
    generate_exe(
        target=Path(file_o),
        command=data_w,
        icon_file=Path(icon),
        show_console=show_console
    )