from abc import ABC, abstractmethod
import json
import os

from ..types import *
from .protocols import *


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
                dst: Optional[str | SupportsIO[str]] = None,
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
            if dst is None:
                return s

        def smart_write(fp):
            # Check if file exists and non-empty
            fp.seek(0, os.SEEK_END)
            file_size = fp.tell()

            if file_size == 0:
                # First write: create new JSON list
                fp.write("[\n")
                json.dump(obj, fp, indent=2)
                fp.write("\n]")
                fp.flush()
                return

            seek_back = min(file_size, 32)
            fp.seek(file_size - seek_back)
            tail = fp.read(seek_back) # read 32 last bytes

            close_index = tail.rfind(']') # find index of ']'
            close_pos = file_size - seek_back + close_index + 2

            fp.seek(close_pos)
            fp.truncate()
            fp.write(",\n")
            json.dump(obj, fp, indent=2)
            fp.write("\n]\n")
            fp.flush()

        if isinstance(dst, str | SupportsIO):
            if isinstance(dst, str):
                with open(dst, "a+") as f:
                    smart_write(f)
            elif isinstance(dst, SupportsIO):
                smart_write(dst)
            return s
        else:
            raise self.JSONExportableError(self.JSONExportableError.default_msg + str(type(dst)))

    def export_(self, dst: Optional[str | SupportsIO] = None) -> str:
        return self.to_json(dst, return_anyway=True)
