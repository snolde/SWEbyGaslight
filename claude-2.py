"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          THE 4-BIT ROTATING PUZZLE — DETERMINISTIC SOLVER                  ║
║                                                                              ║
║  Guarantee: WIN in ≤ 5 turns for ANY initial value, against ANY rotation    ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 1 — PROBLEM STATEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A 4-bit integer `val` is initialized to a random value in [0, 15].
The WIN condition — val ∈ {0b0000, 0b1111} — is only tested AFTER a move.
Therefore an initial value of 0 or 15 does NOT count as a win until after
the first move completes.

Each turn the solver calls:   problem.move(mask, callback)

where mask has exactly 2 bits set. The engine then:
  1. Counts the turn.
  2. Calls callback(mask, val & mask) — exposing the 2 masked bits.
  3. Replaces those 2 bits in val with bits from callback's return value.
  4. Left-rotates val by UNKNOWN amount r ∈ {0,1,2,3}.
  5. Checks WIN: if val ∈ {0, 15} → game ends.

Left-rotation by r: every bit i moves to position (i + r) mod 4.
  Example: 0b1010 rotated by 1 → 0b0101.

WIN states {0, 15} are FIXED POINTS of rotation: rot(0,r)=0, rot(15,r)=15.
  This means: if callback produces 0 or 15, WIN is guaranteed regardless
  of what rotation the adversary applies afterwards.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 2 — CHALLENGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Partial observation: the callback sees only 2 of 4 bits.
2. Rotational anonymity: after every turn the bits shift by an unknown
   amount, erasing positional identity between turns.
3. Adversarial rotation: the rotation must be treated as worst-case. A
   "near-zero probability" of failure is not zero. The algorithm must
   guarantee WIN in a BOUNDED number of turns for EVERY rotation sequence.
4. Initial WIN states: val ∈ {0, 15} at init does not count as won.
   The solver must handle them and WIN after the first move.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 3 — FIRST PRINCIPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Principle 1 — Rotational Equivalence Classes
  Because rotation is unknown, what matters is not the exact value of val
  but which ORBIT it belongs to under rotation. The 16 values collapse into
  6 classes:

    WIN0 = {0}           all zeros  (WIN, fixed point of rotation)
    WINf = {15}          all ones   (WIN, fixed point of rotation)
    A    = {1,2,4,8}     exactly one 1-bit
    B    = {3,6,9,12}    two adjacent 1-bits
    C    = {5,10}        two opposite 1-bits
    Ac   = {7,11,13,14}  exactly one 0-bit  (complement of A)

Principle 2 — Belief State Tracking
  Because the rotation is unknown, the solver must track the SET of all
  values consistent with its history: the BELIEF STATE.

  A strategy is correct only if it guarantees WIN from EVERY value in
  the belief state. After a callback produces post-callback set S:
    - Any v ∈ S ∩ {0,15}: WIN guaranteed (rotation-invariant).
    - Any v ∈ S \ {0,15}: adversary rotates it. Next belief =
        { rot(v,r) : v ∈ S\{0,15}, r ∈ {0,1,2,3} }

Principle 3 — Adversarial Minimax
  The rotation is treated as an adversary choosing the worst possible r.
  A strategy is correct iff at every belief state the solver has a move
  that leads to WIN regardless of which r the adversary picks.

Principle 4 — Callback as Informed Read-and-Set
  The callback both READS and WRITES the 2 masked bits, partitioning the
  belief state by observation (val & mask). Two values that produce
  DIFFERENT observations can be handled with different actions in a SINGLE
  turn — no extra turn is needed to distinguish them.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 4 — FIRST-PRINCIPLES DERIVATION OF THE TRANSITION TABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Two masks are used throughout:
    M1 = 0b0011  — selects bits 0 and 1 (adjacent pair)
    M2 = 0b0101  — selects bits 0 and 2 (opposite pair)

Each state is derived below from the structural properties of its class.

