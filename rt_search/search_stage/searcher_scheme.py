from abc import ABC, abstractmethod
from copy import copy
import mpmath as mp
import random

from ..analysis_stage.subspaces.searchable import Searchable
from .data_manager import DataManager
from ..utils.types import *
from ..system.module import Module


class SearchMethod(ABC):
    """
    The SearchMethod represents a general search method. \n
    A search method is a minimal object that its sole purpose is to preform the search on a given searchable. \n
    This is the base class for all search methods that will be used by the search modules.
    """

    def __init__(self,
                 space: Searchable,
                 const: mp.mpf,
                 use_LIReC: bool,
                 data_manager: DataManager = None,
                 share_data: bool = True,
                 deep_search: bool = True):
        """
        :param space: A subspace the search method is designated to work search in
        :param const: The constant to look for in the subspace
        :param use_LIReC: Preform search by computing data with LIReC
        :param data_manager: A data manager to be used by the search method
        :param share_data: Decide whether to share data between methods or not
        :param deep_search: Indicate whether to use deep search or not
        """
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

    @staticmethod
    def pick_fraction(lst: list | set, percentage: float) -> list:
        n = len(lst)
        k = round(n * percentage)   # nearest integer
        k = min(max(k, 1), n)       # ensure at least 1 and at most n
        return random.sample(list(lst), k)


class SearcherModScheme(Module):
    """
    A Scheme for all search modules.
    """
    # TODO: fix init values and pass the arguments to exec. there should be no need in constructor in subclasses here
    def __init__(self, name: Optional[str] = None,
                 description: Optional[str] = None,
                 version: Optional[str] = None):
        super().__init__(name, description, version)

    @staticmethod
    def execute(self) -> Dict[Searchable, DataManager]:
        raise NotImplementedError
