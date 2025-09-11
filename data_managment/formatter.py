from abc import ABC, abstractmethod
from ramanujantools.cmf import CMF


class Formatter(ABC):
    @abstractmethod
    def from_json(self, s_json: str) -> "Formatter":
        raise NotImplementedError()

    @abstractmethod
    def to_json(self) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def __str__(self):
        raise NotImplementedError()

    @abstractmethod
    def to_cmf(self) -> CMF:
        raise NotImplementedError()
