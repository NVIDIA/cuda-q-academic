import numpy as np
from typing import List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


def top_k_bitstrings(shots, Q: np.ndarray, k: int = 5
                     ) -> List[Tuple[str, float, float]]:
    """
    List the k most-probable bit-strings in `shots` and their QUBO values.

    Returns
    -------
    [(bitstring, probability, qubo_cost), ...]
    """
    # ------------------------------------------------------------------
    # 1) extract a counts-dict {str -> int}
    # ------------------------------------------------------------------
    if isinstance(shots, dict):                        # plain counts dict
        counts_dict = shots
    elif hasattr(shots, "items"):                      # cudaq.SampleResult
        counts_dict = dict(shots.items())
    elif hasattr(shots, "counts"):                     # older naming
        counts_dict = shots.counts
    else:
        raise TypeError("Unrecognised shot container type.")

    total_shots = sum(counts_dict.values())
    if total_shots == 0:
        raise ValueError("No shots in sample result.")

    # ------------------------------------------------------------------
    # 2) sort by frequency and keep top-k
    # ------------------------------------------------------------------
    top = sorted(counts_dict.items(),
                 key=lambda kv: kv[1],
                 reverse=True)[:k]

    # ------------------------------------------------------------------
    # 3) compute QUBO value for every string
    # ------------------------------------------------------------------
    n = Q.shape[0]
    results = []
    for bitstr, cnt in top:
        # bitstr is already a string like '1010'
        x = np.fromiter(bitstr, dtype=int, count=n)
        cost = float(x @ (Q @ x))
        prob = cnt / total_shots
        results.append((bitstr, prob, cost))
        print(f"{bitstr}   prob = {prob:.3f}   QUBO = {cost:.6f}")

    return results

def plot_samples_histogram(sample1, sample2, solutions_data, title="Portfolio Comparison"):
    """
    Plot a histogram comparing two CUDAQ sample objects.
    
    Args:
        sample1: First CUDAQ sample object
        sample2: Second CUDAQ sample object
        solutions_data: List of tuples ((bit0, bit1, ...), objective_value)
        title: Plot title
    """
    # Sort solutions by objective value
    sorted_solutions = sorted(solutions_data, key=lambda x: x[1])
    
    # Create a mapping from bitstring tuples to their string representation
    bitstring_map = {tuple(bits): ''.join(str(b) for b in bits) for bits, _ in sorted_solutions}
    
    # Convert samples to dictionaries of counts
    counts1 = defaultdict(int)
    counts2 = defaultdict(int)
    
    # Extract counts from sample1
    for bitstring, count in sample1.items():
        bitstring_tuple = tuple(int(b) for b in bitstring)
        counts1[bitstring_tuple] = count
        
    # Extract counts from sample2
    for bitstring, count in sample2.items():
        bitstring_tuple = tuple(int(b) for b in bitstring)
        counts2[bitstring_tuple] = count
    
    # Get all unique bitstrings in order of objective value
    all_bitstrings = [bits for bits, _ in sorted_solutions]
    
    # Create x-axis labels with bitstring and objective value
    x_labels = [f"{bitstring_map[bits]}\n(obj: {val:.2f})" for bits, val in sorted_solutions]
    
    # Set up plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Set positions for bars
    x = np.arange(len(all_bitstrings))
    width = 0.35
    
    # Create bars with NVIDIA colors
    nvidia_green = '#76B900'  # NVIDIA green color
    counts1_values = [counts1.get(bits, 0) for bits in all_bitstrings]
    counts2_values = [counts2.get(bits, 0) for bits in all_bitstrings]
    
    # Plot bars with black and NVIDIA green
    bar1 = ax.bar(x - width/2, counts1_values, width, label='Initial State', color='black')
    bar2 = ax.bar(x + width/2, counts2_values, width, label='Final State', color=nvidia_green)
    
    # Find the transition point between good and bad portfolios
    good_portfolios = []
    bad_portfolios = []
    for i, (_, val) in enumerate(sorted_solutions):
        if val < 0:
            good_portfolios.append(i)
        else:
            bad_portfolios.append(i)
    
    # Add annotations for good and bad portfolios
    max_count = max(max(counts1_values or [0]), max(counts2_values or [0]))
    if max_count > 0:
        if good_portfolios:
            mid_good = good_portfolios[len(good_portfolios)//2]
            ax.text(mid_good, max_count * 0.95, "Good Portfolios", 
                ha='center', va='center', fontsize=12, fontweight='bold')
        
        if bad_portfolios:
            mid_bad = bad_portfolios[len(bad_portfolios)//2]
            ax.text(mid_bad, max_count * 0.95, "Bad Portfolios", 
                ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Customize plot
    ax.set_xlabel('Bitstring Configuration (Objective Value)', fontsize=12)
    ax.set_ylabel('Sample Count', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    
    # Improve legend
    ax.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=10)
    
    # Add grid and adjust layout
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    return fig, ax
