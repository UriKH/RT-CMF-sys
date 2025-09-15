from abc import ABC, abstractmethod
from utils.util_types import *


class Searchable(ABC):
    @abstractmethod
    def search(self, start: Position, trajectories: List[Position] | Position):
        # TODO: deside what this should return. I guess we want to return delta, eigenvalues, rho and more data
        pass

