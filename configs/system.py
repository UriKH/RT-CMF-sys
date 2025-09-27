from configs.db_usages import DBUsages
import mpmath as mp

CONSTANTS = ['pi']
MODULE_ERROR_SHOW_TRACE = True
TQDM_CONFIG = {
    'bar_format': '{desc:<30}' + ' ' * 5 + '{bar} | {elapsed} {rate_fmt}',
    'ncols': 80
}
