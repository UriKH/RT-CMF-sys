from .IO import (
    imports as imp,
    exports as exp
)

from typing import Dict, Union

from ramanujantools.cmf.cmf import CMF as RT_CMF
from ramanujantools.cmf.pfq import pFq as RT_pFq
from ramanujantools import Matrix
from sympy import srepr, sympify
import sympy as sp
from dataclasses import dataclass
import json

from .geometry.position import Position


class CMF(RT_CMF, exp.JSONExportable, imp.JSONImportable):
    def __init__(self, matrices: Dict[sp.Symbol, Matrix]):
        super().__init__(matrices, False)

    def to_json_obj(self) -> Dict[str, str]:
        return {srepr(sym): srepr(mat) for sym, mat in self.matrices.items()}

    @classmethod
    def from_json_obj(cls, src: Dict[str, str]) -> "CMF":
        return cls({sympify(sym): sympify(mat) for sym, mat in src.items()})


class pFq(CMF, RT_pFq, exp.JSONExportable):
    def __init__(self, p, q, z_eval, theta_derivative=True, negate_denominator_params=True):
        RT_pFq.__init__(self, p, q, z_eval, theta_derivative, negate_denominator_params)

    def to_json_obj(self) -> Dict[str, ...]:
        return {srepr(sym): srepr(mat) for sym, mat in self.matrices.items()}


@dataclass
class ShiftCMF(exp.JSONExportable, imp.JSONImportable):
    cmf: CMF
    shift: Position

    def to_json_obj(self) -> Dict[str, ...]:
        return {'cmf': self.cmf.to_json_obj(), 'shift': self.shift.to_json_obj()}

    @classmethod
    def from_json_obj(cls, src: Dict[str, ...]) -> "ShiftCMF":
        return cls(cmf=CMF.from_json_obj(src['cmf']), shift=Position.from_json_obj(src['shift']))

    def __hash__(self):
        return hash((self.cmf, self.shift))