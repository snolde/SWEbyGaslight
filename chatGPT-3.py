from problem import Problem
class Solver:
    def __init__(self):
        # Two inequivalent masks under rotation
        self.masks = [0b0011, 0b0101]
        self.idx = 0

    def or_callback(self, mask, masked_val):
        return mask if masked_val != 0 else 0

    def solve(self, problem):
        while True:
            mask = self.masks[self.idx]
            self.idx ^= 1  # alternate

            result = problem.move(mask, self.or_callback)
            if result:
                return result
                

if __name__ == "__main__":
	for _ in range(0,5): Solver().solve(Problem())