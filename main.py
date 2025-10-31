from rt_search import *
from rt_search.db_stage.funcs.pFq_fmt import pFq_formatter
import sympy as sp


if __name__ == '__main__':
    config.configure(
        system={'EXPORT_CMFS': './mycmfs'}
    )
    results = System(
        if_srcs=[pFq_formatter('pi', 2, 1, sp.Rational(1, 2), [0, 0, sp.Rational(1, 2)])],
        analyzers=[AnalyzerModV1],
        searcher=SearcherModV1
    ).run(constants=['pi'])