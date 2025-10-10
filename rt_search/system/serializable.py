from abc import ABC, abstractmethod


class Serializable(ABC):
    @abstractmethod
    def as_json_serializable(self):
        raise NotImplementedError
