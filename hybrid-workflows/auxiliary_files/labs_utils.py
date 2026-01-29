import numpy as np

def compute_topology_overlaps(G2, G4):
    """
    Computes the topological invariants I_22, I_24, I_44 based on set overlaps.
    I_alpha_beta counts how many sets share IDENTICAL elements.
    """
    # Helper to count identical sets
    def count_matches(list_a, list_b):
        matches = 0
        # Convert to sorted tuples to ensure order doesn't affect equality
        set_b = set(tuple(sorted(x)) for x in list_b)
        for item in list_a:
            if tuple(sorted(item)) in set_b:
                matches += 1
        return matches

    # For standard LABS/Ising chains, these overlaps are often 0 or specific integers
    # We implement the general counting logic here.
    I_22 = count_matches(G2, G2) # Self overlap is just len(G2)
    I_44 = count_matches(G4, G4) # Self overlap is just len(G4)
    I_24 = 0 # 2-body set vs 4-body set overlap usually 0 as sizes differ
    
    return {'22': I_22, '44': I_44, '24': I_24}

from math import sin, cos, pi

def compute_theta(t, dt, total_time, N, G2, G4):
    """
    Computes theta(t) using the analytical solutions for Gamma1 and Gamma2.
    """
    
    # ---  Better Schedule (Trigonometric) ---
    # lambda(t) = sin^2(pi * t / 2T)
    # lambda_dot(t) = (pi / 2T) * sin(pi * t / T)
    
    if total_time == 0:
        return 0.0

    # Argument for the trig functions
    arg = (pi * t) / (2.0 * total_time)
    
    lam = sin(arg)**2
    # Derivative: (pi/2T) * sin(2 * arg) -> sin(pi * t / T)
    lam_dot = (pi / (2.0 * total_time)) * sin((pi * t) / total_time)
    
    
    # ---  Calculate Gamma Terms (LABS assumptions: h^x=1, h^b=0) ---
    # For G2 (size 2): S_x = 2
    # For G4 (size 4): S_x = 4
    
    # Gamma 1 (Eq 16)
    # Gamma1 = 16 * Sum_G2(S_x) + 64 * Sum_G4(S_x)
    term_g1_2 = 16 * len(G2) * 2
    term_g1_4 = 64 * len(G4) * 4
    Gamma1 = term_g1_2 + term_g1_4
    
    # Gamma 2 (Eq 17)
    # G2 term: Sum (lambda^2 * S_x)
    # S_x = 2
    sum_G2 = len(G2) * (lam**2 * 2)
    
    # G4 term: 4 * Sum (4*lambda^2 * S_x + (1-lambda)^2 * 8)
    # S_x = 4
    # Inner = 16*lam^2 + 8*(1-lam)^2
    sum_G4 = 4 * len(G4) * (16 * (lam**2) + 8 * ((1 - lam)**2))
    
    # Topology part
    I_vals = compute_topology_overlaps(G2, G4)
    term_topology = 4 * (lam**2) * (4 * I_vals['24'] + I_vals['22']) + 64 * (lam**2) * I_vals['44']
    
    # Combine Gamma 2
    Gamma2 = -256 * (term_topology + sum_G2 + sum_G4)

    # ---  Alpha & Theta ---
    if abs(Gamma2) < 1e-12:
        alpha = 0.0
    else:
        alpha = - Gamma1 / Gamma2
        
    return dt * alpha * lam_dot