──────────────────────────────────────────────────────────────────────────────
S_C — belief = class C = {5=0101, 10=1010}  (two opposite 1-bits)
──────────────────────────────────────────────────────────────────────────────
Mask M2=0101 selects the two opposite positions 0 and 2.

  val=5 =0101: obs = 5  & M2 = 0101  (both masked bits are 1)
  val=10=1010: obs = 10 & M2 = 0000  (both masked bits are 0)

The two values give DIFFERENT observations → one callback handles both:
  obs=0101 → mirror (set [0,0]):  apply(5,  M2, 0b0000) =  0 = WIN0
  obs=0000 → mirror (set [1,1]):  apply(10, M2, 0b0101) = 15 = WINf

Both results ∈ {0,15} = WIN → rotation-invariant → guaranteed in 1 turn.

──────────────────────────────────────────────────────────────────────────────
S_B — belief = class B = {3,6,9,12}  (two adjacent 1-bits)
──────────────────────────────────────────────────────────────────────────────
Mask M1=0011 selects bits 0 and 1.

  val=12=1100: obs=0000  both 1s outside mask → set [1,1]: 12|0b11 = 15=WINf ✓
  val=3 =0011: obs=0011  both 1s are the mask → set [0,0]:  3&~M1  =  0=WIN0 ✓
  val=9 =1001: obs=0001  mixed → swap (set [0,1]): apply(9, M1, 0b0010) = 1010=10=C ✓
  val=6 =0110: obs=0010  mixed → swap (set [1,0]): apply(6, M1, 0b0001) = 0101= 5=C ✓

"Swap" (mirror the observation) converts mixed-B into class C.
Adversary rotation of C stays within C (orbit size 2). → S_B ≤ 2 turns.

──────────────────────────────────────────────────────────────────────────────
S_A — belief = class A = {1,2,4,8}  (single 1-bit)
──────────────────────────────────────────────────────────────────────────────
Mask M2=0101 selects bits 0 and 2.

  val=1=0001: obs=0001  the 1-bit IS visible → set [0,0]: apply(1,M2,0)=0=WIN0 ✓
  val=4=0100: obs=0100  the 1-bit IS visible → set [0,0]: apply(4,M2,0)=0=WIN0 ✓
  val=2=0010: obs=0000  1-bit hidden at pos 1 → cannot zero it
  val=8=1000: obs=0000  1-bit hidden at pos 3 → cannot zero it

For obs=0000: set bit 0 to 1 (introduce a visible 1 adjacent to the hidden 1):
    apply(2, M2, 0b0001) = 0011 = 3  → class B ✓
    apply(8, M2, 0b0001) = 1001 = 9  → class B ✓

Adversary rotation of {3,9} stays within class B. → S_A ≤ 3 turns.

──────────────────────────────────────────────────────────────────────────────
S_Ac — belief = class Ac = {7,11,13,14}  (single 0-bit)
──────────────────────────────────────────────────────────────────────────────
Mask M2=0101 (dual of S_A reasoning — now we hunt the lone 0-bit).

  val=11=1011: obs=0001  0-bit hidden at pos 2 → set [0,0]: apply(11,M2,0)=1010=10=C ✓
  val=14=1110: obs=0100  0-bit hidden at pos 0 → set [0,0]: apply(14,M2,0)=1010=10=C ✓
  val=7 =0111: obs=0101  0-bit hidden at pos 3 → cannot fill it directly
  val=13=1101: obs=0101  0-bit hidden at pos 1 → cannot fill it directly

For obs=0101: set bit 2 to 0 (create an adjacent 0 next to the hidden 0):
    apply(7,  M2, 0b0001) = 0011 = 3  → class B ✓
    apply(13, M2, 0b0001) = 1001 = 9  → class B ✓

→ S_Ac reduces to S_C or S_B in 1 turn. ≤ 3 turns total.

