from s_analysis.subspaces.searchable import Searchable
from s_search.search_method import SearchMethod
from utils.util_types import *
from utils.point_generator import PointGenerator

import sympy as sp


class SerialSearcher(SearchMethod):
    """
    Serial trajectory searcher. \n
    No parallelism or smart co-boundary. \n
    """

    def __init__(self, space: Searchable):
        """
        Creates a searcher
        :param space: The space to search in.
        """
        super().__init__()
        self.space = space
        self.trajectories: Set[Position] = set()

    def generate_trajectories(self,
                              method: str,
                              length: int | sp.Rational,
                              n: Optional[int] = None,
                              clear=True):
        random = n is not None
        if clear:
            self.trajectories.clear()
        trajectories = PointGenerator.generate_via_shape(length, self.space.dim, method, True, random, n)
        arbitrary_start = self.space.choose_start_point()
        self.trajectories.update(
            {Position(t, self.space.symbols) for t in trajectories if self.space.trajectory_in_space(arbitrary_start, t)}
        )

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

    def search(self, starts: Optional[Position | List[Position]] = None):
        if not starts:
            starts = self.space.choose_start_point()
        if isinstance(starts, Position):
            starts = [starts]
        for start in starts:
            for t in self.trajectories:
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
