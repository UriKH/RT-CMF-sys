import json
from dataclasses import dataclass, field
from ramanujantools.cmf.pfq import pFq

from s_db.functions.formatter import Formatter
from utils.util_types import *
from configs.database import *


@dataclass
class pFq_formatter(Formatter):
    """
    Represents a pFq and its CMF + allows conversion to and from JSON.
    :var p: The p value of the pFq.
    :var q: The q value of the pFq.
    :var z: The z value of the pFq.
    :var shifts: The shifts in starting point in the CMF where a sp.Rational indicates a shift.
    While 0 indicates no shift (None if not doesn't matter).
    """
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
    def from_json(cls, s_json: str) -> "pFq_formatter":
        """
        Converts a JSON string to a pFq_formatter.
        :param s_json: The JSON string representation of the pFq_formatter (only attributes).
        :return: A pFq_formatter object.
        """
        data = json.loads(s_json)
        data['z'] = sp.sympify(data['z']) if isinstance(data['z'], str) else data['z']
        data['shifts'] = [sp.sympify(shift) if isinstance(shift, str) else shift for shift in data['shifts']]
        return cls(**data)

    def to_json(self) -> dict:
        """
        Converts the pFq_formatter to a JSON string (i.e., convert sp.Expr to str)
        :return: A dictionary representation of the pFq_formatter matching the JSON format.
        """
        return {
            TYPE_ANNOTATE: self.__class__.__name__,
            DATA_ANNOTATE: {
                "p": self.p, "q": self.q, "z": str(self.z) if isinstance(self.z, sp.Expr) else self.z, "shifts":
                    [str(shift) if isinstance(shift, sp.Expr) else shift for shift in self.shifts.as_list()]
            }
        }

    def to_cmf(self) -> CMFtup:
        """
        Converts the pFq_formatter to a CMF.
        :return: A tuple (CMF, shifts)
        """
        cmf = pFq(self.p, self.q, self.z)
        self.shifts.set_axis(list(cmf.matrices.keys()))
        return cmf, self.shifts

    def __repr__(self):
        return json.dumps(self.to_json())
    