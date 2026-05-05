from problem import Problem
class Solver:
    def __init__(self):
        self.program = [
            (0b0011, self.flip_if_equal),   # A
            (0b0101, self.flip_if_equal),   # B
            (0b0011, self.force_one),       # A
            (0b0101, self.force_one),       # B
            (0b0011, self.finalize),        # A
        ]

    # --- Phase 1: destroy stability ---
    def flip_if_equal(self, mask, v):
        # 00 -> 11
        # 11 -> 00
        # 01,10 unchanged
        if v == 0:
            return mask
        if v == mask:
            return 0
        return v

    # --- Phase 2: inject 1s everywhere reachable ---
    def force_one(self, mask, v):
        # any non-zero becomes 11
        return mask if v != 0 else 0

    # --- Phase 3: final collapse ---
    def finalize(self, mask, v):
        return 0 if v == 0 else mask

    def solve(self, problem):
        for mask, cb in self.program:
            result = problem.move(mask, cb)
            if result:
                return result
        return 0

if __name__ == "__main__":
	for _ in range(0,5): Solver().solve(Problem())