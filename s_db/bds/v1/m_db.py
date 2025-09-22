from s_db.bds.v1.db import DB
from s_db.db_connector import DBModConnector
from utils.util_types import *


class Database(DBModConnector):
    def __init__(self,):
        super().__init__(
            description='Database module for inspiration function management',
            version='1'
        )
        self.db = DB()

    def execute(self, constant: str) -> CMFlist:
        return self.db.select(constant)

    def format_result(self, result, as_type=set):
        match as_type:
            case set():
                return as_type(result)
            case _:
                raise ValueError(f"Invalid type: {as_type}, type must be XXXX")

    def create_from_json(self):
        raise NotImplementedError

    """
    The DB template should allow not only the execution of get() but also updating via terminal and using functions
     manually and external files!
    The system will turn the DB module on and the rest will happen automatically (the only configuration for the system
     will be to choose if interaction is using terminal / external files or function calls)
    """