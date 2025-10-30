from typing import TypeVar, Generic


from ..types import *
from .imports import Importable

T = TypeVar('T', bound=Importable)


class Importer(Generic[T]):
    def __init__(self, t: Optional[Type[T]] = None):
        self.cls = t

    def __call__(self, data: Any, multiple: bool) -> List[T]:
        objs = set()
        if multiple:
            for d in data:
                if not isinstance(d, self.cls.accepted_type):
                    raise Exception()
                objs.add(self.cls.import_it(d))
            objs = list(objs)
        else:
            if not isinstance(data, self.cls.accepted_type):
                raise Exception()
            objs = self.cls.import_it(data)
        return objs

    @classmethod
    def __class_getitem__(cls, item: Type[T]):
        return lambda: cls(item)
