from rt_search.analysis_stage.subspaces.searchable import Searchable
from ...data_manager import DataManager
from ...searcher_scheme import SearcherModScheme
from ...methods.serial.serial_searcher import SerialSearcher
from . import config as search_config
from rt_search.utils.types import *
from rt_search.utils.geometry.point_generator import PointGenerator
from rt_search.system.system import System
from rt_search.system.module import CatchErrorInModule
from rt_search.configs import sys_config

from tqdm import tqdm


class SearcherModV1(SearcherModScheme):
    def __init__(self, searcahbles: List[Searchable], use_LIReC: bool):
        super().__init__(
            description='Searcher module - orchestrating a deep search within a prioritized list of spaces',
            version='0.0.1'
        )
        self.searcahbles = searcahbles
        self.use_LIReC = use_LIReC

    @CatchErrorInModule(with_trace=sys_config.MODULE_ERROR_SHOW_TRACE, fatal=True)
    def execute(self):
        dms: Dict[Searchable, DataManager] = dict()
        for space in tqdm(self.searcahbles, desc='Searching the searchable spaces: ', **sys_config.TQDM_CONFIG):
            searcher = SerialSearcher(space, System.get_const_as_sp(space.const_name), use_LIReC=self.use_LIReC)
            searcher.generate_trajectories(
                'sphere',
                PointGenerator.calc_sphere_radius(search_config.NUM_OF_TRAJ_FROM_DIM(space.dim), space.dim)
            )
            start = space.choose_start_point()
            dms[space] = searcher.search(
                start, partial_search_factor=1,
                find_limit=search_config.FIND_LIMIT,
                find_gcd_slope=search_config.FIND_GCD_SLOPE,
                find_eigen_values=search_config.FIND_EIGEN_VALUES
            )
        return dms
