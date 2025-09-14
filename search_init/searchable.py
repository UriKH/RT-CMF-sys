from abc import ABC, abstractmethod
from utils.util_types import *


class Searchable(ABC):
    @abstractmethod
    def search(self, start: Point, trajectories: List[Trajectory] | Trajectory):
        # TODO: deside what this should return. I guess we want to return delta, eigenvalues, rho and more data
        pass

