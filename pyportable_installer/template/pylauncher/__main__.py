import os

from .launch_args import parse_sys_argv
from .launcher import launch

os.chdir(os.path.dirname(__file__))

conf, args = parse_sys_argv()
launch(conf, args)
