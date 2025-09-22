from abc import ABC, abstractmethod

from module import Module
from utils.util_types import *


class DBModConnector(ABC, Module):
    @classmethod
    def aggregate(cls, dbs: List["DBModConnector"], constants: Optional[List[str] | str] = None) -> Dict[str, CMFlist]:
        """
        Aggregate results from multiple DBModConnector instances.
        i.e., combine data from multiple databases
        :param dbs: A list of database instances given by System
        :return:
        """
        # TODO: should this be in system?
        results = {}
        for db in dbs:
            if not issubclass(db, cls):
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
