from lk_utils import relpath
from rich_click import Path

from ._vendor.rich_click_ext import click


@click.grp(help='PyPortable Installer command line interface.')
def cli():
    pass


@click.cmd()
@click.arg('directory', default='.', type=Path())
def init(directory='.'):
    """
    Initialize project with template config file.
    
    args:
        directory:
            Create a [cyan]"pyproject.json"[/] under this directory.
            If directory not exists, will create it.
            If directory parameter is not given, will use [magenta]current
             directory[/].
    """
    import os
    from shutil import copyfile
    
    file_i = relpath('./template/pyproject.json')
    file_o = f'{directory}/pyproject.json'
    
    if not os.path.exists(directory):
        os.mkdir(directory)
    elif os.path.exists(file_o):
        os.remove(file_o)
    copyfile(file_i, file_o)


@click.cmd()
@click.arg('pyproject-file', default='./pyproject.json', type=Path(exists=True))
def build(pyproject_file='./pyproject.json'):
    """
    Start building application from pyproject config file.
    
    args:
        pyproject-file:
            Choose a pyproject config file. Accepts ".json", ".yaml", ".toml"
             formats.
            If parameter is not given, will use [magenta]"./pyproject.json"[/]
             as default.
    """
    from .main import full_build
    full_build(pyproject_file)


@click.cmd()
def gui():
    """
    Launch PyPortable Installer GUI. [dim](experimental feature)[/]
    """
    from .user_interface import gui_on_psg
    gui_on_psg.main()


if __name__ == '__main__':
    cli()
