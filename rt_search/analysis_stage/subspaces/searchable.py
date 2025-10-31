from abc import ABC, abstractmethod

from rt_search.analysis_stage.subspaces.trajectory_generator import TrajectoryGenerator
from rt_search.utils.IO.exports import JSONExportable
from rt_search.utils.IO.imports import JSONImportable
from rt_search.utils.types import *
from rt_search.utils.geometry.position import Position


class Searchable(JSONImportable, JSONExportable):
    def __init__(self, name: str, dim: int, cmf: CMF, symbols: List[sp.Symbol],
                 tg: Optional[TrajectoryGenerator] = None): # TG should not be optional
        self.dim = dim
        self.cmf = cmf
        self.symbols = symbols
        self._start_points: Set[Position] = set()
        self.data = None
        self.const_name = name
        self.tg = tg

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

    def __repr__(self):
        return self.cmf.__repr__()
