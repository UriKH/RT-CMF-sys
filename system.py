import mpmath as mp

from configs.db_usages import DBUsages
from errors import UnknownConstant
from module import Module
from db_stage.db_scheme import DBModScheme
from utils.util_types import *
import configs.system as sys_config
import configs.database as db_config
from analysis_stage.analysis_scheme import AnalyzerModScheme


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
                 searchers: List[Module] = None):
        self.dbs = dbs
        self.analyzers = analyzers  # TODO: we might want to allow multiple analyzers so check this later!
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
        cmf_data = DBModScheme.aggregate(self.dbs, list(constants.keys()))
        for analyzer in self.analyzers:
            print(analyzer(cmf_data).execute())
        """
        res = None
        for mod in self.mods:
            if mod.config['import']:
                mod.import(.....)
            res = mod.execute(res)
            if mod.config['export']:
                mod.export(res)
            if mod.config['user_input']:
                mod.user_input()
        """
        pass

    @staticmethod
    def validate_constant(constant: str, throw: bool = False) -> bool:
        try:
            System.get_const_as_mpf(constant)
            return True
        except UnknownConstant as e:
            if throw:
                raise e
            return False

    @staticmethod
    def get_const_as_mpf(constant: str) -> mp.mpf:
        try:
            if constant.startswith("zeta-"):
                n = int(constant.split("-")[1])
                return mp.zeta(n)
            return getattr(mp, constant)
        except Exception:
            raise UnknownConstant(constant + UnknownConstant.default_msg)

    @staticmethod
    def get_constants(constants: List[str] | str):
        if isinstance(constants, str):
            constants = [constants]
        return {c: System.get_const_as_mpf(c) for c in constants}
