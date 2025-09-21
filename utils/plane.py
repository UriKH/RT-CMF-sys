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
        if (dot := np.dot(self.normal, direction)) == 0:
            return None
        return np.dot(self.point - start, direction) / dot

    @staticmethod
    def calc_normal(expr: sp.Expr, symbols: List[sp.Symbol]) -> Tuple[np.array, np.array]:
        pt = [0] * len(symbols)
        for i, v in enumerate(symbols):
            if (coeff := expr.coeff(v)) == 0:
                continue
            pt[i] = -expr.subs({v: 0}) / coeff
            break
        return np.array([sp.diff(expr, v) for v in symbols]), np.array(pt)
