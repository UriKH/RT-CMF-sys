from abc import ABC, abstractmethod
from utils.util_types import *


class SearchMethod(ABC):
    def __init__(self):
        self.best_delta = -1
        self.trajectories = set()
        self.start_points = set()

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
