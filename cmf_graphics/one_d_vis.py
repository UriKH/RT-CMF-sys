import matplotlib.pyplot as plt
import sympy as sp

from utils.position import Position
from utils.util_types import *

"""
Visualize 1D data of a CMF:
*   search_via_expr     -   given an expression using spherical coordinates or cartesian coordinates, 
                            and a starting point search in the CMF.
*   
"""


def search_via_expr(expr: sp.Expr, start: Position, cmf: CMF):
    raise NotImplementedError


if __name__ == "__main__":
    pass
