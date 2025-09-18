from utils.util_types import *
from dataclasses import dataclass, field


@dataclass
class Plane:
    expression: sp.Expr
    symbols: List[sp.Symbol]

    def __post_init__(self):
        self.normal, self.point = self.calc_normal(self.expression, self.symbols)

    def intersection_with_line_coeff(self, start: sp.Matrix, direction: sp.Matrix):
        dot = self.normal.dot(direction)
        if dot == 0:
            return None
        d = (self.point - start).dot(direction) / dot
        return d

    @staticmethod
    def calc_normal(expr: sp.Expr, symbols: List[sp.Symbol]) -> Tuple[sp.Matrix, sp.Matrix]:
        pt = [0] * len(symbols)
        for i, v in enumerate(symbols):
            if (coeff := expr.coeff(v)) == 0:
                continue
            pt[i] = -expr.subs({v: 0}) / coeff
            break
        return sp.Matrix([sp.diff(expr, v) for v in symbols], symbols), sp.Matrix(pt, symbols)
