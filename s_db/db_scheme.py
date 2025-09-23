from abc import ABC, abstractmethod

from module import Module
from utils.util_types import *
from s_db.functions.formatter import Formatter


class DBModScheme(Module):
    @classmethod
    def aggregate(cls, dbs: List["DBModScheme"], constants: Optional[List[str] | str] = None) -> Dict[str, CMFlist]:
        """
        Aggregate results from multiple DBModConnector instances.
        i.e., combine data from multiple databases
        :param dbs: A list of database instances given by System
        :param constants: A list of constants to search for. If None, search for constants defined in the configuration
                            file in 'configs.database.py'.
        :return:
        """
        # TODO: should this be in system?
        results = {}
        for db in dbs:
            if not issubclass(db.__class__, cls):
                raise ValueError(f"Invalid DBModConnector instance: {db}")
            for const, l in db.format_result(db.execute(constants)).items():
                results[const] = list(set(results.get(const, []) + l))
        return results

    @abstractmethod
    def format_result(self, result) -> Dict[str, CMFlist]:
        raise NotImplementedError

    @abstractmethod
    def execute(self, constants: Optional[List[str] | str] = None) -> Dict[str, CMFlist] | None:
        raise NotImplementedError


class DBScheme(ABC):
    @abstractmethod
    def select(self, constant: str) -> CMFlist:
        """
        Retrieve the CMFs of the inspiration functions corresponding to the given constant.
        :param constant: The constant for which to retrieve the CMFs.
        :return: A list of tuples (CMF, shifts) for each inspiration function.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, constant: str, funcs: List[Formatter] | Formatter, replace: bool = False) -> None:
        """
        Set the inspiration functions corresponding to the given constant.
        :param constant: The constant for which to retrieve the CMFs.
        :param funcs: The collection of inspiration-functions.
        :param replace: If true, replace the existing inspiration functions.
        :raises ConstantAlreadyExists: If the constant already exists and replace is false.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, constant: str | List[str], funcs: Optional[List[Formatter] | Formatter] = None,
               delete_const: bool = False) -> List[str] | None:
        """
        Remove all the functions from all the constants provided.
        :param constant: A constant or a list of constants to remove from.
        :param funcs: A function or a list of functions to remove from the constants. If None, remove the constant.
        :param delete_const: If True, delete the constant from the database if funcs is None.
         Otherwise, just remove all its functions
        :return: A list of constants that were removed.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all the functions from all the constants.
        """
        raise NotImplementedError

    @abstractmethod
    def from_json(self, path: str) -> None:
        """
        Execute commands via JSON. View the format in the JSONError class.
        :param path: Path to the JSON file.
        """
        raise NotImplementedError
