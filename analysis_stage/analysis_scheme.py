from module import Module

from abc import abstractmethod, ABC


class AnalyzerModScheme(Module):
    @abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError


class AnalyzerScheme(ABC):
    pass
