from collections import defaultdict
from typing import TypeVar, Generic

from ..types import *
from .imports import ImportableProto

T = TypeVar('T', bound=ImportableProto)


class Importer(Generic[T]):
    def __init__(self, cls: Type[T]):
        self.cls = cls  # store the real class

    def __call__(self, data: Any, multiple: bool):
        objs = defaultdict(set)
        if multiple:
            for d in data:
                if not isinstance(d, self.cls.accepted_type):
                    raise Exception()
                imported = self.cls.import_it(d)
                for k in imported:
                    if k not in objs:
                        objs[k] = imported[k]
                    else:
                        objs[k].union(imported[k])
        else:
            if not isinstance(data, self.cls.accepted_type):
                raise Exception()
            objs = self.cls.import_it(data)
        return objs

    @classmethod
    def __class_getitem__(cls, item: Type[T]):
        return lambda: cls(item)
