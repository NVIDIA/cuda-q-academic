# CUDA-Q Autoresearch Demos

These demos show agents running iterative CUDA-Q research against fixed
evaluation harnesses. Each topic provides a completed study for inspection and
a clean copy ready for a new run.

| Topic | Description |
| --- | --- |
| [`cudaq_optimizer/`](cudaq_optimizer/) | Let agents select and refine an optimizer for a fixed depth-15 CUDA-Q QAOA workload. |
| [`cudaq_qec_decoder/`](cudaq_qec_decoder/) | Improve a CUDA-Q QLDPC decoder across fixed error-correction datasets. |
| [`cudaq_tensornet/`](cudaq_tensornet/) | Optimize CUDA-Q TensorNet simulator settings for two fixed circuits. |

## QAOA optimizer selection

[`cudaq_optimizer/`](cudaq_optimizer/) asks two researcher roles to propose and
refine classical optimizers for a fixed 15-layer QAOA MaxCut circuit. Each
round has the same starting parameters and a 300-observation budget, so the
study selects the optimizer that reaches the lowest valid circuit energy.

## QEC decoder improvement

[`cudaq_qec_decoder/`](cudaq_qec_decoder/) has an agent iteratively improve a
CUDA-Q QLDPC decoder against fixed error-correction datasets. The harness
records each proposal and measures logical error rate or decoding time without
letting the agent change the benchmark data or scoring rules.

## TensorNet performance tuning

[`cudaq_tensornet/`](cudaq_tensornet/) assigns agents to tune CUDA-Q TensorNet
simulator settings for two fixed quantum circuits. Every round verifies the
expected result and measures runtime, allowing the study to find faster valid
simulator configurations while keeping the circuits unchanged.

Within a topic, choose `completed/` to inspect prior results or
`ready_to_run/` to launch a fresh autoresearch study.
