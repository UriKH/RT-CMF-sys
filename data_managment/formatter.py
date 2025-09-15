from abc import ABC, abstractmethod
from utils.util_types import CMFtup
from dataclasses import dataclass, field
from ramanujantools.position import Position


@dataclass
class Formatter(ABC):
    @abstractmethod
    def from_json(self, s_json: str) -> "Formatter":
        raise NotImplementedError()

    @abstractmethod
    def to_json(self) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError()

    @abstractmethod
    def to_cmf(self) -> CMFtup:
        raise NotImplementedError()
