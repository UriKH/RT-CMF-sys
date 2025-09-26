from analysis_stage.subspaces.searchable import Searchable
from search_stage.data_manager import *
from search_stage.search_method import SearchMethod
from utils.util_types import *
from utils.point_generator import PointGenerator

import sympy as sp
import mpmath as mp
import random


class SerialSearcher(SearchMethod):
    """
    Serial trajectory searcher. \n
    No parallelism or smart co-boundary. \n
    """

    def __init__(self,
                 space: Searchable,
                 constant: mp.mpf,
                 data_manager: DataManager = None,
                 share_data: bool = True):
        """
        Creates a searcher
        :param space: The space to search in.
        """
        super().__init__(space, constant, data_manager, share_data)
        self.trajectories: Set[Position] = set()
        self.data_manager = data_manager if data_manager else DataManager()

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
        if int(n / percentage) * percentage != n:
            raise ValueError("n must be divisible by k")
        return random.sample(list(lst), int(n * percentage))

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
               partial_search_factor: float = 1) -> DataManager:
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
                if SearchVector(start, t) in self.data_manager:
                    continue

                traj_m = self.space.cmf.trajectory_matrix(
                    trajectory=t,
                    start=start
                )
                lim = traj_m.limit({n: 1}, 2000, {n: 0})
                delta = lim.delta(self.const)
                ev = traj_m.eigenvals()
                gcd_slope = traj_m.gcd_slope()
                initial_values = lim.identify(self.const)

                sv = SearchVector(start, t)
                sd = SearchData(sv, lim, delta, ev, gcd_slope, initial_values)
                self.data_manager[sv] = sd
        return self.data_manager

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
