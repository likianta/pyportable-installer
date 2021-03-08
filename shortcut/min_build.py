import os

from lk_logger import lk

from pyportable_installer import min_build


def main():
    lk.log_enable = False
    os.chdir('../pyportable_installer')
    min_build(input('Input pyproject.json (abspath): '))


if __name__ == '__main__':
    main()
