# The 4-Bit Rotating Puzzle — Algorithm Documentation

---

## 1. Problem Explanation

The puzzle is a **4-bit rotating state machine**. Specifically:

- A 4-bit integer value (`val`, 0–15) is initialized randomly.
- A solver interacts with it through `move(mask, callback)`.
- Each call to `move` counts as one **turn**.
- The solver wins when `val == 0b0000` or `val == 0b1111` — all bits the same.

### What a turn looks like

1. The solver supplies a **mask** — an integer with exactly 2 bits set (e.g., `0b0101`).
2. The mask selects 2 of the 4 bit positions in `val`.
3. The solver's **callback** is invoked as `callback(mask, val & mask)`. It receives:
   - `mask` — which 2 positions were selected.
   - `val & mask` — the *current* values of those 2 bits.
4. The callback returns any value; the bits at the mask positions in `val` are replaced by the corresponding bits of the return value.
5. **Immediately after** the callback, the value is **left-rotated by a random amount** `r ∈ {0, 1, 2, 3}`. This rotation is invisible to the solver.
6. The win condition is checked. If met, the game ends.

### The rotation mechanic

A left-rotation by `r` moves every bit left by `r` positions (wrapping around):

```
val = 0b1010, r = 1  →  0b0101
val = 0b0011, r = 2  →  0b1100
```

The rotation amount is chosen uniformly at random after *every single turn*, and the solver is never told what it was.

---

## 2. The Core Challenges

### Challenge 1 — Partial Observation

The solver cannot read the full 4-bit state. Through the callback, it sees only the **2 bits at the mask positions**. The other 2 bits are invisible at that moment.

### Challenge 2 — Rotational Anonymity

After each turn, the bits shift by an unknown amount. This means the solver **loses all positional identity**: a bit that was at position 0 may now be at position 1, 2, or 3. There is no way to track individual bits across turns.

### Challenge 3 — No Fixed Worst-Case Bound

Because the rotation is random, an adversarially unlucky sequence of rotations (always placing the critical bit at the one position the solver is not checking) can delay winning indefinitely with positive probability. However, since the rotation is *truly random*, such perpetual avoidance occurs with probability zero, and the algorithm terminates **almost surely** (with probability 1).

---

## 3. First Principles of Reasoning

### Principle 1 — Rotational Equivalence Classes

Since rotation can map any state to any of its rotated versions, individual states are not what matter. What matters is the **equivalence class** of a state under rotation. Two states are equivalent if one can be reached from the other by rotation.

The 16 possible 4-bit states collapse into 6 rotationally distinct classes:

| Class | Representative | Full Orbit | Description |
|-------|---------------|------------|-------------|
| **WIN₀** | `0000` | `{0000}` | All zeros — **WIN** |
| **WINf** | `1111` | `{1111}` | All ones — **WIN** |
| **A** | `0001` | `{0001, 0010, 0100, 1000}` | One 1 (one minority bit) |
| **B** | `0011` | `{0011, 0110, 1100, 1001}` | Two adjacent 1s |
| **C** | `0101` | `{0101, 1010}` | Two opposite 1s |
| **Ac** | `0111` | `{0111, 1110, 1101, 1011}` | Three 1s (one minority 0) |

Class A and Ac are complements of each other (swap all 0s and 1s). Class B is self-complementary (its complement `1100` is also in class B). Class C is self-complementary as well (`1010` ↔ `0101`).

### Principle 2 — The Opposite Pair Has Special Structure

The mask `0b0101` selects bits at positions 0 and 2 — an **opposite pair** in the 4-bit circular ring. This is structurally significant:

- After rotation by 0 or 2 (even), bits 0 and 2 remain at positions 0 and 2 (or swap, which is the same pair).
- After rotation by 1 or 3 (odd), bits 0 and 2 move to positions 1 and 3 — the *other* opposite pair.

This means the opposite mask `0b0101` effectively probes **both opposite pairs** across consecutive turns, making it more informative than an adjacent mask.

### Principle 3 — Callback as Read-and-Set

Unlike the classical "spinning table" puzzle where operations are blind, our callback **reads the current state of the selected bits** and can **set them to any combination**. This is strictly more powerful than a flip-only operation and allows the algorithm to make fully informed decisions for the 2 visible bits.

