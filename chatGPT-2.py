from problem import Problem
class Solver:
    def __init__(self):
        # Overlapping cycle covering all 4 bits
        self.masks = [
            0b0011,
            0b0110,
            0b1100,
            0b1001,
        ]
        self.idx = 0

    def or_callback(self, mask, masked_val):
        # If any selected bit is 1 → set both to 1
        return mask if masked_val != 0 else 0

    def solve(self, problem):
        """
        Deterministic solver with finite worst-case bound.
        Converges to 1111 (or immediately succeeds if already 0000).
        """
        while True:
            mask = self.masks[self.idx]
            self.idx = (self.idx + 1) % len(self.masks)

            result = problem.move(mask, self.or_callback)
            if result:
                return result
                

if __name__ == "__main__":
	for _ in range(0,5): Solver().solve(Problem())