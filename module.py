from abc import ABC, abstractmethod
from typing import Optional


class Module(ABC):
    def __init__(self,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 version: Optional[str] = None):
        self.name = name if name else self.__class__.__name__
        self.description = description
        self.version = version

    @abstractmethod
    def execute(self):
        raise NotImplementedError
