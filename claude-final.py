"""
4-BIT ROTATING PUZZLE — DETERMINISTIC SOLVER
═════════════════════════════════════════════

PROBLEM
  A 4-bit value val ∈ [0,15] is initialized randomly.
  Each turn: solver picks a 2-bit mask and a callback.
    1. callback(mask, val & mask) is called — the solver sees 2 bits.
    2. Those 2 bits are replaced with the callback's return value.
    3. val is left-rotated by an unknown amount r ∈ {0,1,2,3}.
    4. WIN if val ∈ {0b0000, 0b1111}.
  WIN is only checked AFTER a move — initial values 0 and 15 must also
  be resolved by the first move.

GUARANTEE
  WIN in ≤ 5 moves for any initial value, against any rotation sequence.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROTATIONAL EQUIVALENCE CLASSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  WIN0 = {0}            all zeros (fixed point of rotation)
  WINf = {15}           all ones  (fixed point of rotation)
  A    = {1,2,4,8}      exactly one 1-bit
  B    = {3,6,9,12}     two adjacent 1-bits
  C    = {5,10}         two opposite 1-bits
  Ac   = {7,11,13,14}   exactly one 0-bit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE FIVE MOVES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Two masks are used:
  M1 = 0b0011  (adjacent bits 0 and 1)
  M2 = 0b0101  (opposite bits 0 and 2)

MOVE 1 — mask M1, callback: always return 0
  Zeros bits 0 and 1 unconditionally.
  Post-callback val ∈ {0, 4, 8, 12}.
  0 is WIN. Worst-case rotation of {4,8,12} spans classes A and B → belief = S1.

MOVE 2 — mask M1, callback: MIRROR (if obs==0: return M1, else return 0)
  S1 belief = {1,2,3,4,6,8,9,12} (no class Ac — filtered out by move 1).
  obs=0b0011 (val=3):     set [0,0] → 0 = WIN.
  obs=0b0001 (vals 1,9):  set [0,0] → WIN(1→0) or A(9→8).
  obs=0b0010 (vals 2,6):  set [0,0] → WIN(2→0) or A(6→4).
  obs=0b0000 (vals 4,8,12): MIRROR sets [1,1] → WIN(12→15) or Ac(4→7, 8→11).
  Worst-case belief after move 2: class A = {1,2,4,8}  or  class Ac = {7,11,13,14}.

MOVE 3 — mask M2, callback: if obs has exactly 1 bit set return 0, else return 1
  Both class A and class Ac are handled by this single rule under M2:

  Class A = {1,2,4,8}:
    obs=0b0001 (val=1): singleton → return 0 → apply(1,M2,0) = 0 = WIN.
    obs=0b0100 (val=4): singleton → return 0 → apply(4,M2,0) = 0 = WIN.
    obs=0b0000 (vals 2,8): non-singleton → return 1 → {3,9} = class B.

  Class Ac = {7,11,13,14}:
    obs=0b0001 (val=11): singleton → return 0 → apply(11,M2,0) = 1010 = C.
    obs=0b0100 (val=14): singleton → return 0 → apply(14,M2,0) = 1010 = C.
    obs=0b0101 (vals 7,13): non-singleton → return 1 → {3,9} = class B.

  If move 3 returned 0 → residual belief is class C.
  If move 3 returned 1 → residual belief is class B.
  The solver KNOWS which it set — no external state needed.

MOVE 4 — mask depends on move 3's return value:
        if move 3 returned 0: mask = M2  (class C case)
        if move 3 returned 1: mask = M1  (class B case)
  callback: SWAP (return mask ^ obs — complement both selected bits)

  Class C under M2 (move 3 returned 0):
    obs=0b0000 (val=10): swap → M2 ^ 0 = 0b0101 → apply(10,M2,5) = 15 = WIN.
    obs=0b0101 (val=5):  swap → M2 ^ M2 = 0b0000 → apply(5,M2,0) = 0 = WIN.
    Both are WIN → move 4 terminates here.

  Class B under M1 (move 3 returned 1):
    obs=0b0000 (val=12): swap → M1^0 = 0b0011 → apply(12,M1,3) = 15 = WIN.
    obs=0b0011 (val=3):  swap → M1^M1= 0b0000 → apply(3,M1,0)  = 0  = WIN.
    obs=0b0001 (val=9):  swap → 0b0010 → apply(9,M1,2) = 1010 = 10 = class C.
    obs=0b0010 (val=6):  swap → 0b0001 → apply(6,M1,1) = 0101 = 5  = class C.
    Residual: class C.

MOVE 5 — mask M2, callback: MIRROR (if obs==0: return M2, else return 0)
  Handles class C = {5, 10}:
    obs=0b0000 (val=10): return M2 → apply(10,M2,5) = 15 = WIN.
    obs=0b0101 (val=5):  return 0  → apply(5,M2,0)  = 0  = WIN.
  Both WIN. Move 5 always terminates.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WORST-CASE BOUNDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  C after move 3  →  WIN at move 4 (4 turns total)
  B after move 3  →  C at move 4  →  WIN at move 5 (5 turns total)
"""


