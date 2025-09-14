import os

import configs.database
from data_managment.database import DBManager
from data_managment.functions.pFq_fmt import pFq_formatter
from pprint import pprint
import sympy as sp


def main():
    db = DBManager()
    try:
        db.set('pi', pFq_formatter(2, 1, sp.Rational(1, 2), [1, sp.Rational(3, 2)]))
        db.add_inspiration_function('pi', pFq_formatter(2, 2, sp.Rational(1, 2), [1, sp.Rational(3, 2)]))

        pprint(db.get('pi'))

        db.remove_inspiration_function('pi', pFq_formatter(2, 1, sp.Rational(1, 2), [1, sp.Rational(3, 2)]))
        pprint(db.get('pi'))
    finally:
        db.db.close()
        os.remove(configs.database.DEFAULT_PATH)


if __name__ == '__main__':
    main()
