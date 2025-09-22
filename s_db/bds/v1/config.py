"""
Module configuration - specific to DB v1
"""
from configs.db_usages import DBUsages

DEFAULT_PATH = './families_v1.db'
ALLOWED_USAGES = [                  # allowed usages of the DB
    DBUsages.RETRIEVE_DATA,
    DBUsages.STORE_DATA
]
MULTIPLE_CONSTANTS = False          # allow operations on multiple constants
# PARALLEL = False                    # Allow parallelism
