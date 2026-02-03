import numpy as np

def calculate_energy(sequence):
    """
    Calculates the Energy (E) of a LABS sequence.
    E is the sum of squares of aperiodic autocorrelations for all non-zero lags.
    
    Args:
        sequence (np.array): A binary sequence of 1s and -1s.
    
    Returns:
        float: The energy value (lower is better).
    """
    N = len(sequence)
    
    # Faster vectorized approach using np.correlate
    # mode='full' gives correlations from lag -(N-1) to (N-1)
    corr = np.correlate(sequence, sequence, mode='full')
    
    # The center index (lag 0) is at N-1. 
    # We want lags 1 to N-1, which are indices N to 2N-2.
    sidelobes = corr[N:] 
    
    return np.sum(sidelobes**2)

def Flip(s, i):
    """Flips the bit at index i of sequence s."""
    s_new = s.copy()
    s_new[i] *= -1
    return s_new

def tabu_local_search(s0):
    """
    Algorithm 2: TabuSearch
    Performs a Tabu Search for local improvement on a starting sequence.
    
    Input: starting sequence s0 (np.array)
    Output: locally improved sequence s_best, s_best_energy
    
    We assume the existence of a utility function 'calculate_energy(s)' 
    to compute E(s)
    """
    N = len(s0)
    
    # 1. Initialize variables
    s_best = s0.copy()  # ~s in the paper
    p = s0.copy()       # Current sequence p
    s_best_energy = calculate_energy(s_best)
    
    # 2. Initialize TabuList
    # TabuList[i] stores the iteration 't' until which index 'i' is forbidden.
    TabuList = np.zeros(N, dtype=int)
    
    # 3. Determine number of iterations M
    # M ∈ [N/2, 3N/2].
    N_over_2 = N // 2
    M_range = N - 1  # Range is from N/2 to 3N/2, which is N wide.
    # To get a random int in [N/2, 3N/2], we can do N/2 + random_int[0, N]
    # np.random.randint(low, high) is [low, high-1]. We need +1 for inclusive range.
    M = np.random.randint(0, N + 1) + N_over_2
    
    # 4. Loop for t = 1 to M
    for t in range(1, M + 1):
        
        # 5. Choose index i* with minimum energy among { i | TabuList[i] < t }
        
        # Candidate set: indices that are NOT tabu at time t
        non_tabu_indices = np.where(TabuList < t)[0]
        
        if len(non_tabu_indices) == 0:
            # If all moves are tabu, break the search
            break 
            
        best_candidate_energy = np.inf
        i_star = -1
        
        # Evaluate all non-tabu neighbors
        for i in non_tabu_indices:
            # Generate the candidate sequence p_candidate by flipping bit i in the current p
            p_candidate = Flip(p, i) 
            E_candidate = calculate_energy(p_candidate)
            
            # Aspiration Criterion: If the move leads to a new global best, 
            # it should be chosen even if it is tabu.
            # However, the algorithm does not explicitly list an aspiration criterion.
            # Sticking strictly to line 5: Choose index i* with minimum energy among { i | TabuList[i] < t }
            
            if E_candidate < best_candidate_energy:
                best_candidate_energy = E_candidate
                i_star = i
                
        # The best non-tabu neighbor (p_star) is now identified by i_star and best_candidate_energy
        
        # 6. Update current sequence p
        p = Flip(p, i_star)
        E_p = best_candidate_energy # E(p) is already calculated
        
        # 7. Update TabuList for the chosen index i*
        theta_min = int(M / 10)
        theta_max = int(M / 50)
        
        # If theta_min < theta_max, we might have an issue with integer division.
        # Assuming theta_min should be the smaller bound (M/50) and theta_max the larger (M/10).
        # Adjusting interpretation for standard range: [M/50, M/10]
        if theta_min > theta_max:
             theta_min, theta_max = theta_max, theta_min
        
        # Ensure minimum tabu tenure is at least 1
        if theta_min == 0:
            theta_min = 1
        if theta_max <= theta_min:
            theta_max = theta_min + 1

        # Tabu tenure: random int(theta_min, theta_max)
        # np.random.randint(low, high) is [low, high-1]. We use [theta_min, theta_max + 1].
        tenure = np.random.randint(theta_min, theta_max + 1)
        
        TabuList[i_star] = t + tenure
        
        # 8. Check for Global Best Update
        if E_p < s_best_energy:
            # 9. ~s <- p
            s_best = p.copy()
            s_best_energy = E_p

    # 10. return ~s
    return s_best, s_best_energy

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

def compute_theta(t, dt, total_time, N):
    """
    Computes theta(t) using the analytical solutions for Gamma1 and Gamma2.
    """
    
    # --- 1. Better Schedule (Trigonometric) ---
    # lambda(t) = sin^2(pi * t / 2T)
    # lambda_dot(t) = (pi / 2T) * sin(pi * t / T)
    
    if total_time == 0:
        return 0.0

    # Argument for the trig functions
    arg = (pi * t) / (2.0 * total_time)
    
    lam = sin(arg)**2
    # Derivative: (pi/2T) * sin(2 * arg) -> sin(pi * t / T)
    lam_dot = (pi / (2.0 * total_time)) * sin((pi * t) / total_time)
    
    # --- 2. Get Interactions and counts ---
    G2, G4 = get_interactions(N)
    
    # --- 3. Calculate Gamma Terms (LABS assumptions: h^x=1, h^b=0) ---
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

    # --- 4. Alpha & Theta ---
    if abs(Gamma2) < 1e-12:
        alpha = 0.0
    else:
        alpha = - Gamma1 / Gamma2
        
    return dt * alpha * lam_dot

def get_interactions(N):
    """
    Generates the interaction sets G2 and G4 based on the loop limits in Eq. 15.
    Returns standard 0-based indices as lists of lists of ints.
    
    Args:
        N (int): Sequence length.
        
    Returns:
        G2: List of lists containing two body term indices
        G4: List of lists containing four body term indices
    """
    
    G2 = []
    # Eq 15: prod_{i=0}^{N-3} prod_{k=0}^{floor((N-i)/2)-1}
    for i in range(1, N-2 +1):
        limit_k = (N - i) // 2
        for k in range(1, limit_k+1):
            # Term: indices [i, i+k]
            G2.append([i-1, i + k-1]) #subtract 1 for zero index

    G4 = []
    # Eq 15: prod_{i=1}^{N-3} prod_{t=1}^{floor((N-i-1)/2)} prod_{k=t+1}^{N-i-t}
    for i in range(1, N - 3 + 1):
        limit_t = (N - i - 1) // 2
        for t in range(1, limit_t +1):
            limit_k_loop = N - i - t
            for k in range(t + 1, limit_k_loop +1):
                # Term: indices [i, i+t, i+k, i+k+t]
                G4.append([i-1, i + t-1, i + k-1, i + k + t-1]) #subtract 1 for zero indexing of qubits

#TODO END
                
    return G2, G4