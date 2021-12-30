import os
import sys

sys.path.append(os.path.dirname(__file__))

# from user_interface import cli  # noqa
from user_interface import gui_on_psg  # noqa

gui_on_psg.main()
