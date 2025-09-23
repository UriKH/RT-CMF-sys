from abc import ABC, abstractmethod
from copy import copy

from analysis_stage.subspaces.searchable import Searchable
from search_stage.data_manager import DataManager
from utils.util_types import *


class SearchMethod(ABC):
    def __init__(self,
                 space: Searchable,
                 data_manager: DataManager = None,
                 share_data: bool = True):
        self.space = space
        self.best_delta = -1
        self.trajectories = set()
        self.start_points = set()
        self.data_manager = data_manager if not share_data else copy(data_manager)

    @abstractmethod
    def generate_trajectories(self, method: str, length: int | sp.Rational, n: Optional[int] = None):
        raise NotImplementedError

    @abstractmethod
    def generate_start_points(self, method: str, length: int | sp.Rational, n: Optional[int] = None):
        raise NotImplementedError

    @abstractmethod
    def search(self, starts: Optional[Position | List[Position]] = None):
        raise NotImplementedError

    @abstractmethod
    def get_data(self):
        raise NotImplementedError

    @abstractmethod
    def enrich_trajectories(self):
        raise NotImplementedError
