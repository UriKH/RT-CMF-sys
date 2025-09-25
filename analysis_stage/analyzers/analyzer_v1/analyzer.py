from analysis_stage.analysis_scheme import AnalyzerScheme
from analysis_stage.errors import MissingStartPoints
from analysis_stage.subspaces.searchable import Searchable
from analysis_stage.subspaces.shard.shard_extraction import ShardExtractor
from search_stage.serial.serial_searcher import SerialSearcher
from utils.util_types import *


class Analyzer(AnalyzerScheme):
    def __init__(self, cmf: CMF, shift: Position):
        self.cmf = cmf
        self.shift = shift
        self.extractor = self.__prepare_extractor(self.cmf, self.shift)
        self.shards = self.extractor.get_shards()

    @staticmethod
    def __prepare_extractor(cmf, shift):
        extractor = ShardExtractor(cmf, shift)
        extractor.populate_cmf_start_points(expand_anyway=True)
        return extractor

    def search(self, method: str = 'sphere', length: int = 4) -> Dict[Position, Any]:
        managers = {}
        for shard in self.shards:
            start = shard.choose_start_point()
            searcher = SerialSearcher(shard)
            searcher.generate_trajectories(method, length, clear=False)
            managers[shard] = searcher.search(start, partial_search_factor=0.5)   # This is not finished
        return managers

    def prioritize(self, managers: Dict[Position, Any]) -> List[Searchable]:
        raise NotImplementedError
