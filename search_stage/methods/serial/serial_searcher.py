from idna import valid_string_length
from sympy.polys.subresultants_qq_zz import find_degree

from analysis_stage.subspaces.searchable import Searchable
from search_stage.data_manager import *
from search_stage.searcher_scheme import SearchMethod
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
from ramanujantools import matrix as rtm


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
                 deep_search: bool = True):     # TODO: we don't use deep_search and share_data, for latewr usage...
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
    def _search_worker(sv, data_manager: DataManager,
                       cmf: CMF, constant: str,
                       use_LIReC: bool,
                       parallel: bool = False,
                       find_limit: bool = True,
                       find_eigen_values: bool = True,
                       find_gcd_slope: bool = True
                       ):
        def h_calc_walk_values(traj_m) -> Tuple[List, Exception | None]:
            values = None
            error = None
            try:
                walked = traj_m.walk({n: 1}, 100, {n: 0})
                walked = walked.inv().T
                t1_col = (walked / walked[0, 0]).col(0)
                values = [v for v in t1_col[1:]]
            except Exception as e:
                error = e
            finally:
                return values, error

        def h_identify(values):
            error = None
            simpified = None
            try:
                res = db.identify(values)
                if res:
                    res = res[0]
                    res.include_isolated = 0
                    res = '('.join(str(res).split('(')[:-1])
                    simpified = sp.sympify(res)
                else:
                    raise Exception(f'Could not identify')
            except Exception as e:
                error = e
            finally:
                return simpified, error

        def h_calc_delta(estimated, constant: str):
            delta = None
            error = None
            try:
                error_v = sp.Abs(estimated - System.get_const_as_sp(constant).evalf(30000))
                denom = sp.denom(estimated)
                delta = -1 - sp.log(error_v) / sp.log(denom)
            except Exception as e:
                error = e
            finally:
                return delta, error

        n = sp.symbols('n')
        start, t = sv

        if SearchVector(start, t) in data_manager:
            return None

        sv = SearchVector(start, t)
        sd = SearchData(sv)

        traj_m = cmf.trajectory_matrix(
            trajectory=t,
            start=start
        )
        try:
            if find_limit:
                limit = traj_m.limit({n: 1}, 2000, {n: 0})
                sd.limit = float(limit.as_float())
        except Exception as e:
            # TODO: add trace logging to some log file
            Logger(
                f'Exception {e.__class__.__name__}: "{e}" encountered while calculating limit '
                f'(trajectory ignored in stats): '
                f'\n> start: {start}\n> trajectory: {t}\n> matrix {traj_m}',
                Logger.Levels.exception
            ).log(msg_prefix='\n')
            return None

        try:
            if find_eigen_values:
                sd.ev = traj_m.eigenvals()
        except Exception as e:
            sd.errors['eigen_values'] = e

        try:
            if find_gcd_slope:
                sd.gcd_slope = traj_m.gcd_slope()
                sd.gcd_slope = float(sd.gcd_slope) if parallel else sd.gcd_slope
        except Exception as e:
            sd.errors['gcd_slope'] = e

        mp.mp.dps = 400

        if not use_LIReC:
            try:
                sd.delta = limit.delta(System.get_const_as_mpf(constant))
                if sd.delta in (mp.mpf("inf"), mp.mpf("-inf")) and parallel:  # TODO: delta is a float!
                    sd.delta = str(sd.delta)
            except Exception as e:
                sd.errors['delta'] = e
            try:
                sd.initial_values = limit.identify(System.get_const_as_mpf(constant))
            except Exception as e:
                sd.errors['initial_values'] = e
            finally:
                return sd

        values, error = h_calc_walk_values(traj_m)
        if error is not None:
            sd.errors['delta'] = error
            sd.errors['initial_values'] = error
            return sd

        simpified, error = h_identify([System.get_const_as_sp(constant).evalf(300)] + values)
        if error is not None:
            sd.errors['delta'] = error
            sd.errors['initial_values'] = error
            return sd

        sd.LIReC_identify = True
        symbols = sp.symbols(f'c:{len(values) + 1}')[1:]
        estimated = simpified.subs({sym: val for sym, val in zip(symbols, values)})
        delta, error = h_calc_delta(estimated, constant)
        if error is not None:
            sd.errors['delta'] = error
        else:
            sd.delta = float(SerialSearcher.sympy_to_mpmath(delta))

        a, b = SerialSearcher.fraction_to_vectors(sp.fraction(simpified), symbols)
        sd.initial_values = rtm.Matrix([a, b])
        return sd

    def search(self,
               starts: Optional[Position | List[Position]] = None,
               partial_search_factor: float = 1,
               find_limit: bool = True,
               find_eigen_values: bool = True,
               find_gcd_slope: bool = True) -> DataManager:
        if partial_search_factor > 1 or partial_search_factor < 0:
            raise ValueError("partial_search_factor must be between 0 and 1")
        if not starts:
            starts = self.space.choose_start_point()
            if starts is None:
                Logger(
                    f'Could not provide a valid start point automatically', Logger.Levels.warning,
                    condition=analysis_config.WARN_ON_EMPTY_SHARDS
                ).log()
                return DataManager(self.use_LIReC)
        if isinstance(starts, Position):
            starts = [starts]

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
                        parallel=True,
                        find_limit=find_limit,
                        find_eigen_values=find_eigen_values,
                        find_gcd_slope=find_gcd_slope
                        ),
                pairs, chunksize=search_config.SEARCH_VECTOR_CHUNK)
            for res in results:
                if res:
                    res.gcd_slope = mp.mpf(res.gcd_slope) if res.gcd_slope else None
                    res.delta = mp.mpf(res.delta) if isinstance(res.delta, str) else res.delta
                    self.data_manager[res.sv] = res
        else:
            for start in starts:
                for t in trajectories:
                    sd = self._search_worker(
                        (start, t), self.data_manager, self.space.cmf, self.const_name, self.use_LIReC,
                        find_limit=find_limit,
                        find_eigen_values=find_eigen_values,
                        find_gcd_slope=find_gcd_slope
                    )
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

    @staticmethod
    def sympy_to_mpmath(x):
        if x is sp.zoo:
            return mp.mpf('inf')
        elif x.is_infinite:
            if x == sp.oo:
                return mp.mpf('inf')
            elif x == -sp.oo:
                return mp.mpf('-inf')
            else:
                return mp.mpf('-inf')  # zoo or directional infinity
        else:
            return mp.mpf(str(x.evalf(500)))

    @staticmethod
    def fraction_to_vectors(frac, symbols):
        """
        Convert a tuple (num, den) of sympy expressions into coefficient vectors.

        Args:
            frac: tuple (numerator_expr, denominator_expr)
            symbols: list of sympy symbols [c1, c2, ...]

        Returns:
            (num_vec, den_vec): two lists of coefficients
                Index 0 = constant term
                Index i = coefficient of symbols[i-1]
        """
        num_expr, den_expr = frac

        def expr_to_vector(expr, symbols):
            coeffs = [expr.as_coeff_add(*symbols)[0]]  # constant term
            for s in symbols:
                coeffs.append(expr.coeff(s))
            return [sp.sympify(c) for c in coeffs]

        return expr_to_vector(num_expr, symbols), expr_to_vector(den_expr, symbols)