class Solver:
    """
    Deterministic solver for the 4-bit rotating puzzle.
    Executes at most 5 moves. No tables, no imports, no external state.

    The only inter-move state is a single integer (_step3_returned) set
    by move 3's callback and read by move 4 to choose its mask. The solver
    knows this value because it is the value the solver itself wrote.
    """

    M1 = 0b0011   # adjacent pair: bits 0 and 1
    M2 = 0b0101   # opposite pair: bits 0 and 2

    def __init__(self, problem):
        self.problem = problem
        self._step3_returned = None   # set by move 3; read by move 4

    # ── The five callbacks ────────────────────────────────────────────────

    def _cb1(self, mask, obs):
        """Move 1: zero out both selected bits unconditionally."""
        return 0

    def _cb2(self, mask, obs):
        """Move 2: mirror — if both bits are 0, set both to 1; else zero."""
        return mask if obs == 0 else 0

    def _cb3(self, mask, obs):
        """
        Move 3: if the observed bits contain exactly one 1 (singleton),
        zero both; otherwise set bit 0 to 1.
        Singleton obs means the lone minority bit is visible → zero wins or
        redirects to C. Non-singleton means it is hidden → plant an adjacent
        bit to form class B.
        """
        result = 0 if bin(obs).count('1') == 1 else 1
        self._step3_returned = result
        return result

    def _cb4(self, mask, obs):
        """Move 4: swap — complement both selected bits (return mask ^ obs)."""
        return mask ^ obs

    def _cb5(self, mask, obs):
        """Move 5: mirror — if both bits are 0, set both to 1; else zero."""
        return mask if obs == 0 else 0

    # ── Execution ─────────────────────────────────────────────────────────

    def run(self):
        """
        Execute the five moves in sequence, stopping early on WIN.
        Returns the number of moves taken.
        """
        moves = [
            (self.M1, self._cb1),
            (self.M1, self._cb2),
            (self.M2, self._cb3),
            (None,    self._cb4),   # mask determined after move 3
            (self.M2, self._cb5),
        ]

        for i, (mask, cb) in enumerate(moves):
            if i == 3:
                # Move 4 mask: M2 if move 3 returned 0 (class C), else M1 (class B)
                mask = self.M2 if self._step3_returned == 0 else self.M1

            result = self.problem.move(mask, cb)
            if result > 0:
                return result

        raise RuntimeError("No WIN in 5 moves — this should never happen")


# ─────────────────────────────────────────────────────────────────────────────
# EXHAUSTIVE ADVERSARIAL VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def _rot(val, r):
    return ((val << r) | (val >> (4 - r))) & 0xF

def _apply(val, mask, new_bits):
    return (val & ~mask) | (mask & new_bits)

def verify():
    """
    Test all 16 initial values × all 4^5 = 1024 rotation sequences (16 384 paths).
    Models the adversary as choosing each rotation after seeing the post-callback value.
    Prints a summary and returns True iff all paths succeed.
    """
    M1, M2, WIN = 0b0011, 0b0101, (0, 15)

    def cb1(m, o): return 0
    def cb2(m, o): return m if o == 0 else 0
    def cb4(m, o): return m ^ o
    def cb5(m, o): return m if o == 0 else 0

    total, failed, per_val_max = 0, 0, {}

    for iv in range(16):
        wt = 0
        for rots in __import__('itertools').product(range(4), repeat=5):
            total += 1
            val, won, step3_ret = iv, False, None

            for tidx, r in enumerate(rots, 1):
                if   tidx == 1: mask, nb = M1, cb1(M1, val & M1)
                elif tidx == 2: mask, nb = M1, cb2(M1, val & M1)
                elif tidx == 3:
                    mask = M2; obs = val & M2
                    nb = 0 if bin(obs).count('1') == 1 else 1
                    step3_ret = nb
                elif tidx == 4:
                    mask = M2 if step3_ret == 0 else M1
                    nb = cb4(mask, val & mask)
                else:            mask, nb = M2, cb5(M2, val & M2)

                new_val = _apply(val, mask, nb)
                if new_val in WIN:  won = True; wt = max(wt, tidx); break
                rotated = _rot(new_val, r)
                if rotated in WIN:  won = True; wt = max(wt, tidx); break
                val = rotated

            if not won:
                failed += 1

        per_val_max[iv] = wt

    CLASS = {0:'WIN0',15:'WINf',1:'A',2:'A',4:'A',8:'A',
             3:'B',6:'B',9:'B',12:'B',5:'C',10:'C',
             7:'Ac',11:'Ac',13:'Ac',14:'Ac'}
    print("=" * 52)
    print(f"EXHAUSTIVE VERIFICATION  ({total:,} paths)")
    print("=" * 52)
    print(f"  {'val':>3}  {'bits':>4}  {'class':<5}  {'worst':>5}")
    for v in range(16):
        print(f"  {v:3}  {v:04b}  {CLASS[v]:<5}  {per_val_max[v]:>5}")
    print(f"\n  Failed : {failed}")
    print(f"  Max    : {max(per_val_max.values())} turns")
    ok = failed == 0
    print(f"\n  {'✓ GUARANTEE HOLDS' if ok else '✗ GUARANTEE VIOLATED'}")
    return ok


if __name__ == '__main__':
    ok = verify()
    assert ok

    import sys
    sys.path.insert(0, '/mnt/user-data/uploads')
    from problem import Problem

    print("\n" + "=" * 52)
    print("LIVE DEMO")
    print("=" * 52)

    results = []
    for forced in (0, 15):          # edge cases first
        p = Problem(); p.val = forced
        print(f"\n── val={forced:04b} ({forced}) ──")
        results.append(Solver(p).run())

    for _ in range(8):              # random games
        p = Problem()
        print(f"\n── val={p.val:04b} ({p.val}) ──")
        results.append(Solver(p).run())

    print(f"\nTurns: {results}  max={max(results)}  all≤5={all(t<=5 for t in results)}")
