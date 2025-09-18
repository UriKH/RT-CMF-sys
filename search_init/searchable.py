from abc import ABC, abstractmethod
from utils.util_types import *


class Searchable(ABC):
    @abstractmethod
    def is_point_in_space(self, point: Position) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_trajectory_in_space(self, start: Position, trajectory: Position) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate_trajectories(self, start: Position, n: int, mapping: str = 'spherical') -> List[Position]:
        raise NotImplementedError

    @abstractmethod
    def generate_start_points(self, n: int) -> List[Position]:
        raise NotImplementedError

    @abstractmethod
    def add_trajectories(self, trajectories: List[Position] | Position) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_start_points(self, start_points: List[Position] | Position) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_trajectories(self, trajectories: List[Position] | Position) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_start_points(self, start_points: List[Position] | Position) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear_start_points(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear_trajectories(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(self, start: List[Position] | Position, trajectories: List[Position] | Position) -> Dict:
        # TODO: decide what this should return. I guess we want to return delta, eigenvalues, rho and more data
        # TODO: The return value should be an object (of a dataclass) not just a dict
        raise NotImplementedError

    # @abstractmethod
    # def get_anchor(self) -> Position:
    #     """
    #     Computes a starting point for the search.
    #     :return: The starting point
    #     """
    #     raise NotImplementedError
    #
    # @abstractmethod
    # def get_trajectory_generator(self,
    #                              generator_type: str = 'sphere',
    #                              *args) -> Callable[[int, Position], List[Position]]:
    #     """
    #     Create a trajectory generator for the searchable object -
    #     the generator will create a set of valid trajectories for the search.
    #     :param generator_type: One of the following: sphere, cube, random, hyperplane
    #     :return: A trajectory generator function that will return a set of trajectories based on the generator_type
    #         and the number of trajectories requested.
    #     """
    #     raise NotImplementedError
