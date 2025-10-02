from dataclasses import dataclass, fields

from .configurable import Configurable


@dataclass
class AnalysisConfig(Configurable):
    """
    Stage analysis configurations
    """
    # ============================= Mathematical error tolerance =============================
    SHARD_EXTRACTOR_ERR: float = 1e-6

    # ============================= Parallelism and efficiency =============================
    USE_CACHING: bool = True  # use caching for lru_cache
    PARALLEL_SHARD_ANALYSIS: bool = False                           # preform shard analysis on parallel
    SHARD_VALIDATION_CHUNK: int = 15
    HP_CALC_CHUNK: int = 10

    NUM_TRAJECTORIES_FROM_DIM: callable = (lambda dim: 10 ** dim)     # #trajectories to analyze given searchable dims
    IDENTIFY_THRESHOLD: float = -1  # consider a shard as related to a constant: threshold > identified_trajectories(%)
    MAX_EXPANSIONS: int = 3         # Times to expand search for start points beyond the 3 by 3 cube around the origin

    # ============================= Printing and error management =============================
    PRINT_SHARDS: bool = True
    PRINT_FOR_EVERY_SEARCHABLE: bool = True         # print the result of each analysis of a searchable object
    WARN_ON_EMPTY_SHARDS: bool = False              # warn user if start points could not be found in the shards

    # ============================= Analysis features =============================
    USE_LIReC: bool = True                  # use LIReC in analysis instead of RT functions
    PARTIAL_SEARCH_FACTOR: float = 0.3      # search only a part of the trajectories generated
    ANALYZE_LIMIT: bool = False             # calculate the limit
    ANALYZE_EIGEN_VALUES: bool = False      # calculate the trajectory matrix eigen values
    ANALYZE_GCD_SLOPE: bool = False         # calculate the gcd slope of the trajectory


analysis_config: AnalysisConfig = AnalysisConfig()