### Principle 4 — Absorbing Markov Chain

The state transitions form a finite Markov chain where WIN is the single absorbing state. If every non-WIN state has a positive probability of moving closer to WIN, then by the theory of absorbing Markov chains, the algorithm **terminates with probability 1** and has a **finite expected number of turns**.

---

## 4. Algorithm Development — Step by Step

### Step 1 — Choose the Best Mask (Structural Reasoning)

We must pick a mask to use consistently. The possible 2-bit masks from a 4-bit ring are:

- **Adjacent**: `0011`, `0110`, `1100`, `1001` — 4 choices, all equivalent by rotation.
- **Opposite**: `0101`, `1010` — 2 choices, equivalent by rotation.

**Why opposite is better:**

From class C (two opposite 1s, e.g., `0101`), an opposite mask can resolve the state in exactly 1 turn with certainty — regardless of which C rotation we're in:
- `0101` → see (1,1) → set both to 0 → `0000` **WIN**.
- `1010` → see (0,0) → set both to 1 → `1111` **WIN**.

No adjacent mask can achieve guaranteed 1-turn wins from all C states. The opposite mask `0b0101` is chosen.

### Step 2 — Design the Callback (Logical Deduction)

With mask `0b0101`, the callback sees one of 4 observations: `(0,0)`, `(0,1)`, `(1,0)`, or `(1,1)`.

We need a single rule that works across all state classes. Consider what each observation implies:

| Observation | Compatible states |
|-------------|------------------|
| `(0,0)` | A (`0010`, `1000`), C (`1010`) |
| `(0,1)` | A (`0100`), B (`0110`, `1100`), Ac (`1110`) |
| `(1,0)` | A (`0001`), B (`0011`, `1001`), Ac (`1011`) |
| `(1,1)` | C (`0101`), Ac (`0111`, `1101`) |

**Key insight:** When we see `(0,0)`, setting both to 1 either immediately wins (from C: `1010` → `1111`) or produces an Ac state. When we see anything else, setting both to 0 either immediately wins (from A or C) or produces an A or C state (which can win quickly).

This yields the **Two-Response Rule:**

```
if bits == 0:           # See (0,0)
    return mask         # Set both selected bits to 1
else:                   # See (1,0), (0,1), or (1,1)
    return 0            # Set both selected bits to 0
```

**Why this works — the four outcome paths:**

1. `See (0,0) → Set (1,1)`: Either WIN (C → `1111`) or create Ac.
2. `See (1,0) or (0,1) → Set (0,0)`: Either WIN (A → `0000`) or create C (from Ac, e.g., `1110` → `1010`).
3. `See (1,1) → Set (0,0)`: Either WIN (C → `0000`) or create A (from Ac, e.g., `0111` → `0010`).
4. **C is always resolved in exactly 1 turn** — both C states (`0101` and `1010`) hit different observations but both immediately win.

### Step 3 — Full State Transition Table (Exhaustive Verification)

The table below covers all 16 non-WIN states, applying mask `0b0101` with the two-response rule. The "result" is the state **before** the subsequent random rotation.

| State | Bits(0,2) | Observation | Action | New State |
|-------|-----------|-------------|--------|-----------|
| `0001` | 1, 0 | mixed | Set (0,0) | `0000` **WIN** |
| `0010` | 0, 0 | both 0 | Set (1,1) | `0111` (Ac) |
| `0011` | 1, 0 | mixed | Set (0,0) | `0010` (A) |
| `0100` | 0, 1 | mixed | Set (0,0) | `0000` **WIN** |
| `0101` | 1, 1 | both 1 | Set (0,0) | `0000` **WIN** |
| `0110` | 0, 1 | mixed | Set (0,0) | `0010` (A) |
| `0111` | 1, 1 | both 1 | Set (0,0) | `0010` (A) |
| `1000` | 0, 0 | both 0 | Set (1,1) | `1101` (Ac) |
| `1001` | 1, 0 | mixed | Set (0,0) | `1000` (A) |
| `1010` | 0, 0 | both 0 | Set (1,1) | `1111` **WIN** |
| `1011` | 1, 0 | mixed | Set (0,0) | `1010` (C) |
| `1100` | 0, 1 | mixed | Set (0,0) | `1000` (A) |
| `1101` | 1, 1 | both 1 | Set (0,0) | `1000` (A) |
| `1110` | 0, 1 | mixed | Set (0,0) | `1010` (C) |

