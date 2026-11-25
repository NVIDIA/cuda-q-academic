# pip install cudaq
import cudaq


@cudaq.kernel
def all_colorings():
    # one qubit per vertex v0-v6: 0 = green, 1 = white
    vertices = cudaq.qvector(7)
    # equal superposition of all 2^7 = 128 colorings
    h(vertices)


print(cudaq.sample(all_colorings, shots_count=1))  # one Measure click: one coloring

n, shots = 7, 10000
counts = cudaq.sample(all_colorings, shots_count=shots)
print("Different colorings seen:", len(counts), "of", 2**n)

probs = [counts.probability(bits) for bits in counts]
print(f"Sampled probability per coloring: {min(probs):.4f} to {max(probs):.4f}")
print(f"Ideal (equal superposition): 1/2^{n} = {1 / 2**n:.4f}")
