from abc import ABC, abstractmethod

from ..types import *

import json
from typing import Protocol, runtime_checkable


@runtime_checkable
class SupportsWrite[T](Protocol):
    def write(self, s: T, *args, **kwargs) -> object: ...


class Exportable(ABC):
    class ExportError(Exception):
        pass

    @abstractmethod
    def export_(self, *args):
        raise NotImplementedError


class JSONExportable(Exportable):
    class JSONExportableError(Exportable.ExportError):
        default_msg = 'Invalid destination type '

    @abstractmethod
    def to_json_obj(self) -> dict | list:
        """
        Convert the object into a JSON like object
        :return: The JSON like object
        """
        raise NotImplementedError

    def to_json(self,
                dst: Optional[str | SupportsWrite[str]] = None,
                return_anyway: bool = False
                ) -> Optional[str]:
        """
        Converts the exported object to a JSON string.
        :param dst: path to file or file object to write to
        :return: If no destination is specified, returns the JSON string. else, None.
        """
        obj = self.to_json_obj()

        s = None
        if dst is None or return_anyway:
            s = json.dumps(obj)
            return s

        if isinstance(dst, str):
            with open(dst, "a") as f:
                json.dump(obj, f)
                return s
        elif isinstance(dst, SupportsWrite):
            json.dump(obj, dst)
            return s
        else:
            raise self.JSONExportableError(self.JSONExportableError.default_msg + type(dst))

    def export_(self, dst: Optional[str | SupportsWrite[str]] = None) -> str:
        return self.to_json(dst, return_anyway=True)
