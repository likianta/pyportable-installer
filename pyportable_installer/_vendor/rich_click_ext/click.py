"""
some predefined configurations for rich-click.
rich-click official website: https://github.com/ewels/rich-click
"""
import typing as t

import rich_click as click

from .docstring_analyser import analyse_docstring
from .extensions import DoNotSortCommands
from .extensions import ArgumentSupportsAddingHelpText
from .extensions import CommandSupportsAddingHelpTextToItsArguments

click.rich_click.SHOW_ARGUMENTS = True
# click.rich_click.STYLE_COMMANDS_PANEL_BORDER = 'cyan'
click.rich_click.USE_RICH_MARKUP = True

__all__ = [
    'group', 'command', 'argument', 'option',
    'grp', 'cmd', 'arg', 'opt'
]


class T:
    Callable = t.Callable
    Decorator = t.Callable
    
    class Docs(t.TypedDict):
        desc: str
        args: t.Dict[str, str]
        options: t.Dict[str, str]
    
    AllFuncDocs = t.Dict[str, Docs]
    
    GroupedObject = t.Optional[DoNotSortCommands]


class FuncDocs:
    
    def __init__(self):
        self.__docs: T.AllFuncDocs = {}
    
    def __call__(self, func: T.Callable) -> T.Docs:
        func_name = func.__name__
        if func_name not in self.__docs:
            doc = func.__doc__ or ''
            doc = analyse_docstring(doc)
            self.__docs[func_name] = doc
            return doc
        return self.__docs[func_name]


__func_docs = FuncDocs()
__grouped_obj: T.GroupedObject = None


def group(*args, **kwargs) -> T.Decorator:
    def decorator(func):
        global __grouped_obj
        __grouped_obj = click.group(
            *args, **kwargs,
            context_settings=dict(help_option_names=['-h', '--help']),
            cls=DoNotSortCommands
        )(func)
        return __grouped_obj
    
    return decorator


def command(*args, group=None, **kwargs) -> T.Decorator:
    global __grouped_obj
    if group is None:
        group = __grouped_obj
    else:
        __grouped_obj = group
    assert group is not None
    
    def decorator(func):
        # add `-h` as alias for `--help`:
        #   https://stackoverflow.com/questions/34182318/python-click-can-you
        #   -make-h-as-an-alias
        return group.command(
            *args, **kwargs,
            cls=CommandSupportsAddingHelpTextToItsArguments,
            context_settings=dict(help_option_names=['-h', '--help']),
            help=__func_docs(func)['desc']
        )(func)
    
    return decorator


def argument(*args, **kwargs) -> T.Decorator:
    def decorator(func):
        # noinspection PyUnresolvedReferences
        doc = __func_docs(func)['args'].get(args[0], '')
        #   e.g. args[0] = 'upload'
        dec = click.argument(*args, **kwargs, help=doc,
                             cls=ArgumentSupportsAddingHelpText)(func)
        return dec
    
    return decorator


def option(*args, **kwargs) -> T.Decorator:
    def decorator(func):
        # noinspection PyUnresolvedReferences
        doc = __func_docs(func)['options'].get(args[0], '')
        #   e.g. args[0] = '--foo'
        dec = click.option(*args, **kwargs, help=doc)(func)
        return dec
    
    return decorator


# alias
grp = group
cmd = command
arg = argument
opt = option
