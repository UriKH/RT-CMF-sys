from abc import ABC, abstractmethod
from copy import copy
import mpmath as mp

from ..analysis_stage.subspaces.searchable import Searchable
from .data_manager import DataManager
from ..utils.types import *
from ..system.module import Module


class SearchMethod(ABC):
    def __init__(self,
                 space: Searchable,
                 const: mp.mpf,
                 use_LIReC: bool,
                 data_manager: DataManager = None,
                 share_data: bool = True,
                 deep_search: bool = True):
        self.space = space
        self.const = const
        self.use_LIReC = use_LIReC
        self.best_delta = -1
        self.trajectories = set()
        self.start_points = set()
        self.data_manager = data_manager if not share_data else copy(data_manager)
        self.deep_search = deep_search

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


class SearcherModScheme(Module):
    @staticmethod
    def execute(self):
        raise NotImplementedError
