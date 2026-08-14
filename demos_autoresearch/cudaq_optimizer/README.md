# CUDA-Q QAOA Optimizer Autoresearch

This topic contains two self-contained versions of an autoresearch study in
which agents choose and refine the classical optimizer for a fixed CUDA-Q
QAOA workload.

- [`completed/`](completed/) preserves all 20 optimizer-selection rounds, the
  winning implementation, ledgers, logs, traces, findings, and visualizations.
- [`ready_to_run/`](ready_to_run/) is a fresh copy of the fixed benchmark and
  baseline optimizer with no prior study results.

The workload fixes the weighted six-node workshop graph, a 15-layer QAOA
circuit with 30 parameters, and a budget of 300 counted `cudaq.observe` calls
per round. Enter the variant you want and read its `README.md` and
authoritative `AGENTS.md` before running it. Evaluations require CUDA-Q and an
NVIDIA GPU.
