import math

from utils.types import *

import mpmath as mp
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
        points = list(itertools.product(range(-edge_len, edge_len + 1), repeat=dim))
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
        new_set = set()

        permutations = list(product(
            range(-expansion_factor if signed_expansion else 0, expansion_factor + 1),
            repeat=len(next(iter(points)))
        ))

        for point in points:
            to_update = set()
            for perm in permutations:
                p = tuple(int(c) for c in (np.array(point, dtype=int) + np.array(list(perm), dtype=int)))
                to_update.add(p)

            if as_primitive:
                to_update = {cls.__to_primitive_vec(p) for p in to_update}
            if norm is not None:
                to_update = cls.limit_by_norm(to_update, norm)
            new_set.update(to_update - points)
        return new_set, new_set.union(points)

    @classmethod
    def limit_by_norm(cls, points: Set, norm: sp.Rational | int):
        return {p for p in points if linalg.norm(np.array(p, dtype=float)) <= norm}

    @classmethod
    def __to_primitive_vec(cls, v: Tuple[int, ...]) -> Tuple[int, ...]:
        g = sp.gcd(v)
        if g == 0:
            return v
        return tuple(int(x // g) for x in v)

    @classmethod
    def generate_hyperplane(cls, n: int, dim: int, hp: sp.Expr):
        raise NotImplementedError

    @staticmethod
    def calc_sphere_radius(N: int, d: int):
        return math.ceil(float((N * mp.gamma(d / 2 + 1) * mp.zeta(d)) ** (1 / d) / mp.sqrt(mp.pi())))

    @staticmethod
    def clac_number_of_primitive_points_in_sphere(R: int, d: int):
        return math.ceil(float(((mp.pi() ** (d / 2)) * (R ** d)) / (mp.zeta(d) * mp.gamma(d / 2 + 1))))
