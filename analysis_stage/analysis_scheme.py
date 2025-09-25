from module import Module
from utils.util_types import *

from abc import abstractmethod, ABC


class AnalyzerModScheme(Module):
    @abstractmethod
    def execute(self):
        raise NotImplementedError


class AnalyzerScheme(ABC):
    pass
