from abc import ABC, abstractmethod
from utils.util_types import *


class Searchable(ABC):
    @abstractmethod
    def search(self, start: Position, trajectories: List[Position] | Position):
        # TODO: deside what this should return. I guess we want to return delta, eigenvalues, rho and more data
        raise NotImplementedError

    @abstractmethod
    def get_anchor(self) -> Position:
        """
        Computes a starting point for the search.
        :return: The starting point
        """
        raise NotImplementedError

    @abstractmethod
    def get_trajectory_generator(self,
                                 generator_type: str = 'sphere',
                                 *args) -> Callable[[int, Position], List[Position]]:
        """
        Create a trajectory generator for the searchable object -
        the generator will create a set of valid trajectories for the search.
        :param generator_type: One of the following: sphere, cube, random, hyperplane
        :return: A trajectory generator function that will return a set of trajectories based on the generator_type
            and the number of trajectories requested.
        """
        raise NotImplementedError
