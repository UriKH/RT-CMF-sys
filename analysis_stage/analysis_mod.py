from search_stage.serial.serial_searcher import SerialSearcher
from module import Module
from analysis_stage.subspaces.shard.shard_extraction import ShardExtractor
from utils.util_types import *


class Analyzer(Module):
    """
    The class represents the module for CMF analysis and shard search filtering and prioritization.
    """

    def __init__(self, cmfs: CMFlist, constant: str):
        super().__init__(
            description='Module for CMF analysis and shard search filtering and prioritization',
            version='1'
        )
        self.cmfs = cmfs
        self.constant = constant

    def execute(self):
        """
        The main function of the module. It performs the following steps:
        * Store all CMFs
        * extract shards for each CMF
        * for each CMF generate start points and trajectories
        * search each shard for shallow search and get the data
        * prioritize for deep search
        """
        priority_list = []

        for cmf in self.cmfs:
            extractor = ShardExtractor(*cmf)
            extractor.populate_cmf_start_points(expand_anyway=True)
            for shard in extractor.get_shards():
                start = shard.choose_start_point()
                searcher = SerialSearcher(shard)
                searcher.generate_trajectories('sphere', 4, clear=False)
                searcher.search(start, partial_search_factor=0.5)
                data = searcher.get_data()
                # TODO: when finishing the implementation of SerialSearcher update this too!
                """
                searcher = Serial(start, shard)
                searcher.generate_trajectories()
                    # searcher.generate_start_points() // Optional
                searcher.search()
                data = searcher.get_data()      <- we need to think about the data format here.
                if data is not enough:
                    searcher.enrich_trajectories()
                    searcher.search()
                if data['constant'] == self.constant:
                    priority_list.append((shard, searcher))
                """
        """
        priority_list = sorted(priority_list, key=lambda x: x[1].best_delta))
        """
        return priority_list