──────────────────────────────────────────────────────────────────────────────
INIT + S1 — belief = ALL 16 values (including 0 and 15)
──────────────────────────────────────────────────────────────────────────────
TURN 1 (INIT): Mask M1=0011. Action: always set bits 0,1 to 0.
  Post-callback: val becomes val & 0b1100 ∈ {0,4,8,12}.
    val=0  →  0=WIN0;  val=15 → 12 (not WIN);  all others → {0,4,8,12}
  0 is WIN; {4,8,12} are not. Worst-case rotation of {4,8,12}:
    orbit(4)∪orbit(8)∪orbit(12) = {1,2,4,8}∪{1,2,4,8}∪{3,6,9,12}
                                 = {1,2,3,4,6,8,9,12} = S1.
  All 4 observations route to S1 (obs=0011 is the only one that includes
  val=3,7,11,15 before the callback; after zeroing, post is still ⊆{0,4,8,12}).

TURN 2 (S1): Mask M1=0011. Belief = {1,2,3,4,6,8,9,12} (no class Ac values).
  obs=0011: val=3 → set [0,0] → 0=WIN0 ✓                  (→ DONE)
  obs=0001: vals {1,9} → set [0,0]:
    1→0=WIN0 ✓;  9→8 → orbit(8)=class A                   (→ S_A)
  obs=0010: vals {2,6} → set [0,0]:
    2→0=WIN0 ✓;  6→4 → orbit(4)=class A                   (→ S_A)
  obs=0000: vals {4,8,12} → 1-bits all outside mask.
    Cannot WIN0 from here (hidden 1s). Fill mask to try for WINf:
    set [1,1]:  4→7=Ac,  8→11=Ac,  12→15=WINf ✓
    orbit(7)∪orbit(11) = class Ac                          (→ S_Ac)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 5 — WORST-CASE TURN BOUNDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  S_C  (class C)   → 1 turn
  S_B  (class B)   → 1 + S_C  = ≤ 2 turns
  S_A  (class A)   → 1 + S_B  = ≤ 3 turns
  S_Ac (class Ac)  → 1 + max(S_C, S_B) = ≤ 3 turns
  S1               → 1 + max(S_A, S_Ac) = ≤ 4 turns
  INIT (all 16)    → 1 + S1   = ≤ 5 turns

  Overall guarantee: WIN in ≤ 5 turns for ANY initial value (0..15),
  against ANY adversarial rotation sequence.
