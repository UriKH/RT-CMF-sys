from analysis_stage.analysis_scheme import AnalyzerModScheme
from utils.util_types import *
from system import System
from analysis_stage.analyzers.analyzer_v1.analyzer import Analyzer
from analysis_stage.subspaces.searchable import Searchable


class AnalyzerMod(AnalyzerModScheme):
    """
    The class represents the module for CMF analysis and shard search filtering and prioritization.
    """

    def __init__(self, cmf_data: Dict[str, List[CMFtup]]):
        super().__init__(
            description='Module for CMF analysis and shard search filtering and prioritization',
            version='1'
        )
        self.cmf_data = cmf_data

    def execute(self) -> Dict[str, List[Searchable]]:
        """
        The main function of the module. It performs the following steps:
        * Store all CMFs
        * extract shards for each CMF
        * for each CMF generate start points and trajectories
        * search each shard for shallow search and get the data
        * prioritize for deep search
        """
        def merge_dicts(dict_list: List[Dict]) -> Dict:
            merged = {}
            for d in dict_list:
                merged.update(d)
            return merged

        queues = {c: [] for c in self.cmf_data.keys()}
        for constant, cmf_tups in self.cmf_data.items():
            queue = []
            for cmf, shift in cmf_tups:
                analyzer = Analyzer(cmf, shift, System.get_const_as_mpf(constant))
                dms = analyzer.search()
                queue.append(analyzer.prioritize(dms))
            merged = merge_dicts(queue)
            queues[constant] = sorted(
                merged.keys(),
                key=lambda space: (-merged[space]['rank'], merged[space]['dim'])
            )
        return queues
