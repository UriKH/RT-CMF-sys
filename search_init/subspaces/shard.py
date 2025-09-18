from search_init.searchable import Searchable
from utils.util_types import *
from utils.plane import Plane


class Shard(Searchable):
    """
    A class representation of a CMF Shard
    """

    def __init__(self,
                 hps: List[Plane],
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
        self.trajectories = set()
        self.start_points = set()

    def __eq__(self, other: object) -> bool:
        """
        Shards are considered equal iff their vector representation is the same.
        :param other: The other Shard
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

    def __repr__(self):
        """
        Shard representation is the unique +-1 tuple representing it
        :return: The string representation of the tuple
        """
        return str(self.shard_id)

    def is_point_in_space(self, point: Position) -> Tuple[bool, ShardVec]:
        """
        Checks if a point is within the Shard's borders.
        :param point: A tuple representing a coordinate in the lattice
        :return: True if the point is within the shard, else False.
        """
        encoded = self.encode_point(point)
        return encoded == self.shard_id, encoded

    def is_trajectory_in_space(self, start: Position, trajectory: Position) -> bool:
        if not self.is_point_in_space(start):
            return False
        return self.get_trajectory_orientation(trajectory) == self.shard_id

    def encode_point(self, point: Position) -> ShardVec:
        """
        Encodes the shard that the point is within its borders.
        :param point: The point as a tuple
        :return: The Shard encoding +-1's vector
        """
        # TODO: add 0 for case that the point is on the plane
        return tuple((1 if plane.expression.subs(point) > 0 else -1) for plane in self.hps)

    def get_trajectory_orientation(self, trajectory: Position) -> ShardVec:
        """
        Encode the validity of the trajectory with respect to the shard hyperplanes.
        If the trajectory points to a valid direction given that the start point will be inside the Shard
        the encoding of the Shard will be returned.
        Otherwise, the encoding of the correct shard matching the trajectory will be returned.
        :param trajectory:
        :return:
        """
        # TODO: This function must be tested and viualized. This makes sense intuitively but I am not sure about it.
        # TODO: finish documenting this
        orientation = []
        start = Position([0] * len(trajectory))
        _, encoded = self.is_point_in_space(start)
        for i, hp in enumerate(self.hps):
            d = hp.intersection_with_line_coeff(start.as_sp_matrix(), trajectory.as_sp_matrix())
            sign = -1 if d is None or d < 0 else 1
            orientation.append(sign * self.shard_id[i])
        return tuple(orientation)

    def add_trajectories(self, trajectories: List[Position] | Position) -> None:
        if isinstance(trajectories, Position):
            trajectories = [trajectories]
        self.trajectories.update(trajectories)

    def add_start_points(self, start_points: List[Position] | Position) -> None:
        if isinstance(start_points, Position):
            start_points = [start_points]
        self.start_points.update(start_points)

    def remove_trajectories(self, trajectories: List[Position] | Position) -> None:
        if isinstance(trajectories, Position):
            trajectories = [trajectories]
        self.trajectories.difference_update(trajectories)

    def remove_start_points(self, start_points: List[Position] | Position) -> None:
        if isinstance(start_points, Position):
            start_points = [start_points]
        self.start_points.difference_update(start_points)

    def clear_start_points(self) -> None:
        self.start_points.clear()

    def clear_trajectories(self) -> None:
        self.trajectories.clear()
