import mpmath

def calculate_pi_to_precision(precision: int) -> str:
    """Calculates Pi and returns the value as a string."""
    if precision == 0:
        return "3"
        
    # Set mpmath context precision (needs padding for intermediate steps)
    mpmath.mp.dps = precision + 50 
    
    # In a real solution, the Chudnovsky algorithm code would go here.
    # For a placeholder, use mpmath's built-in constant:
    pi_val = mpmath.pi 

    total_digits = precision + 1

    # Log the raw mpmath string conversion output
    raw_mpmath_str = mpmath.nstr(pi_val, n=total_digits)
    print(f"[PI_ALGO LOG] Precision {precision}: mpmath.nstr raw output length: {len(raw_mpmath_str)}")
    print(f"[PI_ALGO LOG] mpmath.nstr raw output (first 10 digits): {raw_mpmath_str[:12]}...")
    
    # Format the string to the exact required precision (e.g., 3.1415...)
    return str(raw_mpmath_str)