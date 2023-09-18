from typing import Optional, Sequence, Generator, Any, Iterable, Callable
from argparse import ArgumentParser
from time import sleep
from tqdm import tqdm
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