"""
Placeholders:
    cythonize_packages
    filename
"""
from os import chdir
from os.path import dirname
from sys import path

curr_dir = dirname(__file__)

chdir(curr_dir)
path.append(curr_dir + '/' + r'{cythonize_packages}')

from setuptools import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize('{filename}', language_level='3'))
