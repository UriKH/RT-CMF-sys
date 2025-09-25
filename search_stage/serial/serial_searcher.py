from analysis_stage.subspaces.searchable import Searchable
from search_stage.data_manager import DataManager
from search_stage.search_method import SearchMethod
from utils.util_types import *
from utils.point_generator import PointGenerator

import sympy as sp
import random


class SerialSearcher(SearchMethod):
    """
    Serial trajectory searcher. \n
    No parallelism or smart co-boundary. \n
    """

    def __init__(self,
                 space: Searchable,
                 data_manager: DataManager = None,
                 share_data: bool = True):
        """
        Creates a searcher
        :param space: The space to search in.
        """
        super().__init__(space, data_manager, share_data)
        self.trajectories: Set[Position] = set()

    def generate_trajectories(self,
                              method: str,
                              length: int,
                              n: Optional[int] = None,
                              clear=True):
        random = n is not None
        if clear:
            self.trajectories.clear()
        trajectories = PointGenerator.generate_via_shape(length, self.space.dim, method, True, random, n)
        arbitrary_start = self.space.choose_start_point()
        self.trajectories.update({
            Position(t, self.space.symbols) for t in trajectories if self.space.trajectory_in_space(arbitrary_start, t)
        })

    @staticmethod
    def pick_fraction(lst: list | set, percentage: float) -> list:
        n = len(lst)
        if n % int(1 / percentage) != 0:
            raise ValueError("n must be divisible by k")
        return random.sample(lst, int(n * percentage))

    def generate_start_points(self,
                              method: str,
                              length: int | sp.Rational,
                              n: Optional[int] = None):
        random = n is not None
        starts = [
            Position(s, self.space.symbols) for s in
            PointGenerator.generate_via_shape(length, self.space.dim, method, False, random, n)
        ]
        self.space.add_start_points(starts, filtering=True)

    def search(self,
               starts: Optional[Position | List[Position]] = None,
               partial_search_factor: float = 1):
        if partial_search_factor > 1 or partial_search_factor < 0:
            raise ValueError("partial_search_factor must be between 0 and 1")
        if not starts:
            starts = self.space.choose_start_point()
        if isinstance(starts, Position):
            starts = [starts]

        n = sp.symbols('n')

        trajectories = self.trajectories
        if partial_search_factor < 1:
            trajectories = set(self.pick_fraction(self.trajectories, partial_search_factor))
        for start in starts:
            for t in trajectories:
                traj_m = self.space.cmf.trajectory_matrix(
                    trajectory=t,
                    start=start
                )
                l = traj_m.limit({n: 1}, 2000, {n: 0})
                l.delta()
                # TODO: implement search and data manager
                """
                limit = <COMPUTE LIMIT>     (This should be dependant on type1 / type2 or something doesn't it?)
                delta = <COMPUTE DELTA>
                eigen_values = <COMPUTE EIGEN VALUES>
                rho = <COMPUTE RHO>
                self.data_manager.add_data(start, trajectory, limit, delta, eigen_values, rho)
                """
                # t_mat = self.space.cmf.trajectory_matrix(t, start)
                # limit = self.space.cmf.limit(t, 1000, start)
                pass

    def get_data(self):
        """
        :return:
        """
        """
        return self.data_manager.get_data()
        """
        raise NotImplementedError

    def enrich_trajectories(self):
        raise NotImplementedError
