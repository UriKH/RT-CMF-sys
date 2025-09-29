from utils.util_types import *
from dataclasses import dataclass, field
import mpmath as mp
from ramanujantools import Matrix, Limit
import pandas as pd
from collections import UserDict


@dataclass
class SearchVector:
    start: Position
    trajectory: Position

    def __hash__(self):
        return hash((self.start, self.trajectory))


@dataclass
class SearchData:
    sv: SearchVector
    limit: float = None
    delta: float | str = None
    eigen_values: Dict = field(default_factory=dict)
    gcd_slope: float | None = None
    initial_values: Matrix = None
    LIReC_identify: bool = False
    errors: Dict[str, Exception | None] = field(default_factory=dict)


class DataManager(UserDict[SearchVector, SearchData]):
    def __init__(self, use_LIReC: bool):
        super().__init__()
        self.use_LIReC = use_LIReC

    def is_valid(self) -> float:
        df = self.as_df()
        if df is None:
            return 1
        if self.use_LIReC:
            frac = df['LIReC_identify'].sum() / len(df['LIReC_identify'])
        else:
            frac = 1 - df['initial_values'].isna().sum() / len(df['initial_values'])
        return frac

    def best_delta(self):
        df = self.as_df()
        if df.empty:
            return None, None

        deltas = df['delta'].dropna()
        if deltas.empty:
            return None, None

        row = df.loc[deltas.idxmax()]
        return row['delta'], row['sv']

    def get_data(self):
        return list(self.values())

    def as_df(self):
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
