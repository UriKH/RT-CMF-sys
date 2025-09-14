from search_init.searchable import Searchable
from utils.util_types import *


class Shard(Searchable):
    """
    A class representation of a CMF Shard
    """

    def __init__(self,
                 hps: List[sp.Expr],
                 symbols: List[sp.Symbol],
                 shard_id: ShardVec):
        """
        :param hps: The hyperplanes found in the CMF that compose the Shards
        :param symbols: The symbols used to define the hyperplanes
        :param shard_id: A +-1's vector. Each index corresponds to a hyperplane,
        representing if all the points in the shard are above the hyperplane or blow it (+1 = above, -1 = below).
        """
        self.hps = hps
        self.symbols = symbols
        self.shard_id = shard_id

    def __eq__(self, other: object) -> bool:
        """
        Shards are considered equal iff their vector representation is the same.
        :param other: The other shard
        :return: True if the representation is the same, else False.
        """
        if isinstance(other, Shard):
            return self.shard_id == other.shard_id
        raise NotImplementedError

    def __hash__(self):
        """
        Hash the Shard using the vector representation.
        :return: The hash value for the tuple
        """
        return hash(self.shard_id)

    def in_shard(self, point: Tuple[int | sp.Rational, ...]) -> bool:
        """
        Checks if a point is within the Shard's borders.
        :param point: A tuple representing a coordinate in the lattice
        :return: True if the point is within the shard, else False.
        """
        point = {sym: v for sym, v in zip(self.symbols, point)}
        return all(exp.subs(point) == indicator for exp, indicator in zip(self.hps, self.shard_id))

    def __repr__(self):
        """
        Shard representation is the unique +-1 tuple representing it
        :return: The string representation of the tuple
        """
        return str(self.shard_id)
