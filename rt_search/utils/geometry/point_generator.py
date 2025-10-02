from ..types import *

import math
import mpmath as mp
import itertools
import numpy as np
from numpy import linalg
from itertools import product


Point = Tuple[int, ...]


class PointGenerator:
    @classmethod
    def generate_random_sphere(cls, n: int, radius: int, dim: int):
        raise NotImplementedError

    @classmethod
    def generate_cube(cls, edge_len: int, dim: int, as_primitive=False) -> Set[Point]:
        """
        Generate a set of points inside and on a cube of a certain edge length which is centered around the origin
        :param edge_len: the edge length of the cube
        :param dim: the dimensions in which the cube/hypercube lives
        :param as_primitive: Enforce gcd of coordinates to be 1
        :return: A set of points inside and on a cube
        """
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
                           n: Optional[int] = None) -> Set[Point]:
        """
        Generate a set of points matching some hyper-shapes. This could be done randomly by giving a number
         of required points.
        :param length: The side length or radius length of the respective shape specified
        :param dim: The dimensions of the specified shape
        :param shape: The shape to create (cube / sphere / etc.)
        :param as_primitive: All points will have coordinates with gcd 1
        :param random: Points will be sampled randomly
        :param n: Amount of points to sample randomly
        :return: The generated set of points
        """
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
                   points: Set[Point],
                   expansion_factor: int = 1,
                   signed_expansion: bool = True,
                   norm: sp.Rational | int = None,
                   as_primitive=False) -> Tuple[Set[Point], Set[Point]]:
        """
        Expand a set of points in each direction by the expansion factor.
        The expansion is by adding 1/0/-1 to each coordinate.
        :param points: The set of points to expand
        :param expansion_factor: The number of times to expand.
        :param signed_expansion: Expand using negative coordinates not only positive
        :param norm: A norm of all points limiting the expansion
        :param as_primitive: All points will have coordinates with gcd 1
        :return: A tuple of the new points and the total points (given set union with the new ones)
        """
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
        """
        Filter a set of vectors by a given maximum L_2 norm
        :param points: The set of points to limit
        :param norm: The maximum L_2 norm
        :return: The filtered set
        """
        return {p for p in points if linalg.norm(np.array(p, dtype=float)) <= norm}

    @classmethod
    def __to_primitive_vec(cls, v: Point) -> Point:
        """
        Convert a vector to primitive one - i.e. gcd(coordinates) = 1
        :param v: The vector to convert
        :return: The vector as primitive
        """
        g = sp.gcd(v)
        if g == 0:
            return v
        return tuple(int(x // g) for x in v)

    @classmethod
    def generate_hyperplane(cls, n: int, dim: int, hp: sp.Expr):
        raise NotImplementedError

    @staticmethod
    def calc_sphere_radius(N: int, d: int) -> int:
        """
        Using the known formula, calculates the appropriate radius of a sphere such that there will be enough primitive
         vectors inside it
        :param N: The number of primitive vectors required
        :param d: Dimensions of the hypersphere
        :return: The calculated radius
        """
        return math.ceil(float((N * mp.gamma(d / 2 + 1) * mp.zeta(d)) ** (1 / d) / mp.sqrt(mp.pi())))

    @staticmethod
    def clac_number_of_primitive_points_in_sphere(R: int, d: int) -> int:
        """
        Using the known formula, calculates the number of primitive vectors inside a hypersphere of a given radius.
        :param R: The hypersphere radius
        :param d: The number of dimensions of the hypersphere
        :return: The calculated number of primitive vectors
        """
        return math.ceil(float(((mp.pi() ** (d / 2)) * (R ** d)) / (mp.zeta(d) * mp.gamma(d / 2 + 1))))
