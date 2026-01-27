# reveal_cudaq.py
import ipywidgets as widgets
from IPython.display import display, Markdown
import runpy, tempfile, os

_NV_GREEN = "#76b900"

_CODE_pre = """\
L=3

stabilizers_z = []   # Plaquette stabilizers that flag Z errors
for row in range(L):
  for col in range(L):  
      stabilizers_z.append(L*row + col+L**2)      #left
      stabilizers_z.append(L*row + col )       #top
      stabilizers_z.append((L*row + (col+1)%L)+L**2)  #right
      stabilizers_z.append(L*((row + 1)%L) +col)     #bottom


stabilizers_x = []  # vertex stabilizers that flag X errors
for row in range(L):
  for col in range(L):  
      stabilizers_x.append( (L*row + (col -1 )%L))      #left
      stabilizers_x.append(L*((row-1)%L) + col + L**2)       #top
      stabilizers_x.append(L*row +col)  #right
      stabilizers_x.append(L*row +col + L**2 )     #bottom
"""

# your example as a raw‐string
_CODE = """\
import cudaq 
@cudaq.kernel
def toric(plaq: list[int], vert: list[int]):
    data = cudaq.qvector(18)
    anc = cudaq.qvector(18)


    for x in range(9):
        h(anc[x])
        for i in range(4):
            x.ctrl(anc[x], data[plaq[4*x+i]])
        h(anc[x])

    for x in range(9):
        for i in range(4):
            x.ctrl(data[vert[4*x+i]],anc[x+9])

    
    mz(anc)
    reset(anc)

    #x(data[6],data[7],data[8])    # X1 L 
    #x(data[10],data[13],data[16])  # X2 L 

    #z(data[12],data[13],data[14])  # Z1 L
    #z(data[2],data[5],data[8])   # Z2 L
    
    d = mz(data)


    
cudaq.set_target('stim')

results = cudaq.sample(toric,stabilizers_z, stabilizers_x,shots_count=1000)


def count_summed_bits_at_indices(bit_dict, indices):

    zero_count = 0
    one_count = 0

    for bitstring, count in bit_dict.items():
        # Compute sum of bits at specified indices
        bit_sum = sum(int(bitstring[i]) for i in indices) % 2
        # If bit_sum is 1, increment one_count; else increment zero_count
        if bit_sum == 1:
            one_count += count
        else:
            zero_count += count

    return zero_count, one_count



logical_x1 = [0,1,2]  # L to R horizontal qubits
logical_x2 = [11,14,17] # T to B vertical qubits


logical_z1 = [9,10,11]   # L to R vertical qubits
logical_z2 = [1,4,7]  # T to B horizontal qubits

print("Result of measuring X1:")
print(count_summed_bits_at_indices(results, logical_x1))
print("Result of measuring X2:")
print(count_summed_bits_at_indices(results, logical_x2))

print("Result of measuring Z1:")
print(count_summed_bits_at_indices(results, logical_z1))
print("Result of measuring Z2:")
print(count_summed_bits_at_indices(results, logical_z2))
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
                f.write(_CODE_pre)
                f.write(_CODE)
            try:
                # 3) execute that file as __main__
                runpy.run_path(path, run_name="__main__")
            finally:
                os.remove(path)

    btn.on_click(_on_click)
    return widgets.VBox([btn, out])
