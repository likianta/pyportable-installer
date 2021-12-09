import sys


def parse_sys_argv():
    """
    Input (example):
        sys.argv = ['main.py', 'conf.pkl', 'launcher.exe', 'hello', 'world']
    Process:
        - Detect exe file and remove it from sys.argv.
        - Load config file.
        - The real arguments are ['hello', 'world'].
    """
    args = sys.argv
    #   the first arg is python filename to launch, the second is preset
    #   configuration file, the third is optional exe file.
    
    if len(args) == 0:
        raise ValueError('Unreachable case, the arguments cannot be none!')
    elif len(args) == 1:
        # WARNING: this won't be supported in the future.
        conf_file = '__main__'
        real_args = []
    else:
        if idx := _check_exe_file_in_args(args):
            args.pop(idx)
        conf_file = args.pop(1)
        real_args = args
    
    conf = _load_config(conf_file)
    return conf, real_args


def configure_launch_args():
    pass


def _check_exe_file_in_args(args):
    target_exe_dir = os.path.dirname(os.getcwd())
    if (len(args) > 2
            and args[2].endswith('.exe')
            and os.path.dirname(args[2]) == target_exe_dir):
        return 2
    else:
        return 0


def _load_conf(conf_file):
    assert conf_file.endswith(('.json', '.pkl')), (
        'Unknown file type to load config!', conf_file
    )
    
    if conf_file.endswith('.json'):
        from json import load
        with open(conf_file, 'r', encoding='utf-8') as f:
            return load(f)
    else:
        from pickle import load
        with open(conf_file, 'rb') as f:
            return load(f)
