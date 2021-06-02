import os

from pyportable_installer import *


def main():
    os.chdir('../pyportable_installer')
    
    full_build(input('Input pyproject (abspath): '))
    # min_build(input('Input pyproject (abspath): '))
    # debug_build(input('Input pyproject (abspath): '))


if __name__ == '__main__':
    main()
