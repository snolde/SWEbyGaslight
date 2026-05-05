from problem import Problem

class Solver:
    def __init__(self):
        # All 2-bit masks (choose any 2 positions out of 4)
        self.masks = [
            0b0011,  # bits 0,1
            0b0101,  # bits 0,2
            0b1001,  # bits 0,3
            0b0110,  # bits 1,2
            0b1010,  # bits 1,3
            0b1100   # bits 2,3
        ]
        self.idx = 0

    def or_callback(self, mask, masked_val):
        """
        Set both selected bits to OR of the two bits.
        If any bit is 1 → both become 1.
        """
        if masked_val != 0:
            return mask  # set both bits to 1
        return 0        # keep both 0

    def solve(self, problem):
        """
        Deterministically solves the problem in finite moves.
        """
        while True:
            mask = self.masks[self.idx]
            self.idx = (self.idx + 1) % len(self.masks)

            result = problem.move(mask, self.or_callback)
            if result:
                return result
                

if __name__ == "__main__":
	for _ in range(0,5): Solver().solve(Problem())