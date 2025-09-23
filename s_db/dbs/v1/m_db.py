from s_db.dbs.v1.db import DB
from s_db.db_scheme import DBModScheme
import s_db.dbs.v1.config as v1_config
import configs.database as db_config
from utils.util_types import *


class DBMod(DBModScheme):
    def __init__(self, path: str = None):
        super().__init__(
            description='Database module for inspiration function management',
            version='1'
        )
        self.db = DB(path)

    def execute(self, constants: Optional[List[str] | str] = None) -> Dict[str, CMFlist] | None:
        if not (usage := db_config.USAGE) in v1_config.ALLOWED_USAGES:
            raise ValueError(f"Invalid usage: {usage.name} "
                             f"usages are: {[usage.name for usage in v1_config.ALLOWED_USAGES]}")
        if constants is None:
            constants = db_config.CONSTANTS

        match usage:
            # TODO: this should be updated when adding more usages to the DB
            case db_config.DBUsages.RETRIEVE_DATA:
                if not v1_config.MULTIPLE_CONSTANTS and len(constants) > 1:
                    raise ValueError("Multiple constants are not allowed when retrieving data from DB.")
                return {constant: self.db.select(constant) for constant in constants}
            # case db_config.DBUsages.STORE_DATA:
            #     return {constant: self.db.update(constant) for constant in constants}
            case _:
                raise ValueError(f"Invalid usage: {usage.name} ")

    def format_result(self, result) -> Dict[str, CMFlist]:
        return result

    def create_from_json(self):
        raise NotImplementedError
