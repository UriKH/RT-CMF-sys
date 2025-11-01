from ..IO.exports import JSONExportable
from ..IO.imports import JSONImportable
from ..types import *
from dataclasses import dataclass
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .position import Position


@dataclass
class Plane(JSONExportable, JSONImportable):
    """
    A class representing a plane given as a sympy expression using also a normal and a point on the plane.
    """
    expression: sp.Expr
    symbols: List[sp.Symbol]

    def __post_init__(self):
        self.normal, self.point = self.__calc_normal(self.expression, self.symbols)

    def intersection_with_line_coeff(self, start: "Position", direction: "Position"):
        """
        Calculate the intersection coefficient between a plane and a line defined by start and direction.
        (A ray defined as: l_0 + t * l where t is a scalar)
        :param start: l_0 - a start point of the ray
        :param direction: l - the direction of the ray
        :return: The t value for which the line intersects with the plane, if there is no intersection None.
        """
        if abs(dot := np.dot(self.normal, direction.as_np_array())) <= 1e-10:
            return None
        return np.dot(self.point - start.as_np_array(), self.normal) / dot

    @staticmethod
    def __calc_normal(expr: sp.Expr, symbols: List[sp.Symbol]) -> Tuple[np.array, np.array]:
        """
        Calculate the normal and a point on the plane.
        :param expr: The expression describing the plane.
        :param symbols: The symbols describing the plane.
        :return: A tuple of the normal and a point on the plane.
        """
        normal = np.array([float(expr.diff(v)) for v in symbols], dtype=float)

        # Compute a numeric point on the plane
        pt = np.zeros(len(symbols), dtype=float)
        for i, v in enumerate(symbols):
            a = float(expr.coeff(v))
            if a != 0:
                # set all other variables to 0
                c = float(expr.subs({sym: 0 for sym in symbols}))
                pt[i] = -c / a
                break
        return normal, pt

    def __hash__(self):
        return hash((self.expression, tuple(self.symbols)))

    @classmethod
    def from_json_obj(cls, src: dict):
        return cls(sp.sympify(src["expression"]), sp.sympify(src["symbols"]))

    def to_json_obj(self) -> dict | list:
        return {
            'expression': sp.srepr(self.expression),
            'symbols': sp.srepr(self.symbols)
            # 'point': self.point.tolist(),
            # 'normal': self.normal.tolist()
        }
