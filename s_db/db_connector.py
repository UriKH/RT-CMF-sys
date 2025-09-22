from abc import ABC, abstractmethod

from module import Module
from typing import List


class DBModConnector(ABC, Module):
    @classmethod
    def aggregate(cls, dbs: List["DBModConnector"]):
        """
        Aggregate results from multiple DBModConnector instances.
        i.e., combine data from multiple databases
        :param dbs: A list of database instances given by System
        :return:
        """
        # TODO: should this be in system?
        results = set()
        for db in dbs:
            results.update(db.format_result())
        return results

    @abstractmethod
    def format_result(self):
        raise NotImplementedError

