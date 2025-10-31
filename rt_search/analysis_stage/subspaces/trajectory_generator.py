from rt_search.utils.IO.exports import JSONExportable
from rt_search.utils.IO.imports import JSONImportable
from rt_search.utils.types import *
from rt_search.utils.geometry.point_generator import PointGenerator
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rt_search.analysis_stage.subspaces.searchable import Searchable


@dataclass
class PointGroup(JSONExportable):
    method: str
    dim: int
    primitive: bool
    space: Optional["Searchable"] = None

    def __hash__(self):
        return hash((self.method, self.dim, self.primitive, self.space))

    def to_json_obj(self):
        return {
            'method': self.method,
            'dim': self.dim,
            'primitive': self.primitive,
            'space': self.space if self.space is None else self.space.to_json_obj()
        }


class TrajectoryGenerator(JSONImportable, JSONExportable):
    def __init__(self, symbols, pool: Optional[ProcessPoolExecutor] = None):
        self.symbols = symbols
        self.dim = len(symbols)
        self.point_groups: Dict[PointGroup, Set[Tuple[int, ...]]] = dict()
        # self.pool = ProcessPoolExecutor() if pool is None else pool

    def get_trajectories(self, method: str, length: int, as_primitive: bool):
        group = PointGroup(method, self.dim, as_primitive)
        if group not in self.point_groups:
            self.point_groups[group] = PointGenerator.generate_via_shape(
                length, self.dim, method, as_primitive, False
            )
        return self.point_groups[group]

    @classmethod
    def from_json_obj(cls, src: dict):
        return cls([sp.sympify(sym) for sym in src['symbols']])

    def to_json_obj(self) -> dict | list:
        return {
            'symbols': sp.srepr(self.symbols),
            'dim': self.dim
        }

    # def sort_trajectories_to_searchables(self, group: PointGroup,
    #                                      start_points: List[Position],
    #                                      searchables: List[Searchable]) -> Optional[Dict[Searchable, List[Position]]]:
    #     if group not in self.point_groups:
    #         return None
    #
    #     if len(start_points) != len(searchables):
    #         raise Exception(f"start_points and searchables must have the same length")
    #
    #     sorted_points = dict()
    #     for space, start in zip(searchables, start_points):
    #         if not space.in_space(start):
    #             raise Exception(f'start point must be in the matching searchable space')
    #
    #         res = self.pool.map(
    #             partial(space.trajectory_in_space, start=start),
    #             self.point_groups[group],
    #             chunksize=200
    #         )
    #         sorted_points[space] = {t for valid, t in zip(res, self.point_groups[group]) if valid}
    #     return sorted_points
