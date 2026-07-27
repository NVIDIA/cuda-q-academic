# CUDA-Q Kernels and GPU Simulators

This exercise introduces CUDA-Q kernels through two guided GHZ activities and
two complete GPU simulator examples.

## Prerequisites

Run these files from this folder in a Python environment with CUDA-Q installed.
The `nvidia`, `tensornet`, and `tensornet-mps` targets require a compatible
NVIDIA GPU and driver.

## Files

| File | Purpose |
| --- | --- |
| `run_ghz_template.py` | Intentionally incomplete kernel exercise covering typed returns, mid-circuit measurement, and reset. |
| `run_ghz_solution.py` | Completed solution for the mid-circuit kernel exercise. |
| `template_ghz_kernel.py` | Intentionally incomplete GHZ construction and sampling exercise. |
| `solution_ghz_kernel.py` | Completed GHZ construction, drawing, sampling, and noise example. |
| `mps_observe.py` | Complete state-vector versus MPS expectation-value comparison. |
| `tensor_network_observe.py` | Complete TensorNet expectation-value example with contraction-path settings. |

The two files with `template` in their names contain syntax-level placeholders
and are not expected to run until you complete them.

## Suggested workflow

1. Complete `template_ghz_kernel.py`, then compare it with
   `solution_ghz_kernel.py`.
2. Complete `run_ghz_template.py`, then compare it with
   `run_ghz_solution.py`.
3. Run the complete simulator examples:

   ```bash
   python mps_observe.py
   python tensor_network_observe.py
   ```

The simulator examples may take longer than the small GHZ exercises and require
GPU memory appropriate for their configured circuit sizes.
