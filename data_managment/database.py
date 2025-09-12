from configs.database import *
from data_managment.formatter import Formatter
from data_managment.errors import *
from data_managment.util_types import CMFlist
import data_managment.functions as functions

from peewee import SqliteDatabase, Model, CharField
import json
from typing import Optional


class DBManager:
    """
    Local sqlite database manager.

    Given a constant, the manager is in charge of storing and retrieving CMFs of the corresponding
    inspiration functions.

    The important data of each inspiration function is stored in the database as a JSON string.
        * type: The name of the class of the inspiration function.
        * data: The data of the inspiration function.
        In the data section are also stored the shifts in starting point in the CMF (None if not specified)
    """

    class DB(Model):
        constant = CharField(primary_key=True)
        family = CharField()

    def __init__(self, path: Optional[str] = DEFAULT_PATH):
        """
        Initialize the connection to the database.
        :param path: Path to the database file.
        """
        self.db = SqliteDatabase(path)
        self.db.bind([DBManager.DB])
        self.db.connect()
        self.db.create_tables([DBManager.DB], safe=True)

    def __del__(self) -> None:
        """
        Make sure the connection is closed when the object is destroyed.
        """
        self.db.close()

    def get(self, constant: str) -> CMFlist:
        """
        Retrieve the CMFs of the inspiration functions corresponding to the given constant.
        :param constant: The constant for which to retrieve the CMFs.
        :return: A list of tuples (CMF, shifts) for each inspiration function.
        """
        data = self.__get_as_json(constant)
        cmfs = []
        for func_json in (data if data else []):
            cmfs.append(getattr(functions, func_json['type']).from_json(json.dumps(func_json['data'])).to_cmf())
        return cmfs

    def set(self, constant: str, funcs: list[Formatter] | Formatter, replace=False) -> None:
        """
        Set the inspiration functions corresponding to the given constant.
        :param constant: The constant for which to retrieve the CMFs.
        :param funcs: The collection of inspiration-functions.
        :param replace: If true, replace the existing inspiration functions.
        :raises ConstantAlreadyExists: If the constant already exists and replace is false.
        """
        if isinstance(funcs, Formatter):
            funcs = [funcs]
        if DBManager.DB.select().where(DBManager.DB.constant == constant).exists() and not replace:
            raise ConstantAlreadyExists()

        DBManager.DB.replace(constant=constant, family=json.dumps([func.to_json() for func in funcs])).execute()

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
        data.append(func.to_json())
        DBManager.DB.replace(constant=constant, family=json.dumps(data)).execute()

    def remove_inspiration_function(self, constant: str, func: Formatter) -> None:
        """
        Removes an inspiration function corresponding to a given constant from the database.
        :param constant: The constant for which to update the inspiration functions.
        :param func: The inspiration function to be removed.
        :raise FunctionDoesNotExist: If the inspiration function is not defined.
        """
        data = self.__get_as_json(constant)
        if not self.__check_if_defined(func, data):
            raise FunctionAlreadyExists()
        data.remove(func.to_json())
        DBManager.DB.replace(constant=constant, family=json.dumps(data)).execute()

    def __get_as_json(self, constant: str) -> list[dict]:
        query = DBManager.DB.select().where(DBManager.DB.constant == constant)
        data = query.first()
        if not data:
            raise ConstantDoesNotExist()
        return json.loads(data.family)

    @staticmethod
    def __check_if_defined(func: Formatter, data: list[dict]) -> bool:
        if not data:
            return True

        for func_json in data:
            if func.to_json() == func_json:
                return True
        return False
