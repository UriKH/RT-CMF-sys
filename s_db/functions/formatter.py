from abc import ABC, abstractmethod
from utils.util_types import *
from dataclasses import dataclass
from s_db.functions.config import *


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

    def get_type_name(self) -> str:
        return self.__class__.__name__

    def to_db_json(self) -> Dict[str, Any]:
        return {TYPE_ANNOTATE: self.get_type_name(), DATA_ANNOTATE: self.to_json()}
