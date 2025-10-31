import json
from dataclasses import dataclass, field
from rt_search.utils.cmf import pFq

from rt_search.db_stage.funcs.formatter import Formatter
from rt_search.utils.types import *
from . import FORMATTER_REGISTRY
from rt_search.utils.cmf import ShiftCMF


@dataclass
class pFq_formatter(Formatter):
    """
    Represents a pFq and its CMF + allows conversion to and from JSON.
    :var const: The constant related to this pFq function
    :var p: The p value of the pFq.
    :var q: The q value of the pFq.
    :var z: The z value of the pFq.
    :var shifts: The shifts in starting point in the CMF where a sp.Rational indicates a shift.
    While 0 indicates no shift (None if not doesn't matter).
    """
    # const: str
    p: int
    q: int
    z: sp.Expr
    shifts: Position | List[sp.Expr] = field(default_factory=list)

    def __post_init__(self):
        if self.p <= 0 or self.q <= 0:
            raise ValueError("Non-positive values")
        if not isinstance(self.shifts, list) and not isinstance(self.shifts, Position):
            raise ValueError("Shifts should be a list or Position")

        if self.p + self.q != len(self.shifts) and len(self.shifts) != 0:
            raise ValueError("Shifts should be of length p + q or 0")

        if len(self.shifts) == 0:
            self.shifts = Position([0 for _ in range(self.p + self.q)])
        elif isinstance(self.shifts, list):
            self.shifts = Position(self.shifts)

    @classmethod
    def _from_json_obj(cls, s_json: str) -> "pFq_formatter":
        """
        Converts a JSON string to a pFq_formatter.
        :param s_json: The JSON string representation of the pFq_formatter (only attributes).
        :return: A pFq_formatter object.
        """
        data = json.loads(s_json)
        data['z'] = sp.sympify(data['z']) if isinstance(data['z'], str) else data['z']
        data['shifts'] = [sp.sympify(shift) if isinstance(shift, str) else shift for shift in data['shifts']]
        return cls(**data)

    def _to_json_obj(self) -> dict:
        """
        Converts the pFq_formatter to a JSON string (i.e., convert sp.Expr to str)
        :return: A dictionary representation of the pFq_formatter matching the JSON format.
        """
        return {
            **super()._to_json_obj(),
            "p": self.p,
            "q": self.q,
            "z": str(self.z) if isinstance(self.z, sp.Expr) else self.z,
            "shifts": [str(shift) if isinstance(shift, sp.Expr) else shift for shift in self.shifts.as_list()]
        }

    def to_cmf(self) -> ShiftCMF:
        """
        Converts the pFq_formatter to a CMF.
        :return: A tuple (CMF, shifts)
        """
        cmf = pFq(self.p, self.q, self.z)
        self.shifts.set_axis(list(cmf.matrices.keys()))
        return ShiftCMF(cmf, self.shifts)

    def __repr__(self):
        return json.dumps(self._to_json_obj())

    def __str__(self):
        return f'<{self.__class__.__name__}: {self.__repr__()}>'

    def __hash__(self):
        return hash((self.p, self.q, self.z, self.shifts))


FORMATTER_REGISTRY['pFq_formatter'] = pFq_formatter
