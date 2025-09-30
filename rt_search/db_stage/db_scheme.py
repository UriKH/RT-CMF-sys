from abc import ABC, abstractmethod
from tqdm import tqdm

from rt_search.system.module import Module, CatchErrorInModule
from rt_search.utils.types import *
from .funcs.formatter import Formatter
from rt_search.configs import system as sys_config


class DBModScheme(Module):
    @classmethod
    @CatchErrorInModule(with_trace=sys_config.MODULE_ERROR_SHOW_TRACE, fatal=True)
    def aggregate(cls, dbs: List["DBModScheme"],
                  constants: Optional[List[str] | str] = None,
                  close_after_exec: bool = False) -> Dict[str, CMFlist]:
        """
        Aggregate results from multiple DBModConnector instances.
        i.e., combine data from multiple databases
        :param dbs: A list of database instances given by System
        :param constants: A list of constants to search for. If None, search for constants defined in the configuration
                            file in 'configs.database.py'.
        :param close_after_exec: Close the database after execution
        :return: A dictionary mapping each constant to a list of CMFs and their respective shifts
        """
        results = dict()
        for db in tqdm(dbs, desc=f'Extracting data from DBs', **sys_config.TQDM_CONFIG):
            if not issubclass(db.__class__, cls):
                raise ValueError(f"Invalid DBModConnector instance: {db}")
            for const, l in db.format_result(db.execute(constants)).items():
                results[const] = list(set(results.get(const, []) + l))
            if close_after_exec:
                del db
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
        Retrieve the CMFs of the inspiration funcs corresponding to the given constant.
        :param constant: The constant for which to retrieve the CMFs.
        :return: A list of tuples (CMF, shifts) for each inspiration function.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, constant: str, funcs: List[Formatter] | Formatter, replace: bool = False) -> None:
        """
        Set the inspiration funcs corresponding to the given constant.
        :param constant: The constant for which to retrieve the CMFs.
        :param funcs: The collection of inspiration-funcs.
        :param replace: If true, replace the existing inspiration funcs.
        :raises ConstantAlreadyExists: If the constant already exists and replace is false.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, constant: str | List[str], funcs: Optional[List[Formatter] | Formatter] = None,
               delete_const: bool = False) -> List[str] | None:
        """
        Remove all the funcs from all the constants provided.
        :param constant: A constant or a list of constants to remove from.
        :param funcs: A function or a list of funcs to remove from the constants. If None, remove the constant.
        :param delete_const: If True, delete the constant from the database if funcs is None.
         Otherwise, just remove all its funcs
        :return: A list of constants that were removed.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all the funcs from all the constants.
        """
        raise NotImplementedError

    @abstractmethod
    def from_json(self, path: str) -> None:
        """
        Execute commands via JSON. View the format in the JSONError class.
        :param path: Path to the JSON file.
        """
        raise NotImplementedError
