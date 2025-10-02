from rt_search.system.serializable import Serializable
from rt_search.utils.types import *

from dataclasses import dataclass, field
from ramanujantools import Matrix
import pandas as pd
from collections import UserDict


@dataclass
class SearchVector(Serializable):
    """
    A class representing a search vector in a specific space
    """
    start: Position
    trajectory: Position

    def __hash__(self):
        return hash((self.start, self.trajectory))

    def as_json_serializable(self):
        return {'start': self.start.as_json_serializable(), 'trajectory': self.trajectory.as_json_serializable()}


@dataclass
class SearchData(Serializable):
    """
    A class representing a search data alongside a specific search vector
    """

    sv: SearchVector
    limit: float = None
    delta: float | str = None
    eigen_values: Dict = field(default_factory=dict)
    gcd_slope: float | None = None
    initial_values: Matrix = None
    LIReC_identify: bool = False
    errors: Dict[str, Exception | None] = field(default_factory=dict)

    def as_json_serializable(self):
        return {
            'sv': self.sv.as_json_serializable(),
            'limit': self.limit,
            'delta': self.delta,
            'eigen_values': self.eigen_values,
            'gcd_slope': self.gcd_slope,
            'initial_values': self.initial_values.tolist(),
            'LIReC_identify': self.LIReC_identify
            # 'errors': str(self.errors) # TODO: deal with saving errors
        }


class DataManager(UserDict[SearchVector, SearchData]):
    """
    DataManager represents a set of results found in a specific search in a CMF
    """

    def __init__(self, use_LIReC: bool):
        super().__init__()
        self.use_LIReC = use_LIReC

    @property
    def identified_percentage(self) -> float:
        """
        Computes the percentage identified by the search vector, if no data collected mark as 1 (i.e. 100%)
        :return: The percentage identified by the search vector as a number in [0, 1]
        """
        df = self.as_df()
        if df is None:
            return 1
        if self.use_LIReC:
            frac = df['LIReC_identify'].sum() / len(df['LIReC_identify'])
        else:
            frac = 1 - df['initial_values'].isna().sum() / len(df['initial_values'])
        return frac

    @property
    def best_delta(self) -> Tuple[Optional[float], Optional[SearchVector]]:
        """
        The best delta found
        :return: A tuple of the delta value and the search vector it was found in.
        """
        df = self.as_df()
        if df.empty:
            return None, None

        deltas = df['delta'].dropna()
        if deltas.empty:
            return None, None

        row = df.loc[deltas.idxmax()]
        return row['delta'], row['sv']

    def get_data(self) -> List[SearchData]:
        """
        Gather all search data in the manager into a list
        :return: The data collected as a list
        """
        return list(self.values())

    def as_df(self) -> pd.DataFrame:
        """
        Convert the data into a dataframe
        :return: The pandas dataframe.
        """
        rows = [
            {
                "sv": sv,
                "delta": data.delta,
                "limit": data.limit,
                "eigen_values": data.eigen_values,
                "gcd_slope": data.gcd_slope,
                "initial_values": data.initial_values,
                "LIReC_identify": data.LIReC_identify,
                "errors": data.errors,
            }
            for sv, data in self.items()
        ]
        return pd.DataFrame(rows)

    def as_json_serializable(self) -> list:
        return [
            {
                "sv": sv.as_json_serializable(),
                "delta": data.delta,
                "limit": data.limit,
                "eigen_values":  {str(k): str(v) for k, v in data.eigen_values.items()} if data.eigen_values else None,
                "gcd_slope": data.gcd_slope,
                "initial_values": str(data.initial_values.tolist()) if data.initial_values else None,
                "LIReC_identify": data.LIReC_identify,
                "errors": [{'where': where, 'type': type(error).__name__, 'msg': str(error)} for where, error in data.errors.items()]
            }
            for sv, data in self.items()
        ]
