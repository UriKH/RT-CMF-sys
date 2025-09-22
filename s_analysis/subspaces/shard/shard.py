from s_analysis.subspaces.searchable import Searchable
from s_analysis.subspaces.shard.shard_extraction import ShardExtractor
from utils.util_types import *


class Shard(Searchable):
    """
    A class representation of a CMF Shard.
    The Shard is a searchable object (similar to the Border which is not yet implemented).
    Thus, we want to be able to
    """

    def __init__(self,
                 shard_id: ShardVec,
                 extractor: ShardExtractor):
        """
        :param hps: The hyperplanes found in the CMF that compose the Shards
        :param symbols: The symbols used to define the hyperplanes
        :param shard_id: A +-1's vector. Each index corresponds to a hyperplane,
        representing if all the points in the shard are above the hyperplane or blow it (+1 = above, -1 = below).
        """
        super().__init__(len(extractor.symbols), extractor.cmf, extractor.symbols)
        self.hps = extractor.hps
        self.shard_id = shard_id
        self.extractor = extractor

    def __eq__(self, other: object) -> bool:
        """
        Shards are considered equal iff their vector representation is the same.
        :param other: The other Shard
        :return: True if the representation is the same, else False.
        """
        if isinstance(other, Shard):
            return self.shard_id == other.shard_id and self.extractor == other.extractor
        raise NotImplementedError

    def __hash__(self):
        """
        Hash the Shard using the vector representation.
        :return: The hash value for the tuple
        """
        return hash(self.shard_id)

    def __repr__(self):
        """
        Shard representation is the unique +-1 tuple representing it
        :return: The string representation of the tuple
        """
        return str(self.shard_id)

    def in_space(self, point: Position) -> Tuple[bool, ShardVec]:
        """
        Checks if a point is within the Shard's borders.
        :param point: A tuple representing a coordinate in the lattice
        :return: True if the point is within the shard, else False.
        """
        encoded = ShardExtractor.encode_point(point, self.hps)
        return encoded == self.shard_id, encoded

    def trajectory_in_space(self, start: Position, trajectory: Position) -> bool:
        if not self.in_space(start):
            return False
        for plane in self.hps:
            d = plane.intersection_with_line_coeff(start, trajectory)
            if d is not None and d >= 0:
                return False
        return True

    # def get_trajectory_orientation(self, trajectory: Position) -> ShardVec:
    #     """
    #     Encode the validity of the trajectory with respect to the shard hyperplanes.
    #     If the trajectory points to a valid direction given that the start point will be inside the Shard
    #     the encoding of the Shard will be returned.
    #     Otherwise, the encoding of the correct shard matching the trajectory will be returned.
    #     :param trajectory:
    #     :return:
    #     """
    #     # TODO: This function must be tested and visualized. This makes sense intuitively but I am not sure about it.
    #     # TODO: finish documenting this
    #     orientation = []
    #     start = Position([0] * len(trajectory))
    #     _, encoded = self.in_space(start)
    #     for i, hp in enumerate(self.hps):
    #         d = hp.intersection_with_line_coeff(start.as_sp_matrix(), trajectory.as_sp_matrix())
    #         sign = -1 if d is None or d < 0 else 1
    #         orientation.append(sign * self.shard_id[i])
    #     return tuple(orientation)

    def add_start_points(self, start_points: List[Position] | Position, filtering=True) -> None:
        if isinstance(start_points, Position):
            start_points = [start_points]
        if filtering:
            start_points = [point for point in start_points if self.in_space(point)[0]]
        self._start_points.update(start_points)

    def remove_start_points(self, start_points: List[Position] | Position) -> None:
        if isinstance(start_points, Position):
            start_points = [start_points]
        self._start_points.difference_update(start_points)

    def clear_start_points(self) -> None:
        self._start_points.clear()

    def choose_start_point(self) -> Position:
        if not self._start_points:
            self.extractor.populate_cmf_start_points()
        temp = self._start_points.pop()
        self._start_points.add(temp)
        return temp

    def get_start_points(self) -> Set[Position]:
        if not self._start_points:
            self.extractor.populate_cmf_start_points()
        return self._start_points
