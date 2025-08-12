# reveal_cudaq.py
import ipywidgets as widgets
from IPython.display import display, Markdown
import runpy, tempfile, os

_NV_GREEN = "#76b900"

# your example as a raw‐string
_CODE = """\
import numpy as np
from itertools import product

# Define the bit-flip probability
p = 0.1

# Define the parity check matrix H
H = np.array([
    [1, 1, 0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1]
])

# Generate all possible length-7 bitstrings
bitstrings = list(product([0, 1], repeat=7))

# Function to compute Hamming weight
def hamming_weight(bitstring):
    return sum(bitstring)

# Compute H * x % 2 for each bitstring
results = []
for bitstring in bitstrings:
    x = np.array(bitstring).reshape(7, 1)
    syndrome = (H @ x) % 2
    syndrome = syndrome.flatten()
    w = hamming_weight(bitstring)
    # Probability of this bitstring given independent flips
    prob = (p**w) * ((1 - p)**(7 - w))
    results.append((bitstring, syndrome, w, prob))

# Sort results based on the syndrome
results.sort(key=lambda x: tuple(x[1]))

# Organize by syndrome
syndrome_dict = {}
for bitstring, syndrome, weight, prob in results:
    syndrome_tuple = tuple(syndrome)
    if syndrome_tuple not in syndrome_dict:
        syndrome_dict[syndrome_tuple] = []
    syndrome_dict[syndrome_tuple].append((bitstring, weight, prob))

# Sort each section by Hamming weight
for syndrome in syndrome_dict:
    syndrome_dict[syndrome].sort(key=lambda x: x[1])

# Print the sorted bitstrings by syndrome, Hamming weight, and probability
for syndrome, entries in syndrome_dict.items():
    print(f"Syndrome: {syndrome}")
    for bitstring, weight, prob in entries:
        print(f"  Bitstring: {bitstring}, Hamming Weight: {weight}, Probability: {prob:.6f}")
    print()
"""

def show_cudaq_solution():
    """
    Returns a Reveal‐Answer widget that displays the CUDA‑Q code
    and then runs it, showing its printed output.
    """
    btn = widgets.Button(
        description="Reveal Answer",
        style={"button_color": _NV_GREEN, "font_weight": "bold"},
        layout=widgets.Layout(width="180px")
    )
    out = widgets.Output()

    def _on_click(_):
        out.clear_output()
        with out:
            # 1) show the source
            display(Markdown("```python\n" + _CODE + "\n```"))
            # 2) write to a temp .py file so inspect.getsource will succeed
            fd, path = tempfile.mkstemp(suffix=".py")
            with os.fdopen(fd, "w") as f:
                f.write(_CODE)
            try:
                # 3) execute that file as __main__
                runpy.run_path(path, run_name="__main__")
            finally:
                os.remove(path)

    btn.on_click(_on_click)
    return widgets.VBox([btn, out])
