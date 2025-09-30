from configs.db_usages import DBUsages
import mpmath as mp

CONSTANTS = ['pi']
MODULE_ERROR_SHOW_TRACE = True
TQDM_CONFIG = {
    'bar_format': '{desc:<30}' + ' ' * 5 + '{bar} | {elapsed} {rate_fmt} ({percentage:.1f}%)',
    'ncols': 80
}
LOGGING_BUFFER = 150
SYMPY_TO_MPMATH = {
    "pi": mp.pi,
    "E": mp.e,
    "EulerGamma": mp.euler,
    "Catalan": mp.catalan,
    "GoldenRatio": mp.phi,
    "zeta": mp.zeta,
}