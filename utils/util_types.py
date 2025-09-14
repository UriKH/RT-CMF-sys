from ramanujantools.cmf import CMF
import sympy as sp
from typing import Union, List, Dict, Tuple, Set, FrozenSet

CMFtup = Tuple[CMF, list]
CMFlist = List[CMFtup]
Shift = Union[sp.Rational | int | None]
