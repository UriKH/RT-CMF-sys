# import os
#
# import configs.database
# from db_stage.database import DBManager
# from db_stage.funcs.pFq_fmt import pFq_formatter
# from pprint import pprint
# import sympy as sp

# x0, x1 = sp.symbols('x0 x1')
#
#
# def main():
#     db = DBManager()
#     try:
#         db.set('pi', pFq_formatter(11, 1, sp.Rational(1, 2)))
#         db.add_inspiration_function('pi', pFq_formatter(2, 2, sp.Rational(1, 2), [0, None, sp.Rational(1, 2), 0]))
#
#         print(db.get('pi'))
#
#         db.remove_inspiration_function('pi', pFq_formatter(2, 2, sp.Rational(1, 2), [0, None, sp.Rational(1, 2), 0]))
#         print(db.get('pi'))
#     finally:
#         db.db.close()
#         os.remove(configs.database.DEFAULT_PATH)

import argparse



def main(args=None):
    print('Hello World!')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interactive', type=int, default=1)
    parsed_args = parser.parse_args(args)

    if parsed_args.interactive:
        """
        * Ask user for a constant
        * fetch
        * ask user to choose analyzer based on configurations and allow configuration change
        * run analysis
        * visualize results to user and wait for action, ask confirmation to continue
        * ask for deep search method (user can change configs)
        * run deep search
        """
        pass
    else:
        """
        Run the predefined system as given in the config file
        """
        pass


if __name__ == '__main__':
    from system import System
    from db_stage.DBs.db_v1.db_mod import DBMod
    System([DBMod('./db_yay.db')]).run()
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
    def func():
        pass
    main()
