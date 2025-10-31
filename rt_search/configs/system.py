import mpmath as mp
from dataclasses import dataclass, field

from .configurable import Configurable
from rt_search.utils.types import *


@dataclass
class SystemConfig(Configurable):
    # ============================== Arguments ==============================
    CONSTANTS: List[str] | str = field(default_factory=list)        # search for constants in the list

    # ============================== Printing and errors ==============================
    MODULE_ERROR_SHOW_TRACE: bool = True                            # show error trace if occurs
    TQDM_CONFIG: Dict[str, Any] = field(default_factory=dict)
    LOGGING_BUFFER_SIZE: int = 150  # when logging a buffer use width of terminal as 150 characters

    # ============================== constant mapping ==============================
    SYMPY_TO_MPMATH: Dict[str, mp] = field(default_factory=dict)

    def __post_init__(self):
        self.TQDM_CONFIG = {
            'bar_format': '{desc:<30}' + ' ' * 5 + '{bar} | {elapsed} {rate_fmt} ({percentage:.1f}%)',
            'ncols': 80
        }

        self.SYMPY_TO_MPMATH = {
            "pi": mp.pi,
            "E": mp.e,
            "EulerGamma": mp.euler,
            "Catalan": mp.catalan,
            "GoldenRatio": mp.phi,
            "zeta": mp.zeta,
        }

    EXPORT_CMFS: str = None


sys_config: SystemConfig = SystemConfig()
