from utils.util_types import *
from ramanujantools.cmf import CMF


class ShardExtractor:

    def __init__(self, cmf: CMF, shifts: List[Shift]):
        self.cmf = cmf
        self.shifts = shifts
        self.shard_data = self.__extract_shards_data(cmf)

    @staticmethod
    def __extract_shards_data(cmf: CMF) -> List[Tuple]:
        def zero_det_solve(mat: sp.Matrix) -> Set[FrozenSet]:
            return freeze(sp.solve(mat.det()))

        def undefined_solve(mat: sp.Matrix) -> Set[FrozenSet]:
            l = []
            for v in mat.iter_values():
                if (den := v.as_numer_denom()[1]) == 1:
                    continue
                for sym in den.free_symbols:
                    for sol in sp.solve(den, sym):
                        l.append({sym: sol})
            return freeze(l)

        def freeze(l) -> Set[FrozenSet]:
            sols = set()
            for sol in l:
                sols.add(frozenset(sol.items()))
            return sols

        def unfreeze(sols: Set[FrozenSet]) -> List[Tuple[sp.Expr, ...]]:
            clean = [set(tuple(sol)[0]) for sol in sols]
            solutions = set(tuple(tup) for tup in clean)
            return list(solutions)

        data = set()
        for sym, mat in cmf.matrices.items():
            z_det = zero_det_solve(mat)
            undef = undefined_solve(mat)
            data = data.union(z_det.union(undef))
        return unfreeze(data)

