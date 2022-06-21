from argsense import cli
from lk_utils import relpath


@cli.cmd()
def init(directory='.'):
    """
    Initialize project with template config file.
    
    kwargs:
        directory (-d):
            Create a [cyan]"pyproject.json"[/] under this directory.
            If directory not exists, will create it.
            If directory parameter is not given, will use [magenta]current -
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


@cli.cmd()
def build(pyproject_file='./pyproject.json'):
    """
    Start building application from pyproject config file.
    
    kwargs:
        pyproject_file (-f):
            Choose a pyproject config file. Accepts ".json", ".yaml", ".toml" -
            formats.
            If parameter is not given, will use [magenta]"./pyproject.json"[/] -
            as default.
    """
    from os.path import exists
    assert exists(pyproject_file)
    
    from .main import full_build
    full_build(pyproject_file)


@cli.cmd()
def gui():
    """
    Launch PyPortable Installer GUI. [red](This is an experimental feature.)[/]
    """
    from .user_interface import gui_on_psg
    gui_on_psg.main()


if __name__ == '__main__':
    cli.run()
