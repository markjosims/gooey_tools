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
        return inner_f()
    
    @wraps(f)
    def inner_cli(*args, **kwargs):
        return f(*args, **kwargs)


    if not callable(f):
        return HybridGooey(f, **gkwargs)
    if GUI:
        return inner_gui
    return inner_cli