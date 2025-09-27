from abc import ABC, abstractmethod
from utils.util_types import *


class Searchable(ABC):
    def __init__(self, dim: int, cmf: CMF, symbols: List[sp.Symbol]):
        self.dim = dim
        self.cmf = cmf
        self.symbols = symbols
        self._start_points: Set[Position] = set()
        self.data = None

    @abstractmethod
    def in_space(self, point: Position) -> Tuple[bool, Any]:
        raise NotImplementedError

    @abstractmethod
    def trajectory_in_space(self, start: Position, trajectory: Position) -> bool:
        raise NotImplementedError

    @abstractmethod
    def add_start_points(self, start_points: List[Position] | Position, filtering=True) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_start_points(self, start_points: List[Position] | Position) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear_start_points(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def choose_start_point(self) -> Position:
        raise NotImplementedError

    @abstractmethod
    def get_start_points(self) -> Set[Position]:
        raise NotImplementedError

    def has_start_points(self) -> bool:
        return len(self._start_points) > 0
