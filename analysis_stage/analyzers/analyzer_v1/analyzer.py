from time import sleep

from analysis_stage.analysis_scheme import AnalyzerScheme
from analysis_stage.subspaces.searchable import Searchable
from analysis_stage.subspaces.shard.shard_extraction import ShardExtractor
from search_stage.data_manager import DataManager, SearchVector
from search_stage.serial.serial_searcher import SerialSearcher
from utils.util_types import *
from utils.logger import Logger
import configs.analysis as config_analysis

import mpmath as mp
from tqdm import tqdm


class Analyzer(AnalyzerScheme):
    def __init__(self, cmf: CMF, shift: Position, constant: mp.mpf):
        self.cmf = cmf
        self.shift = shift
        self.constant = constant
        self.extractor = self.__prepare_extractor(self.cmf, self.shift)
        self.shards = self.extractor.get_shards()

    @staticmethod
    def __prepare_extractor(cmf, shift):
        extractor = ShardExtractor(cmf, shift)
        extractor.populate_cmf_start_points(expand_anyway=True)
        return extractor

    def search(self, method: str = 'sphere', length: int = 4) -> Dict[Searchable, DataManager]:
        managers = {}
        for shard in tqdm(self.shards, desc=f'Searching shards ...'):
            start = shard.choose_start_point()
            searcher = SerialSearcher(shard, self.constant)
            searcher.generate_trajectories(method, length, clear=False)
            dm = searcher.search(start, partial_search_factor=0.5)

            identified = dm.is_valid()
            Logger(f'Identified {identified * 100}% of trajectories, best delta: {dm.best_delta()[0]}',
                   Logger.Levels.info).log()
            if identified >= config_analysis.IDENTIFY_THRESH:
                managers[shard] = dm
            sleep(0.1)
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

            while l <= r:
                mid = (l + r) // 2
                if num > ranks[mid]:
                    l = mid + 1
                else:
                    r = mid
            return l + 1

        ranked = {}
        for shard, dm in managers.items():
            ranked[shard] = {
                'delta_rank': match_rank(ranks, dm.best_delta()[0]),
                'dim': self.cmf.dim()
            }
        return ranked
