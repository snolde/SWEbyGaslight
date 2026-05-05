from problem import Problem
class Solver:
    def __init__(self):
        # Fixed finite sequence (mask, callback)
        self.program = [
            (0b0011, self.step1),
            (0b0101, self.step2),
            (0b0011, self.step3),
            (0b0101, self.step4),
            (0b0011, self.finish),
        ]

    # --- Callbacks ---

    def step1(self, mask, v):
        # Normalize first pair:
        # 00->00, 01->01, 10->01, 11->11
        # (forces ordering / breaks symmetry)
        return 0b01 if v in (0b10,) else v

    def step2(self, mask, v):
        # Inject asymmetry:
        # collapse mixed states
        return 0b11 if v in (0b01, 0b10) else v

    def step3(self, mask, v):
        # Force partial consensus
        return 0b11 if v != 0 else 0

    def step4(self, mask, v):
        # Remove remaining ambiguity
        return 0b00 if v == 0 else 0b11

    def finish(self, mask, v):
        # Final collapse: everything → uniform
        return 0b00 if v == 0 else mask

    # --- Runner ---

    def solve(self, problem):
        for mask, cb in self.program:
            result = problem.move(mask, cb)
            if result:
                return result
                

if __name__ == "__main__":
	for _ in range(0,5): Solver().solve(Problem())