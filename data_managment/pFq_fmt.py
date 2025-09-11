import json
from dataclasses import dataclass, field
from ramanujantools.cmf import CMF
from ramanujantools.cmf.pfq import pFq
import sympy as sp

from data_managment.formatter import Formatter


@dataclass()
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
    shifts: list[sp.Rational | int | None] = field(default_factory=list)

    def __post_init__(self):
        if self.p <= 0 or self.q <= 0:
            raise ValueError("Non-positive values")

        if self.p + self.q < len(self.shifts):
            raise ValueError("Too many shifts")
        elif self.p + self.q > len(self.shifts):
            self.shifts = self.shifts + [None for _ in range(len(self.shifts), self.p + self.q)]

    @classmethod
    def from_json(cls, s_json: str) -> "pFq_formatter":
        """
        Converts a JSON string to a pFq_formatter.
        :param s_json: The JSON string representation of the pFq_formatter (only attributes).
        :return: A pFq_formatter object.
        """
        data = json.loads(s_json)
        data['z'] = sp.sympify(data['z']) if isinstance(data['z'], str) else data['z']

        for i, shift in enumerate(data['shifts']):
            if isinstance(shift, str):
                data['shifts'][i] = sp.sympify(shift)
        return cls(**data)

    def to_json(self) -> dict:
        """
        Converts the pFq_formatter to a JSON string (i.e., convert sp.Expr to str)
        :return: A dictionary representation of the pFq_formatter matching the JSON format.
        """
        return {
            "type": self.__class__.__name__,
            "data": {
                "p": self.p, "q": self.q, "z": str(self.z) if isinstance(self.z, sp.Expr) else self.z, "shifts":
                    [str(shift) if isinstance(shift, sp.Expr) else shift for shift in self.shifts]
            }
        }

    def to_cmf(self) -> (CMF, list):
        """
        Converts the pFq_formatter to a CMF.
        :return: A tuple (CMF, shifts)
        """
        return pFq(self.p, self.q, self.z), self.shifts

    def __str__(self):
        return json.dumps(self.to_json())
    