import os

import configs.database
from s_db.database import DBManager
from s_db.functions.pFq_fmt import pFq_formatter
from pprint import pprint
import sympy as sp

x0, x1 = sp.symbols('x0 x1')


def main():
    db = DBManager()
    try:
        db.set('pi', pFq_formatter(11, 1, sp.Rational(1, 2)))
        db.add_inspiration_function('pi', pFq_formatter(2, 2, sp.Rational(1, 2), [0, None, sp.Rational(1, 2), 0]))

        print(db.get('pi'))

        db.remove_inspiration_function('pi', pFq_formatter(2, 2, sp.Rational(1, 2), [0, None, sp.Rational(1, 2), 0]))
        print(db.get('pi'))
    finally:
        db.db.close()
        os.remove(configs.database.DEFAULT_PATH)


if __name__ == '__main__':
    # main()
    s = set([1])
    print(s)
