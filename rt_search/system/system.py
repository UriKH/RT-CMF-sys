import mpmath as mp
from collections import defaultdict
import networkx as nx
from itertools import combinations
from enum import Enum, auto

from ..analysis_stage.subspaces.searchable import Searchable
from ..analysis_stage.analysis_scheme import AnalyzerModScheme
from .errors import UnknownConstant
from ..db_stage.db_scheme import DBModScheme
from rt_search.db_stage.funcs.formatter import Formatter
from ..search_stage.searcher_scheme import SearcherModScheme
from ..utils.types import *
from ..utils.logger import Logger
from ..utils.IO.importer import Importer
from ..configs import (
    sys_config
)


class System:
    """
    A class representing the System itself.
    """

    class RunModes(Enum):
        DB_ONLY = auto()
        JSON_TO_DB = auto()
        JSON_ONLY = auto()
        MANUAL = auto()

    def __init__(self,
                 dbs: List[DBModScheme | str | Dict[str, Formatter]],
                 analyzers: List[Type[AnalyzerModScheme]],
                 searcher: Type[SearcherModScheme]):
        """
        Constructing a system runnable instance for a given combination of modules.
        :param dbs: A list of DBModScheme instances used as sources
        :param analyzers: A list of AnalyzerModScheme types used for prioritization + preparation before the search
        :param searcher: A SearcherModScheme type used to deepen the search done by the analyzers
        """
        self.dbs = dbs
        self.analyzers = analyzers
        self.searcher = searcher
        # if db_config.USAGE != DBUsages.RETRIEVE_DATA and len(dbs) > 1:
        #     raise ValueError("Multiple DBModConnector instances are not allowed when not retrieving data from DBs.")

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
        cmf_data = self.__db_stage(constants)

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

        for const in priorities.keys():
            best_delta = -sp.oo
            best_sv = None
            best_space = None
            for space, dms in results[const].items():
                delta, sv = dms.best_delta
                if delta is None:
                    continue
                if best_delta < delta:
                    best_delta, best_sv = delta, sv
                    best_space = space
            Logger(
                f'Best delta for "{const}": {best_delta} in trajectory: {best_sv} in searchable: {best_space}',
                Logger.Levels.info
            ).log()

    def __db_stage(self, constants: Dict[str, Any]) -> Dict[str, CMFlist]:
        modules = []
        to_import = []
        raw = []
        files = []

        importer = Importer[Formatter]()

        for db in self.dbs:
            match db:
                case DBModScheme():
                    modules.append(db)
                case str():
                    if db.split('.')[-1] == 'json':
                        try:
                            file = open(db, 'r')
                        except Exception as e:
                            raise IOError(f'Unable to open {db}: {e}')
                        files.append(file)
                        to_import.append(file)
                    else:
                        to_import.append(db)
                case dict():
                    if len(db.keys()) != 1 or len(db.values()) != 1 or not isinstance(list(db.values())[0], Formatter):
                        raise ValueError('Dictionary must be of format: {<constant name> : <Formatter subclass>(...)}')
                    raw.append(db)

        imported = importer(to_import, True)
        for file in files:
            file.close()
        cmf_data = DBModScheme.aggregate(modules, list(constants.keys()), True)

        # concatenate the 3 dictionaries
        for const in imported:
            s = {v.to_cmf() for v in imported[const]}
            if const in cmf_data:
                cmf_data[const].union(s)
            else:
                cmf_data[const] = s
        for d in raw:
            for const in d:
                if const in cmf_data:
                    cmf_data[const].add(d[const].to_cmf())
                else:
                    cmf_data[const] = {d[const].to_cmf()}

        # convert back to dict[str, list]
        as_list = dict()
        for k, v in cmf_data.items():
            as_list[k] = list(v)
        return as_list

    def __analysis_stage(self):
        pass

    def __search_stage(self):
        pass

    @staticmethod
    def validate_constant(constant: str, throw: bool = False) -> bool:
        """
        Check if a constant is defined in sympy.
        :param constant: Constant name as string
        :param throw: if True, throw an error on fail
        :raise UnknownConstant if constant is unknown
        :return: True if constant is defined in sympy.
        """
        try:
            System.get_const_as_sp(constant)
            return True
        except UnknownConstant as e:
            if throw:
                raise e
            return False

    @staticmethod
    def get_const_as_mpf(constant: str) -> mp.mpf:
        """
        Convert string to a mpmath.mpf value
        :param constant: Constant name as string
        :raise UnknownConstant if constant is unknown
        :return: the mp.mpf value
        """
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
            return getattr(sp, pieces[0])(n)
        except Exception:
            raise UnknownConstant(constant + UnknownConstant.default_msg)

    @staticmethod
    def get_const_as_sp(constant: str):
        """
        Convert string to a sympy known value
        :param constant: Constant name as string
        :raise UnknownConstant if constant is unknown
        :return: the sympy constant
        """
        pieces = constant.split("-")
        if len(pieces) == 1:
            try:
                return getattr(sp, constant)
            except Exception:
                raise UnknownConstant(constant + UnknownConstant.default_msg)

        n = int(pieces[1])
        try:
            return getattr(sp, pieces[0])(n)
        except Exception:
            raise UnknownConstant(constant + UnknownConstant.default_msg)

    @staticmethod
    def get_constants(constants: List[str] | str):
        """
        Retrieve the constants as sympy constants from strings
        :param constants: A list of constant names
        :return: The sympy constants
        """
        if isinstance(constants, str):
            constants = [constants]
        return {c: System.get_const_as_sp(c) for c in constants}

    @staticmethod
    def __aggregate_analyzers(dicts: List[Dict[str, List[Searchable]]]) -> Dict[str, List[Searchable]]:
        """
        Aggregates the priority lists from several analyzers into one
        :param dicts: A list of mappings from constant name to a list of its relevant subspaces
        :return: The aggregated priority dictionaries
        """
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
            result[key] = consensus
        return result
