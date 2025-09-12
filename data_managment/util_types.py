from ramanujantools.cmf import CMF
import sympy as sp
from typing import Union, List, Dict, Tuple

CMFtup = Tuple[CMF, list]
CMFlist = List[CMFtup]
Shift = Union[sp.Rational | int | None]
