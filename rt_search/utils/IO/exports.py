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


class JSONExportable(Exportable):
    class JSONExportableError(Exportable.ExportError):
        default_msg = 'Invalid destination type '

    @abstractmethod
    def to_json_obj(self, obj: Optional[object] = None) -> dict | list:
        """
        Convert the object into a JSON string
        :return: The JSON string
        """
        raise NotImplementedError

    def to_json(self, dst: Optional[str | SupportsWrite[str]] = None) -> Optional[str]:
        """
        Converts the exported object to a JSON string.
        :param dst: path to file or file object to write to
        :return: If no destination is specified, returns the JSON string. else, None.
        """
        obj = self.to_json_obj()

        if dst is None:
            return json.dumps(obj)
        if isinstance(dst, str):
            with open(dst, "a") as f:
                json.dump(obj, f)
                return None
        elif isinstance(dst, SupportsWrite):
            json.dump(obj, dst)
            return None
        else:
            raise cls.JSONExportableError(cls.JSONExportableError.default_msg + type(dst))
