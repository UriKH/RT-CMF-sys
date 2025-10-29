from abc import ABC, abstractmethod
from collections import defaultdict

from typing_extensions import runtime_checkable, Protocol
from ..types import *
import json
from rt_search.db_stage.config import *


@runtime_checkable
class SupportsRead(Protocol):
    def read(self, *args, **kwargs) -> str: ...


@runtime_checkable
class ImportableProto(Protocol):
    accepted_type: type

    @classmethod
    def import_it(cls, data): ...


class Importable(ABC):
    accepted_type = None

    class ImportError(Exception):
        pass

    @classmethod
    @abstractmethod
    def import_it(cls, *args):
        raise NotImplementedError


class JSONImportable(Importable):
    class JSONImportError(Importable.ImportError):
        default_msg = 'Could not import from type '

    accepted_type = dict | str | SupportsRead

    @classmethod
    @abstractmethod
    def from_json_obj(cls, src: dict):
        """
        Create the object from a JSON like dict or list (i.e. an object).
        :param src: the JSON like dict or list.
        :return: an object
        """
        raise NotImplementedError

    @classmethod
    def from_json(cls, src: str | SupportsRead) -> Dict[str, Any]:
        """
        Create the object from a JSON file or a json like string.
        :param src: The JSON file or string.
        :return: an object
        """
        def do_unpack(data):
            results = defaultdict(set)
            if type(data) is list:
                for d in data:
                    obj = cls.from_json_obj(d)
                    results[d[CONST_ANNOTATE]].add(obj)
            else:
                results[data[CONST_ANNOTATE]] = {cls.from_json_obj(data)}
            return results

        if isinstance(src, str):
            with open(src, 'r') as f:
                data = json.load(f)
                return do_unpack(data)
        elif isinstance(src, SupportsRead):
            return do_unpack(json.load(src))
        else:
            raise cls.JSONImportError(cls.JSONImportError.default_msg + str(type(src)))

    @classmethod
    def import_it(cls, src: dict | str | SupportsRead) -> Dict[str, Any]:
        if isinstance(src, str):
            return cls.from_json(json.loads(src))
        if isinstance(src, dict):
            return {src[CONST_ANNOTATE]: {cls.from_json_obj(src)}}
        if isinstance(src, SupportsRead):
            return cls.from_json(src)
        raise cls.JSONImportError(cls.JSONImportError.default_msg + str(type(src)))
