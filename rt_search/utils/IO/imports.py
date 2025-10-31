from abc import ABC, abstractmethod

from typing_extensions import runtime_checkable, Protocol
import json
from typing import TypeVar, List


@runtime_checkable
class SupportsRead(Protocol):
    def read(self, *args, **kwargs) -> str: ...


@runtime_checkable
class ImportableProto(Protocol):
    accepted_type: type

    @classmethod
    def import_(cls, data) -> List["ImportableProto"]: ...

    def __hash__(self) -> int: ...


class Importable(ABC):
    accepted_type = None

    class ImportError(Exception):
        pass

    @classmethod
    @abstractmethod
    def import_(cls, *args):
        raise NotImplementedError

    def __hash__(self) -> int: ...


T = TypeVar('T', bound="JSONImportable")


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
    def from_json(cls, src: str | SupportsRead) -> List[T]:
        """
        Create the object from a JSON file.
        :param src: The JSON file or path.
        :return: an object list
        """
        def do_unpack(data) -> List[T]:
            results = set()
            if type(data) is list:
                for d in data:
                    obj = cls.from_json_obj(d)
                    results.add(obj)
            else:
                results = {cls.from_json_obj(data)}
            return list(results)

        if isinstance(src, str) and src.split('.')[-1] == 'json':
            with open(src, 'r') as f:
                data = json.load(f)
                return do_unpack(data)
        elif isinstance(src, SupportsRead):
            return do_unpack(json.load(src))
        raise cls.JSONImportError(cls.JSONImportError.default_msg + str(type(src)))

    @classmethod
    def import_(cls, src: dict | str | SupportsRead) -> List[T]:
        """
        Given a dictionary representing an object / a json file path / or the file itself
        :param src: source to import from
        :return: a list of objects
        """
        match src:
            case str() | SupportsRead():
                return cls.from_json(src)
            case dict():
                return cls.from_json_obj(src)
            case _:
                raise cls.JSONImportError(cls.JSONImportError.default_msg + str(type(src)))
