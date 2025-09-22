from configs.db_usages import DBUsages
from module import Module
from s_db.db_connector import DBModConnector
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

    def __init__(self, constant: str, dbmods: List[DBModConnector]):
        self.constant = constant
        self.dbs = dbmods
        if sys_config.DB_USAGE != DBUsages.RETRIEVE_DATA and len(dbmods) > 1:
            raise ValueError("Multiple DBModConnector instances are not allowed when not retrieving data from DBs.")

    def run(self):
        results = []
        for db in self.dbs:
            results.append(db.execute())
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
