from textwrap import dedent

from pyportable_installer import *


def main():
    print(dedent('''\
        Command template:
            <mode> <pyproject_file>
            
        For example:
            0 D:\\my_project\\hello_world\\pyproject.json
            
        Params:
            mode:
                0   full build
                1   min build
                2   debug build
            pyproject_file:
                An absolute path to your 'pyproject.json'.
                The filename is changeable, but please make sure it is placed
                right in its project and all relative paths description in it
                is calculated based on its directory.
    '''))
    
    cmd = input('Your command here: ')
    mode, file = cmd.split(' ', 1)
    
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
