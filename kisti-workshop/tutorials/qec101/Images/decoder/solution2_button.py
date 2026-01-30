# reveal_solution.py
import ipywidgets as widgets
from IPython.display import display, Markdown

_NV_GREEN = "#76b900"

# 1) The student’s answer‐code (display only – not run)


_ANSWER_TEXT_1 = """\
**Answer:**  
Below is the code to generate the training data.  Note, you need to take one shot at a time as you need the individual syndromes to map to the data qubit measurements which would be obfuscated if you sampled an ensemble. 
"""

_CODE_SNIPPET_1 = """\
nsamples = 10000
syndromes = []
data_qubits = []
logical_flips =[]

for x in range(nsamples):
    results = cudaq.sample(steane_code, noise_model=noise, shots_count=1)
    ancilla = [int(x) for x in np.array(results.get_register_counts('ancilla'))[0]]
    data = [int(x) for x in np.array(results.get_register_counts('data'))[0]]
    syndromes.append(ancilla)
    parity = (data[0] + data[1] + data[4]) %2
    logical_flips.append(parity)
"""


def show_cudaq_solution():
    """
    Returns a widget with a green 'Reveal Answer' button.
    On click it displays the code snippet and then the explanatory text.
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
            display(Markdown(_ANSWER_TEXT_1))
            display(Markdown(f"```python\n{_CODE_SNIPPET_1}\n```"))



    btn.on_click(_on_click)
    return widgets.VBox([btn, out])
