from abc import ABC, abstractmethod
from inspect import isclass
from typing import Optional

import functools
import traceback

from utils.logger import Logger


class CatchErrorInModule:
    def __init__(self, with_trace=True):
        self.with_trace = with_trace

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(mod, *args, **kwargs):
            try:
                return func(mod, *args, **kwargs)
            except Exception as e:
                version = None
                if isinstance(mod, Module):
                    name = mod.name
                    version = mod.version
                elif isclass(mod):
                    name = mod.__name__
                else:
                    name = mod.__class__.__name__

                Logger(
                    f'In module {name} [version: {version}] caught {e.__class__.__name__}: {e}',
                    Logger.Levels.exception
                ).log()
                if self.with_trace:
                    traceback.print_exc()
        return wrapper


class Module(ABC):
    def __init__(self,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 version: Optional[str] = None):
        self.name = name if name else self.__class__.__name__
        self.description = description
        self.version = version

    @abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError
