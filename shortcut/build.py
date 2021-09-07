from textwrap import dedent

from pyportable_installer import *


def main():
    mode = input(dedent('''\
        Build mode:
            0   full build
            1   min build
            2   debug build
        Input build mode number: ''')).strip()
    
    file = input('Input pyproject configuration file (abspath): ')
    
    if mode == '0':
        build = full_build
    elif mode == '1':
        build = min_build
    elif mode == '2':
        build = debug_build
    else:
        raise ValueError(mode)
    
    build(file)


if __name__ == '__main__':
    main()
