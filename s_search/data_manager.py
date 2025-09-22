from utils.util_types import *
from dataclasses import dataclass
import mpmath as mp


@dataclass
class SearchVector:
    start: Position
    trajectory: Position

    def __hash__(self):
        return hash((self.start, self.trajectory))


@dataclass
class SearchData:
    limit: mp.limit
    # TODO: finish this


class DataManager(Dict[SearchVector, Dict]):
    def __init__(self):
        super().__init__()

    def __copy__(self):
        return DataManager()
