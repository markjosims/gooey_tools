from typing import Optional, Sequence, Generator, Any, Iterable, Callable, Union
from argparse import ArgumentParser, Action, _ArgumentGroup
from time import sleep
from tqdm import tqdm
from inspect import signature
import io
import os
from gooey import Gooey, GooeyParser
from functools import wraps

GUI = os.environ.get('GUI')

def HybridGooey(f: Optional[Callable] = None, **gkwargs):
    """
    Wraps f with Gooey if GUI environment variable is truthy,
    else returns f.
    """
    @wraps(f)
    def inner_gui(*args, **kwargs):
        @Gooey(**gkwargs)
        def inner_f(*args, **kwargs):
            return f(*args, **kwargs)
        return inner_f(*args, **kwargs)
    
    @wraps(f)
    def inner_cli(*args, **kwargs):
        return f(*args, **kwargs)


    def inner_nofunc(f):
        return HybridGooey(f, **gkwargs)

    if not callable(f):
        return inner_nofunc
    if GUI:
        return inner_gui
    return inner_cli

def HybridGooeyParser(*args, **kwargs) -> Union[ArgumentParser, GooeyParser]:
    """
    Returns argparse.ArgumentParser or gooey.GooeyParser depending on environment.
    """
    if GUI:
        return GooeyParser(*args, **kwargs)
    return ArgumentParser(*args, **kwargs)

def is_valid_file(parser: ArgumentParser, arg: str) -> str:
    """
    Return error if filepath not found, return filepath otherwise.
    """
    if not os.path.exists(arg):
        parser.error("The file %s does not exist" % arg)
    else:
        return arg
    
def is_valid_dir(parser: ArgumentParser, arg: str) -> str:
    """
    Return error if directory path not found, return filepath otherwise.
    """
    if not os.path.isdir(arg):
        parser.error("The folder %s does not exist" % arg)
    else:
        return arg

def add_hybrid_arg(
        parser: Union[ArgumentParser, GooeyParser],
        *args,
        group: Optional[_ArgumentGroup] = None,
        **kwargs,
    ) -> Action:
    """
    Add argument to parser and return.
    If using _ArgumentGroup, pass _ArgumentGroup to group arg
    and the parent Argument/GooeyParser to the parser arg
    since _ArgumentGroup does not support type validation.
    If type is 'file' or 'folder', replace with an appropriate validation function
    and sets widget arg automatically.
    If in CLI environment, remove any Gooey-specific args to avoid a KeyError.
    """
    argtype = kwargs.pop('type', None)
    if argtype == 'file':
        kwargs['type'] = lambda x: is_valid_file(parser, x)
        kwargs['widget'] = 'FileChooser'
    if argtype == 'filepath':
        kwargs['type'] = str
        kwargs['widget'] = 'FileChooser'
    if (argtype == 'folder') or (argtype == 'dir'):
        kwargs['type'] = lambda x: is_valid_dir(parser, x)
        kwargs['widget'] = 'DirChooser'
    if (argtype == 'folderpath') or (argtype == 'dirpath'):
        kwargs['type'] = str
        kwargs['widget'] = 'DirChooser'

    if not GUI:
        kwargs.pop('widget', None)
        # can't use metavar w/ boolean args w/ argparse
        if kwargs.get('action', None) in ('store_true', 'store_false'):
            kwargs.pop('metavar', None)

    if group:
        return group.add_argument(*args, **kwargs)
    return parser.add_argument(*args, **kwargs)

def tqdm_gooey(
        iterable: Iterable,
        desc: str = 'Progress',
        **kwargs,
    ) -> Generator[Any, None, None]:
    """
    Wraps iterable in a tqdm object.
    In a GUI environment, pass tqdm progress strings to a StringIO
    and print manually in order to work with Gooey.
    """
    if GUI:
        progress_bar_output = io.StringIO()
        for iter_tup in tqdm(iterable, file=progress_bar_output, desc=desc, **kwargs):
            prog = progress_bar_output.getvalue().split('\r')[-1].strip()
            print(prog)
            yield iter_tup
    else:
        for iter_tup in tqdm(iterable, desc=desc, **kwargs):
            yield iter_tup

def gooey_tqdm_write(*args, **kwargs):
    """
    Due to the interaction of tqdm and Gooey,
    print should be used in a GUI environment
    where tqdm.write might otherwise be favored.
    """
    if GUI:
        return print(*args, **kwargs)
    return tqdm.write(*args, **kwargs)