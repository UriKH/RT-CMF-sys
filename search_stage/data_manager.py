from utils.util_types import *
from dataclasses import dataclass, field
import mpmath as mp


@dataclass
class SearchVector:
    start: Position
    trajectory: Position

    def __hash__(self):
        return hash((self.start, self.trajectory))


@dataclass
class SearchData:
    limit: mp.limit = None
    delta_sequence: List = field(default=list)
    delta: mp.mpf = None
    eigen_values: List = field(default=list)
    gcd_slope: mp.mpf = None
    converges: bool = False


class DataManager(Dict[SearchVector, Dict]):
    def __init__(self, deep_search: bool = True):
        super().__init__()
        self.deep_search = deep_search

    def best_delta(self):
        return None
