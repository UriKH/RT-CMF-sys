from utils.util_types import *
import itertools
import numpy as np
from numpy import linalg
from itertools import product


class PointGenerator:
    @classmethod
    def generate_random_sphere(cls, n: int, radius: int, dim: int):
        raise NotImplementedError

    @classmethod
    def generate_cube(cls, edge_len: int, dim: int, as_primitive=False) -> Set[Tuple[int, ...]]:
        points = itertools.product(range(-edge_len, edge_len + 1), repeat=dim)
        if as_primitive:
            return {cls.__to_primitive_vec(p) for p in points}
        return set(points)

    @classmethod
    def generate_via_shape(cls,
                           length: int,
                           dim: int,
                           shape: str,
                           as_primitive=False,
                           random=False,
                           n: Optional[int] = None):
        if random and n is None:
            raise ValueError('Option chosen is random but number of points unspecified')
        match shape:
            case 'cube':
                if random:
                    return cls.generate_random_cube(n, length, dim)
                return cls.generate_cube(length, dim, as_primitive)
            case 'sphere':
                if random:
                    return cls.generate_random_sphere(n, length, dim)
                return cls.generate_sphere(length, dim, as_primitive)
            case _:
                raise ValueError(f"Invalid shape: {shape}, shape must be 'cube' / 'sphere'")

    @classmethod
    def generate_random_cube(cls, n: int, edge_len: int, dim: int):
        raise NotImplementedError

    @classmethod
    def generate_sphere(cls, radius: int, dim: int, as_primitive=False):
        return cls.limit_by_norm(cls.generate_cube(radius, dim, as_primitive), radius)

    @classmethod
    def expand_set(cls,
                   points: Set[Tuple[int, ...]],
                   expansion_factor: int = 1,
                   signed_expansion: bool = True,
                   norm: sp.Rational | int = None,
                   as_primitive=False):
        new_set = points.copy()
        for point in points:
            permutations = product(
                range(-expansion_factor if signed_expansion else 0, expansion_factor + 1),
                repeat=len(point)
            )
            to_update = {tuple(list(np.array(point) + np.array(perm))) for perm in permutations}
            if as_primitive:
                to_update = {cls.__to_primitive_vec(p) for p in to_update}
            if norm is not None:
                to_update = cls.limit_by_norm(to_update, norm)
            new_set.update(to_update)
        return new_set

    @classmethod
    def limit_by_norm(cls, points: Set, norm: sp.Rational | int):
        return {p for p in points if linalg.norm(np.array(p, dtype=float)) <= norm}

    @classmethod
    def __to_primitive_vec(cls, v: Tuple[int, ...]) -> Tuple[int, ...]:
        g = sp.gcd(v)
        if g == 0:
            return v
        return tuple(x // g for x in v)

    @classmethod
    def generate_hyperplane(cls, n: int, dim: int, hp: sp.Expr):
        raise NotImplementedError
