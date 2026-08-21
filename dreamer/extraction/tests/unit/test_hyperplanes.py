import pytest
from ...hyperplanes import Hyperplane, Position
import sympy as sp
import numpy as np


x, y, z = sp.symbols('x y z')


class TestClass:

    # ==========================================
    # 1. VALIDATION TESTS (Expected Failures)
    # ==========================================

    def test_missing_symbols_raises_error(self):
        """Ensure passing an expression with variables not in the symbols list fails."""
        expr = x + y + z

        with pytest.raises(ValueError, match="Missing symbols in ordering"):
            Hyperplane(expr, symbols=[x, y])

    @pytest.mark.parametrize("bad_expr", [
        x ** 2 + y,
        x * y + z,
        sp.sin(x) + y
    ])
    def test_non_linear_expressions_raise_error(self, bad_expr):
        """Ensure non-linear equations are caught and rejected."""
        with pytest.raises(ValueError, match="Expression is not linear"):
            Hyperplane(bad_expr, symbols=[x, y, z])

    # ==========================================
    # 2. NORMALIZATION TESTS (Scaling & Signs)
    # ==========================================

    @pytest.mark.parametrize("input_expr, expected_expr", [
        (x / 2 + y / 3 - 1, 3 * x + 2 * y - 6),
        (x / 5, x),
        (-x + y, x - y),
        (-2 * x - 3 * y + 1, 2 * x + 3 * y - 1),
        (-x / 2 + y / 4, 2 * x - y),
    ])
    def test_expression_normalization(self, input_expr, expected_expr):
        """
        Tests that __post_init__ correctly scales fractional coefficients to integers
        and normalizes the signs so the leading coefficient is positive.
        """
        hp = Hyperplane(input_expr, symbols=[x, y, z])
        assert hp.expr.equals(expected_expr), f"Expected {expected_expr}, but got {hp.expr}"

    # ==========================================
    # 3. PROPERTY EXTRACTION TESTS
    # ==========================================

    def test_property_extraction(self):
        """
        Ensures that after all normalization, the linear term, free term,
        and coefficient maps are extracted correctly.
        """
        hp = Hyperplane(2 * x - 4 * y + 5, symbols=[x, y, z])
        assert hp.free_term == 5
        assert hp.linear_term.equals(2 * x - 4 * y)
        assert hp.sym_coef_map[x] == 2
        assert hp.sym_coef_map[y] == -4
        assert hp.sym_coef_map.get(z, 0) == 0

    @pytest.mark.parametrize("input_expr, expected_res", [
        (x + y, True),
        (x, True),
        (-x + y + sp.Rational(1, 2), False)
    ])
    def test_integer_shift(self, input_expr, expected_res):
        hp = Hyperplane(input_expr, symbols=[x, y, z])
        assert hp.is_in_integer_shift() is expected_res, f"Expected {expected_res}, but got {not expected_res}"

    @pytest.mark.parametrize("input_expr, shift, output_expr", [
        (x + y, Position({x: 0, y: sp.Rational(1, 2), z: sp.Rational(1, 2)}), 2 * x + 2 * y + 1),
        (x + y, Position({x: sp.Rational(1, 2), y: sp.Rational(1, 2), z: 0}), x + y + 1),
        (x + y, Position({x: sp.Rational(1, 2), y: -sp.Rational(1, 2), z: 0}), x + y),
        (x + y, Position({x: sp.Rational(1, 2), y: sp.Rational(1, 3), z: 0}), 6 * x + 6 * y + 5)
    ])
    def test_shift_application(self, input_expr, shift, output_expr):
        hp = Hyperplane(input_expr, symbols=[x, y, z])
        shifted = hp.apply_shift(shift).expr
        assert shifted.equals(output_expr), f"Expected {output_expr}, but got {shifted}"

    @pytest.mark.parametrize("input_expr, shift, output_expr", [
        (2 * x + 2 * y + 1, Position({x: 0, y: sp.Rational(1, 2), z: sp.Rational(1, 2)}), x + y),
        (x + y + 1, Position({x: sp.Rational(1, 2), y: sp.Rational(1, 2), z: 0}), x + y),
        (x + y, Position({x: sp.Rational(1, 2), y: -sp.Rational(1, 2), z: 0}), x + y),
        (6 * x + 6 * y + 5, Position({x: sp.Rational(1, 2), y: sp.Rational(1, 3), z: 0}), x + y)
    ])
    def test_shift_application(self, input_expr, shift, output_expr):
        hp = Hyperplane(input_expr, symbols=[x, y, z])
        shifted = hp.remove_shift(shift).expr
        assert shifted.equals(output_expr), f"Expected {output_expr}, but got {shifted}"

    @pytest.mark.parametrize("expr, linear, free", [
        (2 * x + 2 * y + 1, 2 * x + 2 * y, -1),
        (x + y + 1, x + y, -1),
        (x + y, x + y, 0)
    ])
    def test_expr_format(self, expr, linear, free):
        hp = Hyperplane(expr, symbols=[x, y, z])
        lin, f = hp.equation_like
        assert lin.equals(linear) and f == free, f"Expected {linear}, {free} but got {lin}, {f}"

    @pytest.mark.parametrize("expr, linear, free", [
        (2 * x + 2 * y + 1, np.array([2, 2, 0]), 1),
        (x + y + 1, np.array([1, 1, 0]), 1),
        (x + sp.Rational(1, 2) * y, np.array([2, 1, 0]), 0)
    ])
    def test_vector_format(self, expr, linear, free):
        hp = Hyperplane(expr, symbols=[x, y, z])
        lin, f = hp.vectors
        assert np.all(lin == linear) and f == free, f"Expected {linear}, {free} but got {lin}, {f}"

    @pytest.mark.parametrize("expr, other, expect", [
        (2 * x + 2 * y + 2, x + y + 1, True),
        (x + 0, x, True),
        (x + y + 3 + 2, x + y + 5, True),
        (0 * x - y, y, True),
    ])
    def test_equality(self, expr, other, expect):
        hp = Hyperplane(expr, symbols=[x, y, z])
        other_hp = Hyperplane(other, symbols=[x, y, z])
        assert hp == other_hp if expect else hp != other_hp
