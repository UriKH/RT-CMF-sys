from rt_search.utils.types import *
from rt_search.utils.geometry.plane import Plane
from rt_search.utils.geometry.point_generator import PointGenerator
from rt_search.configs import *
from functools import partial
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rt_search.analysis_stage.subspaces.searchable import Searchable


@dataclass
class PointGroup:
    method: str
    dim: int
    primitive: bool
    space: Optional["Searchable"] = None

    def __hash__(self):
        return hash((self.method, self.dim, self.primitive, self.space))


class TrajectoryGenerator:
    def __init__(self, symbols, pool: Optional[ProcessPoolExecutor] = None):
        self.symbols = symbols
        self.dim = len(symbols)
        self.point_groups = dict()
        # self.pool = ProcessPoolExecutor() if pool is None else pool

    def get_trajectories(self, method: str, length: int, as_primitive: bool):
        group = PointGroup(method, self.dim, as_primitive)
        if group not in self.point_groups:
            self.point_groups[group] = PointGenerator.generate_via_shape(
                length, self.dim, method, as_primitive, False
            )
        return self.point_groups[group]

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
