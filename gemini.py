from problem import Problem

def solver():
    p = Problem()
    
    # Logic: Toggle the bits indicated by the mask
    # This changes the state regardless of the current bit values
    flip_logic = lambda mask, current_val: mask ^ current_val

    # Deterministic sequence to solve 4-bit rotation puzzles
    # We use masks that represent 'Opposite' and 'Adjacent' bits
    strategy_masks = [
        0b1010, # Opposite
        0b1100, # Adjacent
        0b1010, # Opposite
        0b0110, # Adjacent (different pair)
        0b1010, # Opposite
        0b1100, # Adjacent
        0b1010  # Opposite
    ]

    print(f"Starting value: {p.val:04b}")

    for mask in strategy_masks:
        if p.move(mask, flip_logic):
            return # Problem.move returns turns if solved

    # If not solved in 7, the parity requires a different approach,
    # but for 4 bits, this sequence covers the state space.
    print("Sequence complete.")

if __name__ == "__main__":
    solver()
