# QAOA and ADAPT-QAOA Exercise Files

The workshop handout provides the exercises; this README only identifies the
files included in this folder.

| File | Purpose |
| --- | --- |
| `workshop_graphs.py` | Defines the weighted MaxCut graphs shared by the QAOA examples and selects the graph to run. |
| `qaoa_maxcut.py` | Implements and runs MaxCut QAOA directly with CUDA-Q kernels and SciPy optimization. |
| `qaoa_maxcut_solvers.py` | Solves the same MaxCut problem through the higher-level CUDA-Q Solvers QAOA API. |
| `adapt_qaoa.py` | Implements ADAPT-QAOA for the selected weighted MaxCut graph. |
| `tests/test_qaoa_maxcut.py` | Checks the custom QAOA state and compares its optimized result with CUDA-Q Solvers. |
