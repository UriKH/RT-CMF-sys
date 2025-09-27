from utils.util_types import *
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Plane:
    expression: sp.Expr
    symbols: List[sp.Symbol]

    def __post_init__(self):
        self.normal, self.point = self.calc_normal(self.expression, self.symbols)

    def intersection_with_line_coeff(self, start: Position, direction: Position):
        # TODO: need to normalize things here
        if abs(dot := np.dot(self.normal, direction.as_np_array())) <= 1e-10:
            return None
        return np.dot(self.point - start.as_np_array(), self.normal) / dot

    @staticmethod
    def calc_normal(expr: sp.Expr, symbols: List[sp.Symbol]) -> Tuple[np.array, np.array]:
        # pt = np.zeros(len(symbols), dtype=float)
        # normal = np.zeros(len(symbols), dtype=float)
        #
        # for i, v in enumerate(symbols):
        #     if (coeff := float(expr.coeff(v))) == 0:
        #         continue
        #     pt[i] = float(-expr.subs({v: 0}.update({for k, sym in enumerate(symbols) if k < i}))) / coeff
        #     break
        #
        # for i, v in enumerate(symbols):
        #     normal[i] = float(sp.diff(expr, v))
        # return normal, pt
        # Compute numeric normal
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
