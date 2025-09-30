import mpmath as mp
from collections import defaultdict
import networkx as nx
from itertools import combinations

from rt_search.analysis_stage.subspaces.searchable import Searchable
from rt_search.analysis_stage.analysis_scheme import AnalyzerModScheme
from rt_search.configs.db_usages import DBUsages
from .errors import UnknownConstant
from rt_search.db_stage.db_scheme import DBModScheme
from rt_search.search_stage.searcher_scheme import SearcherModScheme
from rt_search.utils.types import *
from rt_search.utils.logger import Logger
from rt_search.configs import (
    system as sys_config
)
from rt_search.configs import database as db_config


class System:
    """
    configurations:
    * list of constants to search for
    * what features we are interested in (delta, eigenvalues, etc.)
    * export - to where and at which stages
    * import - from where and at which stage
    * modules config - ()
    """

    def __init__(self,
                 dbs: List[DBModScheme],
                 analyzers: List[Type[AnalyzerModScheme]],
                 searcher: Type[SearcherModScheme]):
        self.dbs = dbs
        self.analyzers = analyzers  # TODO: we might want to allow multiple analyzers so check this later!
        self.searcher = searcher
        if db_config.USAGE != DBUsages.RETRIEVE_DATA and len(dbs) > 1:
            raise ValueError("Multiple DBModConnector instances are not allowed when not retrieving data from DBs.")

    def run(self, constants: List[str] | str = None):
        """
        Run the system given the constants to search for.
        :param constants: if None, search for constants defined in the configuration file in 'configs.database.py'.
        :return:
        """
        if not constants:
            constants = sys_config.CONSTANTS
        elif isinstance(constants, str):
            constants = [constants]

        constants = self.get_constants(constants)
        cmf_data = DBModScheme.aggregate(self.dbs, list(constants.keys()), True)

        for constant, funcs in cmf_data.items():
            functions = '\n'
            for i, func in enumerate(funcs):
                functions += f'{i+1}. {func}\n'
            Logger(
                f'Searching for {constant} using inspiration functions: {functions}', Logger.Levels.info
            ).log(msg_prefix='\n')

        analyzers_results = [analyzer(cmf_data).execute() for analyzer in self.analyzers]
        priorities = self.__aggregate_analyzers(analyzers_results)
        results = dict()
        for const in priorities.keys():
            s = self.searcher(priorities[const], True)
            results[const] = s.execute()

        print(results)  # TODO: remove this
        for const in priorities.keys():
            best_delta = -sp.oo
            best_sv = None
            best_space = None
            for space, dms in results[const].items():
                delta, sv = dms.best_delta()
                if delta is None:
                    continue
                if best_delta < delta:
                    best_delta, best_sv = delta, sv
                    best_space = space
            Logger(
                f'Best delta for "{const}": {best_delta} in trajectory: {best_sv} in searchable: {best_space}',
                Logger.Levels.info
            ).log()

    @staticmethod
    def validate_constant(constant: str, throw: bool = False) -> bool:
        try:
            System.get_const_as_sp(constant)
            return True
        except UnknownConstant as e:
            if throw:
                raise e
            return False

    @staticmethod
    def get_const_as_mpf(constant: str) -> mp.mpf:
        try:
            constant = sys_config.SYMPY_TO_MPMATH[constant]
        except Exception:
            raise UnknownConstant(constant + UnknownConstant.default_msg)

        pieces = constant.split("-")
        if len(pieces) == 1:
            try:
                return getattr(sp, constant)
            except Exception:
                raise UnknownConstant(constant + UnknownConstant.default_msg)

        n = int(pieces[1])
        try:
            return getattr(sp, constant)(n)
        except Exception:
            raise UnknownConstant(constant + UnknownConstant.default_msg)

    @staticmethod
    def get_const_as_sp(constant: str):
        pieces = constant.split("-")
        if len(pieces) == 1:
            try:
                return getattr(sp, constant)
            except Exception:
                raise UnknownConstant(constant + UnknownConstant.default_msg)

        n = int(pieces[1])
        try:
            return getattr(sp, constant)(n)
        except Exception:
            raise UnknownConstant(constant + UnknownConstant.default_msg)

    @staticmethod
    def get_constants(constants: List[str] | str):
        if isinstance(constants, str):
            constants = [constants]
        return {c: System.get_const_as_sp(c) for c in constants}

    @staticmethod
    def __aggregate_analyzers(dicts: List[Dict[str, List[Searchable]]]) -> Dict[str, List[Searchable]]:
        all_keys = set().union(*dicts)
        result = {}

        for key in all_keys:
            lists = [d[key] for d in dicts if key in d]
            prefs = defaultdict(int)
            searchables = set().union(*lists)

            # Count preferences
            for lst in lists:
                for i, a in enumerate(lst[:-1]):
                    for j, b in enumerate(lst[i + 1:]):
                        prefs[(a, b)] += 1  #(j - i) * 1. / len(lst)

            G = nx.DiGraph()
            G.add_nodes_from(searchables)
            for a, b in combinations(searchables, 2):
                if prefs[(a, b)] > prefs[(b, a)]:
                    G.add_edge(a, b)
                elif prefs[(a, b)] < prefs[(b, a)]:
                    G.add_edge(b, a)
                else:
                    if hash(a) > hash(b):
                        G.add_edge(a, b)
                    else:
                        G.add_edge(b, a)

            try:
                consensus = list(nx.topological_sort(G))
            except nx.NetworkXUnfeasible:
                raise Exception('This was not supposed to happen')
                # Cycles = ties, break them by degree or fallback
                # consensus = sorted(searchables, key=lambda x: -sum(prefs[(x, y)] for y in searchables if x != y))
            result[key] = consensus
        return result
