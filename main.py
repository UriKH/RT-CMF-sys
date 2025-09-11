import os

from data_managment.database import DBManager
from data_managment.pFq_fmt import pFq_formatter
from pprint import pprint
import json
import sympy as sp


def main():
    db = DBManager()
    try:
        db.set('pi', pFq_formatter(2, 1, sp.Rational(1, 2), [1, sp.Rational(3, 2)]))
        db.add_inspiration_function('pi', pFq_formatter(2, 1, sp.Rational(1, 2), [1, sp.Rational(3, 2)]))

        pprint(db.get('pi'))

        db.remove_inspiration_function('pi', pFq_formatter(2, 1, sp.Rational(1, 2), [1, sp.Rational(3, 2)]))
        pprint(db.get('pi'))
    finally:
        os.remove("db.sql")


if __name__ == '__main__':
    main()