"""

import random
from itertools import product as iproduct


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def rot(val, r):
    """Left-rotate a 4-bit value by r positions."""
    return ((val << r) | (val >> (4 - r))) & 0xF

def apply_mask(val, mask, new_bits):
    """Replace bits at mask positions in val with those of new_bits."""
    return (val & ~mask) | (mask & new_bits)


# ─────────────────────────────────────────────────────────────────────────────
# SOLVER
# ─────────────────────────────────────────────────────────────────────────────

class Solver:
    """
    Deterministic solver for the 4-bit rotating puzzle.

    Guarantees WIN in ≤ 5 turns for ANY initial value (including 0 and 15)
    and ANY rotation sequence, including worst-case adversarial.

    The transition table is derived directly from the logical structure of
    the rotational equivalence classes (Section 4 above). It is NOT a lookup
    table mined from a search — each row follows from an explicit logical
    argument about what the observed bits imply and what action achieves
    a proven reduction in belief-state complexity.
    """

    M1 = 0b0011   # adjacent pair: bits 0 and 1
    M2 = 0b0101   # opposite pair: bits 0 and 2

    # Transition table: (state, obs) → (new_bits, next_state)
    # obs      = val & mask  (what the callback observes)
    # new_bits = value returned by callback (only mask bits matter)
    # next_state = solver state after this move (tracks belief class)
    # 'DONE' = callback guaranteed WIN; no further move needed.
    TRANSITIONS = {
        # INIT: zero bits 0,1 unconditionally → post ∈ {0,4,8,12} → belief → S1
        ('INIT', 0b0000): (0b0000, 'S1'),
        ('INIT', 0b0001): (0b0000, 'S1'),
        ('INIT', 0b0010): (0b0000, 'S1'),
        ('INIT', 0b0011): (0b0000, 'S1'),

        # S1: belief={1,2,3,4,6,8,9,12}
        #   obs=00: vals{4,8,12} → set[1,1] → WIN(12→15) or Ac(4→7,8→11) → S_Ac
        #   obs=01: vals{1,9}    → set[0,0] → WIN(1→0) or A(9→8)          → S_A
        #   obs=10: vals{2,6}    → set[0,0] → WIN(2→0) or A(6→4)          → S_A
        #   obs=11: val{3}       → set[0,0] → WIN(3→0)                     → DONE
        ('S1', 0b0000): (0b0011, 'S_Ac'),
        ('S1', 0b0001): (0b0000, 'S_A'),
        ('S1', 0b0010): (0b0000, 'S_A'),
        ('S1', 0b0011): (0b0000, 'DONE'),

        # S_A: belief=class A={1,2,4,8}, mask M2
        #   obs=0001: val=1, 1-bit visible  → set[0,0] → WIN              → DONE
        #   obs=0100: val=4, 1-bit visible  → set[0,0] → WIN              → DONE
        #   obs=0000: vals{2,8}, 1-bit hidden → set[1,0] → class B {3,9}  → S_B
        ('S_A', 0b0000): (0b0001, 'S_B'),
        ('S_A', 0b0001): (0b0000, 'DONE'),
        ('S_A', 0b0100): (0b0000, 'DONE'),

        # S_Ac: belief=class Ac={7,11,13,14}, mask M2
        #   obs=0001: val=11, 0-bit hidden at pos2 → set[0,0] → 10=C      → S_C
        #   obs=0100: val=14, 0-bit hidden at pos0 → set[0,0] → 10=C      → S_C
        #   obs=0101: vals{7,13}, 0-bit hidden in unmask → set[1,0] → B{3,9} → S_B
        ('S_Ac', 0b0001): (0b0000, 'S_C'),
        ('S_Ac', 0b0100): (0b0000, 'S_C'),
        ('S_Ac', 0b0101): (0b0001, 'S_B'),

        # S_B: belief=class B={3,6,9,12}, mask M1
        #   obs=0000: val=12, both 1s outside → set[1,1] → WIN(15)        → DONE
        #   obs=0001: val=9, mixed → swap → set[0,1] → 10=C               → S_C
        #   obs=0010: val=6, mixed → swap → set[1,0] →  5=C               → S_C
        #   obs=0011: val=3, both 1s inside → set[0,0] → WIN(0)           → DONE
        ('S_B', 0b0000): (0b0011, 'DONE'),
        ('S_B', 0b0001): (0b0010, 'S_C'),
        ('S_B', 0b0010): (0b0001, 'S_C'),
        ('S_B', 0b0011): (0b0000, 'DONE'),

        # S_C: belief=class C={5,10}, mask M2
        #   obs=0000: val=10, both masked=0 → mirror: set[1,1] → WIN(15)  → DONE
        #   obs=0101: val=5,  both masked=1 → mirror: set[0,0] → WIN(0)   → DONE
        ('S_C', 0b0000): (0b0101, 'DONE'),
        ('S_C', 0b0101): (0b0000, 'DONE'),
    }

    STATE_MASK = {
        'INIT': M1, 'S1':   M1,
        'S_A':  M2, 'S_Ac': M2,
        'S_B':  M1, 'S_C':  M2,
    }

    def __init__(self, problem):
        self.problem = problem
        self.state   = 'INIT'

    def _make_callback(self, current_state):
        def callback(mask, obs):
            new_bits, next_state = self.TRANSITIONS[(current_state, obs)]
            self.state = next_state
            return new_bits
        return callback

    def step(self):
        """Execute one move. Returns turn count if solved, else 0."""
        mask     = self.STATE_MASK[self.state]
        callback = self._make_callback(self.state)
        return self.problem.move(mask, callback)

    def run(self, max_turns=5):
        """
        Run the solver to completion.
        Returns the number of turns taken.
        Raises RuntimeError if max_turns exceeded (guaranteed not to happen).
        """
        for _ in range(max_turns):
            if self.state == 'DONE':
                break   # Callback guaranteed WIN on the previous move
            result = self.step()
            if result > 0:
                return result
        raise RuntimeError("Solver exceeded max_turns — this should never happen")


# ─────────────────────────────────────────────────────────────────────────────
# EXHAUSTIVE ADVERSARIAL VERIFIER
# ─────────────────────────────────────────────────────────────────────────────

def verify_exhaustive(max_turns=5):
    """
    Test ALL 16 initial values × ALL 4^max_turns rotation sequences.
    The adversary is modelled as choosing each rotation after seeing the
    post-callback value (worst case).
    Returns True iff every single path results in WIN within max_turns.
    """
    TRANSITIONS = Solver.TRANSITIONS
    STATE_MASK  = Solver.STATE_MASK
    CLASS = {
        0:'WIN0', 15:'WINf',
        1:'A', 2:'A', 4:'A', 8:'A',
        3:'B', 6:'B', 9:'B', 12:'B',
        5:'C', 10:'C',
        7:'Ac', 11:'Ac', 13:'Ac', 14:'Ac',
    }

    print("=" * 60)
    print("EXHAUSTIVE ADVERSARIAL VERIFICATION")
    print(f"16 initial values × 4^{max_turns} = {16 * 4**max_turns:,} paths")
    print("=" * 60)

    failed = 0
    per_val_max = {}

    for initial_val in range(16):
        val_max = 0
        for rotations in iproduct(range(4), repeat=max_turns):
            val, state, won = initial_val, 'INIT', False
            for turn_idx, adversary_r in enumerate(rotations, start=1):
                mask = STATE_MASK[state]
                obs  = val & mask
                new_bits, next_state = TRANSITIONS[(state, obs)]
                new_val = apply_mask(val, mask, new_bits)
                if new_val in (0, 15):
                    won = True; val_max = max(val_max, turn_idx); break
                rotated = rot(new_val, adversary_r)
                if rotated in (0, 15):
                    won = True; val_max = max(val_max, turn_idx); break
                val, state = rotated, next_state
            if not won:
                failed += 1
        per_val_max[initial_val] = val_max

    max_overall = max(per_val_max.values())
    print(f"\n  {'val':>3}  {'binary':>6}  {'class':<5}  {'worst turns':>11}")
    print(f"  {'---':>3}  {'------':>6}  {'-----':<5}  {'-----------':>11}")
    for v in range(16):
        print(f"  {v:3}  {v:06b}  {CLASS[v]:<5}  {per_val_max[v]:>11}")
    print(f"\n  Total paths  : {16 * 4**max_turns:,}")
    print(f"  Failed paths : {failed}")
    print(f"  Max turns    : {max_overall}")
    ok = (failed == 0)
    print(f"\n  {'✓ GUARANTEE VERIFIED' if ok else '✗ GUARANTEE FAILED'}: "
          f"WIN in ≤ {max_overall} turns for all initial values and rotation sequences.")
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ok = verify_exhaustive()
    assert ok

    import sys
    sys.path.insert(0, '/mnt/user-data/uploads')
    from problem import Problem

    print("\n" + "=" * 60)
    print("LIVE DEMO  (edge cases 0 and 15 first, then random games)")
    print("=" * 60)

    results = []
    for forced in (0, 15):
        p = Problem(); p.val = forced
        print(f"\n── Edge case: initial val = {forced:04b} ({forced}) ──")
        results.append(Solver(p).run())

    for i in range(1, 9):
        p = Problem()
        print(f"\n── Game {i}: initial val = {p.val:04b} ({p.val}) ──")
        results.append(Solver(p).run())

    print(f"\n── Summary ──")
    print(f"  Turns  : {results}")
    print(f"  Max    : {max(results)}")
    print(f"  All ≤5 : {all(t <= 5 for t in results)}")
