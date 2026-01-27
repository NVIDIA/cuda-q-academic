# reveal_cudaq.py
import ipywidgets as widgets
from IPython.display import display, Markdown
import runpy, tempfile, os

_NV_GREEN = "#76b900"

# your example as a raw‐string
_CODE = """\
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



print("plaq")
for x in range(L**2):
    print(stabilizers_z[4*x], stabilizers_z[4*x+1],stabilizers_z[4*x+2],stabilizers_z[4*x+3])

print("vertex")
for x in range(L**2):
    print(stabilizers_x[4*x], stabilizers_x[4*x+1],stabilizers_x[4*x+2],stabilizers_x[4*x+3])
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
