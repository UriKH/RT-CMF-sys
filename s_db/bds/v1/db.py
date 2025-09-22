from s_db.bds.v1.config import *
from s_db.functions.formatter import Formatter
from s_db.errors import *
import s_db.functions as functions
from s_db.functions.config import *
from utils.util_types import *

from peewee import SqliteDatabase, Model, CharField
import json
from tqdm import tqdm


class DB:
    """
    Local sqlite database manager.

    Given a constant, the manager is in charge of storing and retrieving CMFs of the corresponding
    inspiration functions.

    The important data of each inspiration function is stored in the database as a JSON string.
        * type: The name of the class of the inspiration function.
        * data: The data of the inspiration function.
        In the data section are also stored the shifts in starting point in the CMF (None if not specified)
    """

    class Table(Model):
        constant = CharField(primary_key=True)
        family = CharField()

    def __init__(self, path: Optional[str] = DEFAULT_PATH) -> None:
        """
        Initialize the connection to the database.
        :param path: Path to the database file.
        """
        self.db = SqliteDatabase(path)
        self.db.bind([DB.Table])
        self.db.connect()
        self.db.create_tables([DB.Table], safe=True)

    def __del__(self) -> None:
        """
        Make sure the connection is closed when the object is destroyed.
        """
        self.db.close()

    def select(self, constant: str) -> CMFlist:
        """
        Retrieve the CMFs of the inspiration functions corresponding to the given constant.
        :param constant: The constant for which to retrieve the CMFs.
        :return: A list of tuples (CMF, shifts) for each inspiration function.
        """
        data = self.__get_as_json(constant)
        cmfs = []
        for func_json in tqdm((data if data else []), desc="Loading CMFs from DB"):
            cmfs.append(
                getattr(functions, func_json[TYPE_ANNOTATE]).from_json(json.dumps(func_json[DATA_ANNOTATE])).to_cmf()
            )
        return cmfs

    def update(self,
               constant: str,
               funcs: List[Formatter] | Formatter,
               replace=False) -> None:
        """
        Set the inspiration functions corresponding to the given constant.
        :param constant: The constant for which to retrieve the CMFs.
        :param funcs: The collection of inspiration-functions.
        :param replace: If true, replace the existing inspiration functions.
        :raises ConstantAlreadyExists: If the constant already exists and replace is false.
        """
        if isinstance(funcs, Formatter):
            funcs = [funcs]
        if self.Table.select().where(self.Table.constant == constant).exists() and not replace:
            raise ConstantAlreadyExists()
        self.Table.replace(constant=constant, family=json.dumps([func.to_db_json() for func in funcs])).execute()

    def add_inspiration_function(self, constant: str, func: Formatter) -> None:
        """
        Adds an inspiration function corresponding to a given constant to the database.
        :param constant: The constant for which to update the inspiration functions.
        :param func: The inspiration function to add.
        :raise FunctionAlreadyExists: If the inspiration function is already defined.
        """
        data = self.__get_as_json(constant)
        if self.__check_if_defined(func, data):
            raise FunctionAlreadyExists()
        data.append(func.to_db_json())
        DB.Table.replace(constant=constant, family=json.dumps(data)).execute()

    def remove_inspiration_function(self, constant: str, func: Formatter) -> None:
        """
        Removes an inspiration function corresponding to a given constant from the database.
        :param constant: The constant for which to update the inspiration functions.
        :param func: The inspiration function to be removed.
        :raise FunctionDoesNotExist: If the inspiration function is not defined.
        """
        data = self.__get_as_json(constant)
        if not self.__check_if_defined(func, data):
            raise FunctionDoesNotExist()
        data.remove(func.to_db_json())
        self.Table.replace(constant=constant, family=json.dumps(data)).execute()

    def __get_as_json(self, constant: str) -> List[Dict]:
        query = self.Table.select().where(self.Table.constant == constant)
        data = query.first()
        if not data:
            raise ConstantDoesNotExist()
        return json.loads(data.family)

    @staticmethod
    def __check_if_defined(func: Formatter, data: List[Dict]) -> bool:
        if not data:
            return True

        for func_json in data:
            if func.to_db_json() == func_json:
                return True
        return False
