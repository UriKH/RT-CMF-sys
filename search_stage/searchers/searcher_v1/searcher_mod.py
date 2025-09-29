from analysis_stage.subspaces.searchable import Searchable
from search_stage.data_manager import DataManager
from search_stage.searcher_scheme import SearcherModScheme
from search_stage.methods.serial.serial_searcher import SerialSearcher
from utils.util_types import *

from system import System
from utils.point_generator import PointGenerator


class SearcherMod(SearcherModScheme):
    def __init__(self, searcahbles: List[Searchable], use_LIReC: bool):
        super().__init__(
            description='Searcher module - orchestrating a deep search within a prioritized list of spaces',
            version='0.0.1'
        )
        self.searcahbles = searcahbles
        self.use_LIReC = use_LIReC

    def execute(self):
        dms: Dict[Searchable, DataManager] = dict()
        for space in self.searcahbles:
            searcher = SerialSearcher(space, System.get_const_as_mpf(space.const_name), use_LIReC=self.use_LIReC)
            searcher.generate_trajectories(
                'sphere',
                PointGenerator.calc_sphere_radius(10 ** space.dim, space.dim)   # TODO: convert this to the config
            )
            start = space.choose_start_point()
            dms[space] = searcher.search(start, partial_search_factor=1)
        return dms
