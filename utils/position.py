from utils.util_types import *

import ramanujantools.position as rt_pos
import sympy as sp
import numpy as np


class Position(rt_pos.Position):
    """
    Position wrapper to the ramanujantools.position.Position class. \n
    Here we add some extra functionality - the starting representation is a list of sympy expressions instead of a dict.
    Later it is possible to add corresponding symbols.
    """

    def __init__(self, pos: List[sp.Expr | int | None], symbols: Optional[List[sp.Symbol]] = None):
        """
        This constructor initializes an instance of a class with a mapping derived
        from the provided position list and symbols list. It maps symbolic expressions
        to their corresponding positions, allowing symbolic manipulation and evaluation.

        :param pos: List of symbolic expressions or None. Represents the position.
        :param symbols: List of symbolic variables or None. Represents the symbols
            used in conjunction with their positions from the `pos` parameter.
            Symbols need to align with the positions provided for accurate mapping.
        """
        mapping, symbols = self.__build_mapping(pos, symbols)
        super().__init__(mapping)
        self.ordered = [(c, sym) for c, sym in zip(pos, symbols)]
        for c, sym in self.ordered:
            if not isinstance(c, int | sp.Rational):
                raise ValueError('FuCKKKKKKK')

    def copy(self):
        return Position(list(self.values()), list(self.keys()))

    def __add__(self, other):
        if not isinstance(other, Position):
            raise NotImplementedError
        new = self.copy()
        new += other
        return new

    def __iadd__(self, other: dict):
        if not isinstance(other, Position):
            raise NotImplementedError
        for key in other:
            self[key] = self.get(key, 0) + other[key]
        return self

    @staticmethod
    def __build_mapping(pos: List[sp.Expr | None], symbols: List[sp.Symbol] | None):
        if symbols is None:
            symbols = sp.symbols(f"x:{len(pos)}")
        elif len(symbols) < len(pos) or len(set(symbols)) < len(pos):
            raise ValueError("Invalid symbols")

        for i, pos_elem in enumerate(pos):
            if pos_elem is None:
                pos[i] = -1
        return dict(zip(symbols, pos)), symbols

    def set_axis(self, symbols: List[sp.Symbol]) -> None:
        """
        Sets the symbols for the position (match each coordinate to its symbol).
        :param symbols: List of symbols to match the position to.
        """
        mapping, _ = self.__build_mapping(list(self.values()), symbols)
        self.clear()
        self.update(mapping)

    def as_list(self) -> List[sp.Expr]:
        """
        :return: The position as a list of sympy expressions.
        """
        return [c for c, _ in self.ordered]
        # return list(self.values())

    def as_sp_matrix(self):
        return sp.Matrix(self.as_list())

    def as_np_array(self):
        return np.array(self.as_list())
