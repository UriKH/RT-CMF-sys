from typing import TypeVar, Generic


from ..types import *
from .exports import Exportable

T = TypeVar('T', bound=Exportable)


class Exporter(Generic[T]):
    def __init__(self, path: str, t: Optional[Type[T]] = None):
        self.cls = t
        self.path = path

    def __call__(self, data: T | List[T]) -> List[str]:
        results = []
        if isinstance(data, list):
            with open(self.path, 'a') as f:
                for d in data:
                    results.append(d.export_(f))
            return results
        return [data.export_(self.path)]

    @classmethod
    def __class_getitem__(cls, item: Type[T]):
        return lambda path: cls(path, item)
