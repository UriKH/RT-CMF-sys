"""
Global config file for system flow regarding DBs
"""

from configs.db_usages import DBUsages

# PARALLEL_EXEC = False               # try to run DBs in parallel if possible
USAGE = DBUsages.RETRIEVE_DATA      # execute DBs retrieve if retrieve is an option
INPUT_FILE = None                   # the input file will be used when DBUsages.STORE_DATA
                                    #    (file will be parsed and uploaded to the DBs)
