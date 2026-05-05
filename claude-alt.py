import sys
sys.path.insert(0, '/mnt/user-data/uploads')
from problem import Problem


class Solver:
    """
    Deterministic solver for the 4-bit rotating nibble problem.
    Guarantees a win in at most 5 moves against fully adversarial rotation.

    Move 1  OPPOSITE(0101)  Force 00          any input -> 00
    Move 2  OPPOSITE(0101)  Zero-inject       00->11,  else->00
    Move 3  OPPOSITE(0101)  Demote-top        00->00, mixed->11, 11->10
    Move 4  ADJACENT(0011)  Flip both         any input -> NOT(input)
    Move 5  OPPOSITE(0101)  Zero-inject       00->11,  else->00
    """

    OPPOSITE = 0b0101
    ADJACENT = 0b0011

    @staticmethod
    def _force_zeros(mask, bits):
        return 0

    @staticmethod
    def _zero_inject(mask, bits):
        return mask if bits == 0 else 0

    @staticmethod
    def _demote_top(mask, bits):
        if bits == 0:
            return 0
        elif bits == mask:
            return mask & ~1    # 11 -> 10  (clears bit 0)
        else:
            return mask         # 01 or 10 -> 11

    @staticmethod
    def _flip_both(mask, bits):
        return mask ^ bits

    def solve(self, problem):
        moves = [
            (self.OPPOSITE, self._force_zeros,  "OPP: force 00"),
            (self.OPPOSITE, self._zero_inject,  "OPP: 00->11, else->00"),
            (self.OPPOSITE, self._demote_top,   "OPP: 00->00, mixed->11, 11->10"),
            (self.ADJACENT, self._flip_both,    "ADJ: flip both bits"),
            (self.OPPOSITE, self._zero_inject,  "OPP: 00->11, else->00"),
        ]

        print("=" * 50)
        for mask, cb, rationale in moves:
            print(f"  [{rationale}]")
            result = problem.move(mask, cb)
            if result:
                return result

        raise RuntimeError("Solver failed — this should never happen.")


if __name__ == "__main__":
    import io, sys

    solver = Solver()
    total = 10000
    wins = 0
    by_turn = {}

    print(f"Running {total} trials...\n")
    for _ in range(total):
        p = Problem()
        old = sys.stdout
        sys.stdout = io.StringIO()
        try:
            result = solver.solve(p)
        finally:
            sys.stdout = old
        if result:
            wins += 1
            by_turn[result] = by_turn.get(result, 0) + 1

    print(f"Solved:  {wins}/{total}  ({100.0*wins/total:.2f}%)")
    print(f"Failed:  {total - wins}/{total}")
    print(f"Turns:   { {k: by_turn[k] for k in sorted(by_turn)} }")
    print()
    print("--- Single verbose game ---")
    solver.solve(Problem())

