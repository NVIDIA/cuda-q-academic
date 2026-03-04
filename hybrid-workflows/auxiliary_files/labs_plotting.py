import matplotlib.pyplot as plt
import numpy as np

def plot_energy_distributions(results_1, results_2=None, labels=("Experiment 1", "Experiment 2"), n_val=0):
    """
    Plots histograms of final energy distributions.
    
    Args:
        results_1 (array-like): List of energy values from first experiment.
        results_2 (array-like, optional): List of energy values from second experiment.
        labels (tuple): Labels for the legend.
        n_val (int): Sequence length (for title).
    """
    plt.figure(figsize=(10, 6))
    
    # Determine common bin edges for consistent alignment
    all_data = results_1
    if results_2 is not None:
        all_data = np.concatenate([results_1, results_2])
        
    # Calculate 15 bins based on the full range of data
    bins = np.histogram_bin_edges(all_data, bins=15)
    
    # Plot first set
    plt.hist(results_1, bins=bins, alpha=0.6, label=labels[0], color='blue', edgecolor='black')
    
    # Plot second set if provided
    if results_2 is not None:
        plt.hist(results_2, bins=bins, alpha=0.6, label=labels[1], color='green', edgecolor='black')
    
    plt.title(f"LABS Memetic Optimization Results (N={n_val})\nFinal Population Cost Distribution")
    plt.xlabel("Energy Cost (Lower is Better)")
    plt.ylabel("Frequency in Population")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()