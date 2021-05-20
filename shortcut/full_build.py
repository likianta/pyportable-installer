import os

from lk_logger import lk

from pyportable_installer import full_build


def main():
    lk.log_enable = False
    os.chdir('../pyportable_installer')
    full_build(input('Input pyproject (abspath): '))


if __name__ == '__main__':
    main()
