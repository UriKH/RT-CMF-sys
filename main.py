import argparse

from analysis_stage.analyzers.analyzer_v1.analyzer_mod import AnalyzerMod
from system import System
from db_stage.DBs.db_v1.db_mod import DBMod


def main():
    System([DBMod('./db_yay.db', './db_yay.json')], [AnalyzerMod]).run(constants='pi')


if __name__ == '__main__':
    """
    we want:
    System("euler-gamma", DBMod, Analyzer, Searcher).load_and_run()
    
    how do we make sure this works?
    Connectors: define interface for DBMod, Analyzer, Searcher and in it define connectors that make sure that the data
     sent to the next module is in valid format.
     
    * DB's only job is to fetch the constant's inspiration funcs. 
        (We want to allow DB combining if we have 2 different DB's and we want to aggregate them)
    * Analyzer is a specific method implementation for prioritization. 
        (We want to allow different implementations of prioritization methods, in case we want user input on both options)
    * Searcher is a specific method implementation for trajectory search.
        (Here we can provide a list of search methods and execute all of them while checking cached trajectories)
    """
    main()
