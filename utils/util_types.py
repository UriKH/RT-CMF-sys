from ramanujantools.cmf import CMF
import sympy as sp
from typing import Union, List, Dict, Tuple, Set, FrozenSet, Annotated, Optional

from utils.position import Position

Shift = Union[sp.Rational | int | None]     # a shift in starting point
CMFtup = Tuple[CMF, Position]               # CMF tuple (CMF, list of shifts)
CMFlist = List[CMFtup]
EqTup = Tuple[sp.Expr, sp.Expr]             # Hyperplane equation representation

ShardVec = Tuple[int, ...]


