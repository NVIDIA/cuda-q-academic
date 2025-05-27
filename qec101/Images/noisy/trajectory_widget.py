import ipywidgets as widgets
from IPython.display import display

# NVIDIA green
_NV_GREEN = "#76b900"

TREE_STYLE = f"""
<style>
.tree-wrapper {{
  width: 100%;        /* full page width */
  overflow: hidden;    /* no scrollbar */
}}
.tree {{
  transform: scale(0.75);       /* shrink to 75% */
  transform-origin: top left;
}}
.tree ul {{ position: relative; padding-top: 20px; white-space: nowrap; }}
.tree li {{
  display: inline-block; vertical-align: top; text-align: center;
  list-style: none; position: relative; padding: 15px 3px 0;
}}
.tree li::before, .tree li::after {{
  content: ''; position: absolute; top: 0; right:50%;
  border-top:1px solid #ccc; width:50%; height:20px;
}}
.tree li::after {{
  left:50%; right:auto; border-left:1px solid #ccc;
}}
.tree li:only-child::before, .tree li:only-child::after {{ display:none; }}
.tree li:first-child::before, .tree li:last-child::after {{ border:none; }}
.tree li:last-child::before {{
  border-right:1px solid #ccc; border-radius:0 5px 0 0;
}}
.tree li:first-child::after {{ border-radius:5px 0 0 0; }}
.tree ul ul::before {{
  content:''; position:absolute; top:0; left:50%;
  border-left:1px solid #ccc; height:20px;
}}
.node {{
  border:1px solid #ccc; background:#f5f5f5;
  padding:8px 12px; border-radius:5px;
  display:inline-block; transition:all 0.3s;
  font-size: 14px;       /* main text bigger */
}}
.node small {{
  display:block;         /* force prob onto its own line */
  margin-top:4px;
  font-size:12px;        /* prob text */
  color: #333;
}}
.active > .node {{
  background:{_NV_GREEN};
  border-color:{_NV_GREEN};
  color:#fff;
}}
</style>
"""

def show_error_tree_widget():
    p_slider = widgets.FloatSlider(
        description="P(error):", min=0.0, max=0.20, step=0.01, value=0.1,
        continuous_update=False
    )
    q1 = widgets.ToggleButtons(description="Qubit 1:", options=[("No Error",0),("Error",1)])
    q2 = widgets.ToggleButtons(description="Qubit 2:", options=[("No Error",0),("Error",1)])
    q3 = widgets.ToggleButtons(description="Qubit 3:", options=[("No Error",0),("Error",1)])
    tree_out = widgets.HTML()

    def _redraw(change=None):
        pp = p_slider.value
        html = TREE_STYLE
        html += "<div class='tree-wrapper'><div class='tree'><ul>"
        for b1 in (0,1):
            a1 = (b1 == q1.value)
            html += f"<li class='{'active' if a1 else ''}'>"
            html += f"<div class='node'>Q1={b1}</div><ul>"
            for b2 in (0,1):
                a2 = a1 and (b2 == q2.value)
                html += f"<li class='{'active' if a2 else ''}'>"
                html += f"<div class='node'>Q2={b2}</div><ul>"
                for b3 in (0,1):
                    a3 = a2 and (b3 == q3.value)
                    n = b1 + b2 + b3
                    k = 3 - n
                    prob = (pp**n) * ((1-pp)**k)
                    leaf_html = (
                        f"{b1}{b2}{b3}"
                        f"<small>P(state) = {prob:.3f}</small>"
                    )
                    html += f"<li class='{'active' if a3 else ''}'>"
                    html += f"<div class='node'>{leaf_html}</div></li>"
                html += "</ul></li>"
            html += "</ul></li>"
        html += "</ul></div></div>"
        tree_out.value = html

    for w in (p_slider, q1, q2, q3):
        w.observe(_redraw, names="value")
    _redraw()

    return widgets.VBox([p_slider, q1, q2, q3, tree_out])
