from analysis_stage.subspaces.searchable import Searchable
from search_stage.data_manager import *
from search_stage.search_method import SearchMethod
from utils.util_types import *
from utils.point_generator import PointGenerator
from utils.logger import Logger
from configs import (
    analysis as analysis_config,
    search as search_config
)
from system import System


import sympy as sp
import mpmath as mp
import random
from LIReC.db.access import db
from concurrent.futures import ProcessPoolExecutor
from functools import partial


class SerialSearcher(SearchMethod):
    """
    Serial trajectory searcher. \n
    No parallelism or smart co-boundary. \n
    """

    def __init__(self,
                 space: Searchable,
                 constant: mp.mpf,
                 data_manager: DataManager = None,
                 share_data: bool = True,
                 use_LIReC: bool = True,
                 deep_search: bool = True):
        """
        Creates a searcher
        :param space: The space to search in.
        """
        super().__init__(space, constant, use_LIReC, data_manager, share_data, deep_search)
        self.trajectories: Set[Position] = set()
        self.data_manager = data_manager if data_manager else DataManager(use_LIReC)
        self.const_name = space.const_name
        self.parallel = ((not self.deep_search and analysis_config.PARALLEL_TRAJECTORY_MATCHING)
                         or search_config.PARALLEL_SEARCH)
        self.pool = ProcessPoolExecutor() if self.parallel else None

    @Logger('').time_it
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
        if not arbitrary_start:
            Logger(
                f'Could not generate trajectories. Could not provide a valid start point', Logger.Levels.warning,
                condition=analysis_config.WARN_ON_EMPTY_SHARDS
            ).log(msg_prefix='\n')
            return

        trajectories = {Position(t, self.space.symbols) for t in trajectories}
        if not self.deep_search and analysis_config.PARALLEL_TRAJECTORY_MATCHING:
            res = self.pool.map(partial(self.space.trajectory_in_space, start=arbitrary_start), trajectories, chunksize=200)
            self.trajectories.update({t for valid, t in zip(res, trajectories) if valid})
        else:
            self.trajectories.update({t for t in trajectories if self.space.trajectory_in_space(t, arbitrary_start)})

    @staticmethod
    def pick_fraction(lst: list | set, percentage: float) -> list:
        n = len(lst)
        if int(n / percentage) * percentage != n:
            raise ValueError("n must be divisible by k")
        random.seed(42)     # TODO: remove seed
        return random.sample(list(lst), int(n * percentage))

    def generate_start_points(self,
                              method: str,
                              length: int | sp.Rational,
                              n: Optional[int] = None):
        random = n is not None
        starts = [
            Position(s, self.space.symbols) for s in
            PointGenerator.generate_via_shape(length, self.space.dim, method, False, random, n)
            if self.space.in_space(Position(s, self.space.symbols))[0]
        ]
        self.space.add_start_points(starts, filtering=True)

    @staticmethod
    def _search_worker(sv, data_manager: DataManager, cmf: CMF, constant: str, use_LIReC: bool, parallel: bool = False):
        n = sp.symbols('n')
        start, t = sv

        if SearchVector(start, t) in data_manager:
            return None

        traj_m = cmf.trajectory_matrix(
            trajectory=t,
            start=start
        )
        try:
            lim = traj_m.limit({n: 1}, 2000, {n: 0})
        except Exception as e:
            # TODO: add trace logging to some log file
            Logger(
                f'Exception {e.__class__.__name__} encountered while calculating limit '
                f'(trajectory ignored in stats): '
                f'\n> start: {start}\n> trajectory: {t}\n> matrix {traj_m}',
                Logger.Levels.exception
            ).log(msg_prefix='\n')
            return None
        errors = {}
        try:
            delta = lim.delta(System.get_const_as_mpf(constant))
            if delta in (mp.mpf("inf"), mp.mpf("-inf")) and parallel:
                delta = str(delta)
        except Exception as e:
            delta = -1
            errors['delta'] = e

        try:
            ev = traj_m.eigenvals()
        except Exception as e:
            errors['eigen_values'] = e
            ev = dict()

        try:
            gcd_slope = traj_m.gcd_slope()
            gcd_slope = float(gcd_slope) if parallel else gcd_slope
        except Exception as e:
            errors['gcd_slope'] = e
            gcd_slope = None

        try:
            initial_values = lim.identify(System.get_const_as_mpf(constant))
        except Exception as e:
            initial_values = None
            errors['initial_values'] = e

        mp.mp.dps = 400
        LIReC_identify = False
        try:
            if use_LIReC:
                LIReC_identify = len(db.identify([lim.as_float(), constant])) > 0
        except Exception as e:
            errors['LIReC_identify'] = e

        sv = SearchVector(start, t)
        sd = SearchData(sv, lim, delta, ev, gcd_slope, initial_values, LIReC_identify, errors)
        return sd

    @Logger('').time_it
    def search(self,
               starts: Optional[Position | List[Position]] = None,
               partial_search_factor: float = 1) -> DataManager:

        if partial_search_factor > 1 or partial_search_factor < 0:
            raise ValueError("partial_search_factor must be between 0 and 1")
        if not starts:
            starts = self.space.choose_start_point()
            if starts is None:
                Logger(
                    f'Could not provide a valid start point automatically', Logger.Levels.warning,
                    condition=analysis_config.WARN_ON_EMPTY_SHARDS
                ).log()
                return DataManager(self.use_LIReC, empty=True)
        if isinstance(starts, Position):
            starts = [starts]

        n = sp.symbols('n')

        trajectories = self.trajectories
        if partial_search_factor < 1:
            trajectories = set(self.pick_fraction(self.trajectories, partial_search_factor))
            if len(trajectories) == 0:
                Logger(
                    'Too few trajectories, all chosen for search (consider adjusting partial_search_factor)',
                    Logger.Levels.warning
                ).log()
                trajectories = self.trajectories

        if self.parallel:
            pairs = [(start, t) for start in starts for t in trajectories]
            results = self.pool.map(
                partial(self._search_worker,
                        data_manager=self.data_manager,
                        cmf=self.space.cmf,
                        constant=self.const_name,
                        use_LIReC=self.use_LIReC,
                        parallel=True),
                pairs, chunksize=search_config.SEARCH_VECTOR_CHUNK)
            for res in results:
                if res:
                    res.gcd_slope = mp.mpf(res.gcd_slope) if res.gcd_slope else None
                    res.delta = mp.mpf(res.delta) if isinstance(res.delta, str) else res.delta
                    self.data_manager[res.sv] = res
        else:
            for start in starts:
                for t in trajectories:
                    sd = self._search_worker((start, t), self.data_manager, self.space.cmf, self.const_name, self.use_LIReC)
                    self.data_manager[sd.sv] = sd
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
