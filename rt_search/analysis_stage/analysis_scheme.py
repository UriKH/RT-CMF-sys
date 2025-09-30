from rt_search.analysis_stage.subspaces.searchable import Searchable
from rt_search.search_stage.data_manager import DataManager
from rt_search.system.module import Module
from rt_search.utils.types import *

from abc import abstractmethod, ABC


class AnalyzerModScheme(Module):
    @abstractmethod
    def execute(self) -> Dict[str, List[Searchable]]:
        raise NotImplementedError


class AnalyzerScheme(ABC):
    @abstractmethod
    def search(self, method: str, length: int) -> Dict[Searchable, DataManager]:
        raise NotImplementedError

    @abstractmethod
    def prioritize(self, managers: Dict[Searchable, DataManager], ranks: int) -> Dict[Searchable, Dict[str, int]]:
        raise NotImplementedError
