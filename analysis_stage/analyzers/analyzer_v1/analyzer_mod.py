from analysis_stage.analysis_scheme import AnalyzerModScheme
from utils.geometry.point_generator import PointGenerator
from utils.logger import Logger
from utils.types import *
from system.system import System
from analysis_stage.analyzers.analyzer_v1.analyzer import Analyzer
from analysis_stage.analyzers.analyzer_v1.config import *
from analysis_stage.subspaces.searchable import Searchable
from system.module import CatchErrorInModule
import configs.system as sys_config

from tqdm import tqdm


class AnalyzerModV1(AnalyzerModScheme):
    """
    The class represents the module for CMF analysis and shard search filtering and prioritization.
    """

    def __init__(self, cmf_data: Dict[str, List[CMFtup]]):
        super().__init__(
            description='Module for CMF analysis and shard search filtering and prioritization',
            version='1'
        )
        self.cmf_data = cmf_data

    @CatchErrorInModule(with_trace=sys_config.MODULE_ERROR_SHOW_TRACE, fatal=True)
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
        for constant, cmf_tups in tqdm(self.cmf_data.items(), desc='Analyzing constants and their CMFs',
                                       **sys_config.TQDM_CONFIG):
            queue: List[Dict[Searchable, Dict[str, int]]] = []

            Logger(
                Logger.buffer_print(sys_config.LOGGING_BUFFER, f'Analyzing for {constant}', '=')
            ).log(msg_prefix='\n')
            for cmf, shift in cmf_tups:
                Logger(
                    Logger.buffer_print(sys_config.LOGGING_BUFFER, f'Current CMF: {cmf} with shift {shift}', '=')
                ).log(msg_prefix='\n')
                analyzer = Analyzer(constant, cmf, shift, System.get_const_as_sp(constant))
                dim = cmf.dim()
                dms = analyzer.search(length=PointGenerator.calc_sphere_radius(NUM_OF_TRAJ_FROM_DIM(dim), dim))
                queue.append(analyzer.prioritize(dms))
                # TODO: Now we want to take the DataManagers and convert whose to databases per CMF - I don't know if we really want this or not...
            merged: Dict[Searchable, Dict[str, int]] = merge_dicts(queue)
            queues[constant] = sorted(
                merged.keys(),
                key=lambda space: (-merged[space]['delta_rank'], merged[space]['dim'])
            )
        return queues
