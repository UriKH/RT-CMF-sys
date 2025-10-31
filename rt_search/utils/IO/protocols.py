from typing import Protocol, runtime_checkable, TypeVar


T = TypeVar('T')


@runtime_checkable
class SupportsWrite(Protocol[T]):
    def write(self, s: T, *args, **kwargs) -> object: ...


@runtime_checkable
class SupportsRead(Protocol[T]):
    def read(self, *args, **kwargs) -> T: ...


@runtime_checkable
class SupportsIO(SupportsRead[T], SupportsWrite[T], Protocol[T]):
    def flush(self) -> None: ...
    def seek(self, offset: int, whence: int = 0) -> int: ...
    def tell(self) -> int: ...
