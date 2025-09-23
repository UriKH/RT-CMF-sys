from configs.db_usages import DBUsages
from module import Module
from db_stage.db_scheme import DBModScheme
from utils.util_types import *
import configs.system as sys_config


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
                 dbs: List[Tuple[Type[DBModScheme], str]],
                 analyzers: List[Module] = None,
                 searchers: List[Module] = None):
        self.dbs = []
        for db in dbs:
            if not issubclass(db[0], DBModScheme):
                raise ValueError(f"Invalid DBModConnector instance: {db}")
            self.dbs.append(db[0](db[1]))

        if sys_config.DB_USAGE != DBUsages.RETRIEVE_DATA and len(dbs) > 1:
            raise ValueError("Multiple DBModConnector instances are not allowed when not retrieving data from DBs.")

    def run(self, constants: List[str] | str = None):
        """
        Run the system given the constants to search for.
        :param constants: if None, search for constants defined in the configuration file in 'configs.database.py'.
        :return:
        """
        if isinstance(constants, str):
            constants = [constants]
        cmf_data = DBModScheme.aggregate(self.dbs, constants)
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

