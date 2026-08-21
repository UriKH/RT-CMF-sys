import numpy as np
from ...hyperplanes import Hyperplane
from ...utils.initial_points import *
import pytest
import sympy as sp


x, y, z = sp.symbols('x y z')

hps = [
    Hyperplane(x - z + 1, symbols=[x, y, z]),
    Hyperplane(y - z, symbols=[x, y, z]),
    Hyperplane(y, symbols=[x, y, z]),
    Hyperplane(z, symbols=[x, y, z])
]


class TestClass:
    def test_compute_mapping(self):
        D = 3
        S = 8
        A = np.array([hp.vectors[0] for hp in hps], dtype=np.int64)
        b = np.array([hp.vectors[1] for hp in hps], dtype=np.int64)
        mappings = compute_mapping(D, S, A, b)
        assert len(mappings) == 12
