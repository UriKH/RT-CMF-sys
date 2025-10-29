import os.path
from peewee import SqliteDatabase, Model, CharField
import json

from .config import *
from ...db_scheme import DBScheme
from rt_search.db_stage.funcs.formatter import Formatter
from ...errors import *
from rt_search.db_stage import funcs
from rt_search.db_stage.config import *
from rt_search.utils.types import *
from rt_search.system.system import System


class DB(DBScheme):
    """
    Local sqlite database manager.

    Given a constant, the manager is in charge of storing and retrieving CMFs of the corresponding
    inspiration funcs.

    The important data of each inspiration function is stored in the database as a JSON string.
        * type: The name of the class of the inspiration function.
        * data: The data of the inspiration function.
        In the data section are also stored the shifts in starting point in the CMF (None if not specified)
    """

    class Table(Model):
        constant = CharField(primary_key=True)
        family = CharField(null=False, default="[]")

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
        Retrieve the CMFs of the inspiration funcs corresponding to the given constant.
        :param constant: The constant for which to retrieve the CMFs.
        :return: A list of tuples (CMF, shifts) for each inspiration function.
        """
        data = self.__get_as_json(constant)
        cmfs = []
        for func_json in (data if data else []):
            try:
                cmfs.append(Formatter.from_json_obj(func_json).to_cmf())
            except AttributeError:
                raise NoSuchInspirationFunction(NoSuchInspirationFunction.default_msg + func_json[TYPE_ANNOTATE])
        return cmfs

    def update(self,
               constant: str,
               funcs: List[Formatter] | Formatter,
               override=False) -> None:
        """
        Updates the inspiration funcs corresponding to the given constant.
        :param constant: The constant for which to retrieve the CMFs.
        :param funcs: The collection of inspiration-funcs.
        :param override: If true, replace the existing inspiration funcs.
        :raises ConstantAlreadyExists: If the constant already exists and replace is false.
        """
        if isinstance(funcs, Formatter):
            funcs = [funcs]
        if not self.Table.select().where(self.Table.constant == constant).exists():
            raise ConstantDoesNotExist()
        data = [func.to_json_obj() for func in funcs]
        if not override:
            for fun in self.__get_as_json(constant):
                if fun not in data:
                    data.append(fun)
        self.Table.update({self.Table.family.name: json.dumps(data)}).where(self.Table.constant == constant).execute()

    def replace(self, constant: str, funcs: List[Formatter] | Formatter) -> None:
        if not self.Table.select().where(self.Table.constant == constant).exists():
            self.insert(constant, funcs)
        else:
            self.update(constant, funcs, override=True)

    def append(self, constant: str, funcs: List[Formatter] | Formatter) -> None:
        if not self.Table.select().where(self.Table.constant == constant).exists():
            self.insert(constant, funcs)
        else:
            self.update(constant, funcs, override=False)

    def insert(self, constant: str, funcs: List[Formatter] | Formatter) -> None:
        if isinstance(funcs, Formatter):
            funcs = [funcs]
        if self.Table.select().where(self.Table.constant == constant).exists():
            raise ConstantAlreadyExists(ConstantAlreadyExists.default_msg + constant)
        self.Table.insert(constant=constant, family=json.dumps([func.to_json_obj() for func in funcs])).execute()

    def delete(self,
               constants: str | List[str],
               funcs: Optional[List[Formatter] | Formatter] = None,
               delete_const: bool = False) -> List[str] | None:
        deleted = []
        constants = [constants] if isinstance(constants, str) else constants
        funcs = [funcs] if isinstance(funcs, Formatter) else funcs

        for constant in constants:
            if funcs is None:
                if not delete_const:
                    self.update(constant, [], override=True)
                else:
                    self.Table.delete().where(self.Table.constant == constant).execute()
                    deleted.append(constant)
                continue
            data = self.__get_as_json(constant)
            for func in funcs:
                try:
                    data.remove(func.to_json_obj())
                except ValueError:
                    continue
            (self.Table.update({self.Table.family.name: json.dumps(data)})
             .where(self.Table.constant == constant).execute())
        return deleted

    def clear(self) -> None:
        self.Table.update({self.Table.family.name: '[]'}).execute()

    def add_inspiration_function(self, constant: str, func: Formatter) -> None:
        """
        Adds an inspiration function corresponding to a given constant to the database.
        :param constant: The constant for which to update the inspiration funcs.
        :param func: The inspiration function to add.
        :raise FunctionAlreadyExists: If the inspiration function is already defined.
        """
        data = self.__get_as_json(constant)
        if self.__check_if_defined(func, data):
            raise FunctionAlreadyExists(FunctionAlreadyExists.default_msg + str(func))
        data.append(func.to_json_obj())
        DB.Table.update(constant=constant, family=json.dumps(data)).execute()

    def remove_inspiration_function(self, constant: str, func: Formatter) -> None:
        """
        Removes an inspiration function corresponding to a given constant from the database.
        :param constant: The constant for which to update the inspiration funcs.
        :param func: The inspiration function to be removed.
        :raise FunctionDoesNotExist: If the inspiration function is not defined.
        """
        data = self.__get_as_json(constant)
        if not self.__check_if_defined(func, data):
            raise FunctionDoesNotExist(FunctionDoesNotExist.default_msg + str(func) + f" in {constant}")
        data.remove(func.to_json_obj())
        (self.Table.update({self.Table.family.name: json.dumps(data)})
         .where(self.Table.constant == constant).execute())

    def __get_as_json(self, constant: str) -> List[Dict]:
        query = self.Table.select().where(self.Table.constant == constant)
        data = query.first()
        if not data:
            raise ConstantDoesNotExist(ConstantDoesNotExist.message_prefix + constant)
        return json.loads(data.family)

    @staticmethod
    def __check_if_defined(func: Formatter, data: List[Dict]) -> bool:
        if not data:
            return True

        for func_json in data:
            if func.to_json_obj() == func_json:
                return True
        return False

    def from_json(self, path) -> None:
        """
        Execute limited commands via JSON as the format shown at `JSONError.default_msg`
        :param path: The path to the JSON file.
        """
        data = None
        if not os.path.exists(path):
            raise FormattingError(f"File not found: {path}")

        try:
            with open(path, "r") as f:
                data = json.load(f)
            func = getattr(self, data["command"])
            for d in data['data']:
                for key in d:
                    if key not in ["constant", "data", "kwargs"]:
                        raise FormattingError(FormattingError.bad_format_msg)

                System.validate_constant(d['constant'], throw=True)

                if 'kwargs' in d.keys():
                    func(
                        d["constant"],
                        getattr(funcs, d['data'][TYPE_ANNOTATE]).from_json_obj(json.dumps(d['data'][DATA_ANNOTATE])),
                        **json.loads(d['kwargs'])
                    )
                else:
                    func(
                        d["constant"],
                        getattr(funcs, d['data'][TYPE_ANNOTATE]).from_json_obj(json.dumps(d['data'][DATA_ANNOTATE])),
                    )
        except TypeError as e:
            raise e
        except Exception:
            raise FormattingError(FormattingError.bad_format_msg)
