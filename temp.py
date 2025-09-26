import sympy as sp
import numpy as np

SHARD_EXTRACTOR_ERR = 1e-9

# Example symbols
x, y = sp.symbols("x y")
symbols = [x, y]

def expr_to_ineq(expr, greater_than_0: bool = True):
    coeffs = expr.as_coefficients_dict()
    a = [coeffs.get(v, 0) for v in symbols]
    const = float(expr.as_independent(*symbols, as_Add=True)[0])

    if greater_than_0:
        row = [-coef for coef in a]
        b = const - SHARD_EXTRACTOR_ERR
    else:
        row = [coef for coef in a]
        b = -const - SHARD_EXTRACTOR_ERR

    return row, b


def test_expr_to_ineq(expr, greater_than_0, test_points):
    row, b = expr_to_ineq(expr, greater_than_0)
    row = np.array(row, dtype=float)
    for pt in test_points:
        pt_arr = np.array(pt, dtype=float)
        original = float(expr.subs({x: pt[0], y: pt[1]})) > 0 if greater_than_0 else float(expr.subs({x: pt[0], y: pt[1]})) < 0
        transformed = np.dot(row, pt_arr) <= b + SHARD_EXTRACTOR_ERR
        print(f"Point {pt}: original={original}, transformed={transformed}")
        assert original == transformed, f"Mismatch at point {pt}"


def main():
    # expr > 0
    expr1 = x + 1  # x + 1 > 0  =>  -x <= 1 - eps
    expr2 = -2 * y + 3  # -2y + 3 > 0 =>  2y <= 3 - eps

    # expr < 0
    expr3 = x - y - 2  # x - y - 2 < 0 => x - y <= 2 - eps

    test_points1 = [[0, 0], [-0.5, 0], [2, 1]]
    test_points2 = [[0, 0], [2, 0], [0, 2]]
    test_points3 = [[3, 6], [0, 0], [-1, 1]]

    print("Testing expr1 (>0)")
    test_expr_to_ineq(expr1, True, test_points1)
    print("Testing expr2 (>0)")
    test_expr_to_ineq(expr2, True, test_points2)
    print("Testing expr3 (<0)")
    test_expr_to_ineq(expr3, False, test_points3)


if __name__ == "__main__":
    main()
