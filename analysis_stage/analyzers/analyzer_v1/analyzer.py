from analysis_stage.analysis_scheme import AnalyzerScheme
from analysis_stage.subspaces.searchable import Searchable
from analysis_stage.subspaces.shard.shard_extraction import ShardExtractor

from search_stage.data_manager import DataManager, SearchVector
from search_stage.serial.serial_searcher import SerialSearcher

from utils.util_types import *
from utils.logger import Logger

from configs import (
    analysis as config_analysis,
    system as sys_config
)

import mpmath as mp
from tqdm import tqdm
from time import sleep


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
                f'Could not find valid start points for {bad_shards}/{len(self.shards)}.'
                f'\nTry increasing MAX_EXPANSIONS or changing the shift values.', Logger.Levels.warning
            ).log(msg_prefix='\n')

        for shard in tqdm(self.shards, desc=f'Searching shards', **sys_config.TQDM_CONFIG):
            start = shard.choose_start_point()
            if start is None:
                Logger(
                    f'Could not find valid start point search in shard (probably due to shift).'
                    f' Try increasing MAX_EXPANSIONS.', Logger.Levels.warning,
                    condition=config_analysis.WARN_ON_EMPTY_SHARDS
                ).log(msg_prefix='\n')
                continue
            searcher = SerialSearcher(shard, self.constant, use_LIReC=config_analysis.USE_LIReC, deep_search=False)
            searcher.generate_trajectories(method, length, clear=False)
            dm = searcher.search(start, partial_search_factor=0.5)

            identified = dm.is_valid()
            Logger(f'Identified {identified * 100}% of trajectories, best delta: {dm.best_delta()[0]}',
                   Logger.Levels.info).log(msg_prefix='\n')
            if identified > config_analysis.IDENTIFY_THRESH:
                managers[shard] = dm
            else:
                Logger(
                    f'Ignoring shard - identified <= {config_analysis.IDENTIFY_THRESH}% of tested trajectories.',
                    Logger.Levels.info
                ).log()
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
            best_delta = dm.best_delta()[0]
            if best_delta is None:
                continue
            ranked[shard] = {
                'delta_rank': match_rank(ranks, best_delta),
                'dim': self.cmf.dim()
            }
        return ranked
