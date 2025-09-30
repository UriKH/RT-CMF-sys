from .db import DB
from ...db_scheme import DBModScheme
from ...errors import MissingPath
from . import config as v1_config

import rt_search.configs.database as db_config
import rt_search.configs.system as sys_config
from rt_search.utils.types import *
from rt_search.system.module import CatchErrorInModule


class DBModV1(DBModScheme):
    def __init__(self, path: Optional[str] = v1_config.DEFAULT_PATH, json_path: Optional[str] = None):
        super().__init__(
            description='Database module for inspiration function management',
            version='1'
        )
        self.db = DB(path)
        self.json_path = json_path

    @CatchErrorInModule(with_trace=sys_config.MODULE_ERROR_SHOW_TRACE, fatal=True)
    def execute(self, constants: Optional[List[str] | str] = None) -> Dict[str, CMFlist] | None:
        def classify_usage(usage: db_config.DBUsages) -> Optional[dict]:
            match usage:
                case db_config.DBUsages.RETRIEVE_DATA:
                    # if not v1_config.MULTIPLE_CONSTANTS and len(constants) > 1:
                    #     raise ValueError("Multiple constants are not allowed when retrieving data from DB.")
                    return {constant: self.db.select(constant) for constant in constants}
                case db_config.DBUsages.STORE_DATA:
                    try:
                        if not self.json_path:
                            raise MissingPath(MissingPath.default_msg)
                        self.db.from_json(self.json_path)
                    except Exception as e:
                        raise e
                case _:
                    raise ValueError(f"Invalid usage: {usage.name} ")

        if not (usage := db_config.USAGE) in v1_config.ALLOWED_USAGES:
            raise ValueError(f"Invalid usage: {usage.name} "
                             f"usages are: {[usage.name for usage in v1_config.ALLOWED_USAGES]}")
        if constants is None:
            constants = sys_config.CONSTANTS
        elif isinstance(constants, str):
            constants = [constants]
        match usage:
            case db_config.DBUsages.STORE_THEN_RETRIEVE:
                classify_usage(db_config.DBUsages.STORE_DATA)
                return classify_usage(db_config.DBUsages.RETRIEVE_DATA)
            case db_config.DBUsages.RETRIEVE_DATA:
                return classify_usage(usage)
            case _:
                raise NotImplementedError(f"Invalid usage: {usage.name} ")

    def format_result(self, result) -> Dict[str, CMFlist]:
        return result
