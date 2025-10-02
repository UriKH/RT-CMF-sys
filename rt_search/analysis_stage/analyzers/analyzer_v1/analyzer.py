from ...analysis_scheme import AnalyzerScheme
from ...subspaces.searchable import Searchable
from ...subspaces.shard.shard_extraction import ShardExtractor
from rt_search.search_stage.data_manager import DataManager
from rt_search.search_stage.methods.serial.serial_searcher import SerialSearcher
from rt_search.utils.types import *
from rt_search.utils.logger import Logger
from rt_search.configs import (
    sys_config,
    analysis_config
)

import mpmath as mp
from tqdm import tqdm


class Analyzer(AnalyzerScheme):
    def __init__(self, const_name: str, cmf: CMF, shift: Position, constant: mp.mpf):
        self.cmf = cmf
        self.shift = shift
        self.constant = constant
        self.extractor = self.__prepare_extractor(const_name, self.cmf, self.shift)
        self.shards = self.extractor.get_shards()

    @staticmethod
    def __prepare_extractor(const_name, cmf, shift):
        extractor = ShardExtractor(const_name, cmf, shift)
        extractor.populate_cmf_start_points(expand_anyway=True)
        return extractor

    def search(self, method: str = 'sphere', length: int = 4) -> Dict[Searchable, DataManager]:
        managers = {}
        bad_shards = 0
        for shard in self.shards:
            if shard.choose_start_point() is None:
                bad_shards += 1
        if bad_shards > 0:
            Logger(
                f'Could not find valid start points for {bad_shards}/{len(self.shards)} of the shards.'
                f'\nTry increasing MAX_EXPANSIONS or changing the shift values.', Logger.Levels.warning
            ).log(msg_prefix='\n')

        for shard in tqdm(self.shards, desc=f'Analyzing shards', **sys_config.TQDM_CONFIG):
            start = shard.choose_start_point()
            if start is None:
                Logger(
                    f'Could not find valid start point search in shard (probably due to shift).'
                    f' Try increasing MAX_EXPANSIONS.', Logger.Levels.warning,
                    condition=analysis_config.WARN_ON_EMPTY_SHARDS
                ).log(msg_prefix='\n')
                continue
            searcher = SerialSearcher(shard, self.constant, use_LIReC=analysis_config.USE_LIReC, deep_search=False)
            searcher.generate_trajectories(method, length, clear=False)
            dm = searcher.search(
                start,
                partial_search_factor=analysis_config.PARTIAL_SEARCH_FACTOR,
                find_limit=analysis_config.ANALYZE_LIMIT,
                find_gcd_slope=analysis_config.ANALYZE_GCD_SLOPE,
                find_eigen_values=analysis_config.ANALYZE_EIGEN_VALUES
            )

            identified = dm.identified_percentage
            best_delta = dm.best_delta[0]
            if analysis_config.PRINT_FOR_EVERY_SEARCHABLE:
                if best_delta is None:
                    Logger(f'Identified {identified * 100:.2f}% of trajectories, best delta: {best_delta}',
                           Logger.Levels.info).log(msg_prefix='\n')
                else:
                    Logger(f'Identified {identified * 100:.2f}% of trajectories, best delta: {best_delta:.4f}',
                           Logger.Levels.info).log(msg_prefix='\n')
            if identified > analysis_config.IDENTIFY_THRESHOLD:
                managers[shard] = dm
            else:
                Logger(
                    f'Ignoring shard - identified <= {analysis_config.IDENTIFY_THRESHOLD ** 100}% of tested trajectories.',
                    Logger.Levels.info
                ).log(msg_prefix='\n')
        return managers

    def prioritize(self, managers: Dict[Searchable, DataManager], ranks=3) -> Dict[Searchable, Dict[str, int]]:
        if ranks < 3:
            Logger('prioritization ranks must be >= 3 (resulting to default = 3), '
                   'continuing to prevent data loss', Logger.Levels.inform).log()

        def match_rank(n: int, num):
            step = 1 / n
            ranks = [-1 + k * step for k in range(n + 1)]
            l = 0
            r = len(ranks) - 1

            while l < r:
                mid = (l + r) // 2
                if num > ranks[mid]:
                    l = mid + 1
                else:
                    r = mid
            return l + 1

        ranked = {}
        for shard, dm in managers.items():
            best_delta = dm.best_delta[0]
            if best_delta is None:
                continue
            ranked[shard] = {
                'delta_rank': match_rank(ranks, best_delta),
                'dim': self.cmf.dim()
            }
        return ranked