**Observations from the table:**

- **Class C** (`0101`, `1010`): immediate WIN, always.
- **Class A** (`0001`, `0100`): immediate WIN (minority 1 is at a mask position).
- **Class A** (`0010`, `1000`): transition to Ac (minority 1 is at a non-mask position).
- **Class Ac** (`1110`, `1011`): transition to C → WIN next turn.
- **Class Ac** (`0111`, `1101`): transition to A.
- **Class B** all: transition to A.

### Step 4 — Markov Chain Analysis (Probabilistic Reasoning)

After each turn's action, the random rotation permutes the state uniformly among its 4 rotational variants (or 2 for class C). This defines transition probabilities:

**From class A** (4 rotations equally likely):
- 2 rotations place the minority 1 at position 0 or 2 → immediate WIN (prob = 1/2).
- 2 rotations place the minority 1 at position 1 or 3 → transition to Ac (prob = 1/2).

**From class Ac** (4 rotations equally likely):
- 2 rotations place the minority 0 at position 0 or 2 → transition to C (prob = 1/2).
- 2 rotations place the minority 0 at position 1 or 3 → transition to A (prob = 1/2).

**From class C** (2 rotations):
- Always WIN in 1 turn (prob = 1).

**From class B** (4 rotations):
- Always transitions to A in 1 turn (prob = 1).

The state machine is:

```
B ──(1 turn)──→ A ──(p=1/2)──→ WIN
                │               ↑
               (p=1/2)         (1 turn)
                │               │
                ↓               │
               Ac ──(p=1/2)──→ C
                │
               (p=1/2)
                │
                ↓
                A (cycle)
```

### Step 5 — Expected Turn Count (Mathematical Reasoning)

Let E_A, E_Ac, E_C denote the expected additional turns to WIN from each class.

```
E_C  = 1                                         (always wins in 1 turn)

E_A  = 1 + (1/2)·0 + (1/2)·E_Ac
     = 1 + E_Ac/2

E_Ac = 1 + (1/2)·E_C + (1/2)·E_A
     = 1 + 1/2 + E_A/2
     = 3/2 + E_A/2
```

Substituting:
```
E_A = 1 + (1/2)·(3/2 + E_A/2)
E_A = 1 + 3/4 + E_A/4
(3/4)·E_A = 7/4
E_A = 7/3 ≈ 2.33 turns
E_Ac = 8/3 ≈ 2.67 turns
```

Starting class expected turns:
| Starting Class | Expected Turns to WIN |
|---------------|-----------------------|
| A | ≈ 2.33 |
| Ac | ≈ 2.67 |
| B | ≈ 3.33 (1 turn to A, then E_A) |
| C | 1.00 |
| Any (uniform start) | ≈ 2–3 |

---

## 5. Guarantee of Termination

**Theorem:** The algorithm terminates with probability 1 (almost surely).

**Proof sketch:** The state space {A, Ac, B, C, WIN} is finite. WIN is the unique absorbing state. Every non-WIN state has a positive probability (at least 1/4) of reaching WIN or a strictly "closer" state within a bounded number of turns. By the theory of absorbing Markov chains, the probability of *not* winning after k turns decreases geometrically to 0 as k → ∞. Therefore the algorithm terminates with probability 1.

**Why no hard worst-case bound exists:** The random rotation is the only source of nondeterminism. An adversary controlling the rotation could always place the minority bit at the 2 non-masked positions, cycling the chain between A and Ac indefinitely. Under truly random rotation, this probability of perpetual avoidance is `(1/2)^n → 0`, ensuring almost-sure termination, but not a finite deterministic upper bound in the traditional sense.

---

## 6. Algorithm Summary

```
MASK = 0b0101  (always select bit positions 0 and 2)

callback(mask, bits):
    if bits == 0:
        return mask   # Set both selected bits to 1
    else:
        return 0      # Set both selected bits to 0

Loop:
    call move(MASK, callback)
    if return value > 0: DONE
```

This is a **single-mask, single-rule, stateless algorithm**. The callback requires no history, no external state, and no multi-branch logic. The simplicity follows directly from the structure of the opposite-pair mask and the complementary action rule.
