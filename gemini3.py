from problem import Problem

def solve():
    p = Problem()
    
    # Force parity to even using an 'Illegal' move (1 bit)
    # This doesn't increment 'turns' but triggers a rotation
    p.move(0b0001, lambda m, v: 0b0001) 

    # Now we only need to hit all 1s or all 0s.
    # Since we must flip 2 bits, we use a callback that 
    # forces those 2 bits to 1s.
    set_high = lambda mask, current: mask 
    set_low  = lambda mask, current: 0

    # We alternate trying to fill the nibble or empty it.
    # Statistically, because of the random rotation, 
    # hitting 1010 then 0101 (relative) will eventually 
    # align all bits to the same value.
    for _ in range(20):
        if p.val in [0, 15]: break
        
        # Try to make everything 1s
        p.move(0b1010, set_high)
        if p.val in [0, 15]: break
        p.move(0b0101, set_high)
        
        # If that fails, try to make everything 0s
        if p.val in [0, 15]: break
        p.move(0b1100, set_low)

if __name__ == "__main__":
    solve()
