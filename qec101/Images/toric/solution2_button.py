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
    data = cudaq.qvector(18) #first horizontal then vertical
    anc = cudaq.qvector(18)


    for x in range(9): #loops over 9  plaquette stabilizers 
        h(anc[x])
        for i in range(4):  # loops over data qubit index in stabilizer
            x.ctrl(anc[x], data[plaq[4*x+i]])  #
        h(anc[x])

    for x in range(9):#loops over 9 vertex stabilizers 
        for i in range(4):
            x.ctrl( data[vert[4*x+i]],anc[x+9])


    anc0 = mz(anc) # saves round 0 measurements
    reset(anc) # resets only ancilla measurements

    for x in range(9):
        h(anc[x])
        for i in range(4):
            x.ctrl(anc[x], data[plaq[4*x+i]])
        h(anc[x])

    for x in range(9):
        for i in range(4):
            x.ctrl( data[vert[4*x+i]],anc[x+9])



    anc1 = mz(anc)
    reset(anc)

    for x in range(9):
        h(anc[x])
        for i in range(4):
            x.ctrl(anc[x], data[plaq[4*x+i]])
        h(anc[x])

    for x in range(9):
        for i in range(4):
            x.ctrl( data[vert[4*x+i]],anc[x+9])


    anc2 = mz(anc)
    reset(anc)


    for x in range(9):
        h(anc[x])
        for i in range(4):
            x.ctrl(anc[x], data[plaq[4*x+i]])
        h(anc[x])

    for x in range(9):
        for i in range(4):
            x.ctrl( data[vert[4*x+i]],anc[x+9])


    anc3 = mz(anc)
    reset(anc)


    data_qubits=mz(data)


    
cudaq.set_target('stim')

results = cudaq.sample(toric,stabilizers_z, stabilizers_x,shots_count=1)

print(results.get_register_counts("anc0"))
print(results.get_register_counts("anc1"))
print(results.get_register_counts("anc2"))
print(results.get_register_counts("anc3"))
print(results.get_register_counts("data_qubits"))
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
