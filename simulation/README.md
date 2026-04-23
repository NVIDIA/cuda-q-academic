# Quantum Algorithm Simulation 101

Quantum Algorithm Simulation 101 introduces the main simulator families used throughout CUDA-Q Academic. The lesson focuses on when to use state vector, tensor network, matrix product state, Pauli propagation, and stabilizer simulation, and on the tradeoffs between memory footprint, observable access, contraction order, entanglement structure, and circuit class.

**Pre-requisites:** Learners should be comfortable with Python and Jupyter notebooks and have basic quantum computing familiarity, including qubits, gates, circuits, bra-ket notation, and measurement. Familiarity with expectation values and Pauli operators is helpful.

**Learning Objectives:**
* Build small NumPy and CUDA-Q examples for state vector, tensor network, and matrix product state simulation.
* Compare when state vector, tensor network, Pauli propagation, and stabilizer methods are the right fit.
* Analyze how endianness, contraction order, bond dimension, and branching affect simulator performance.

## Notebooks

* [01_simulation101.ipynb](01_simulation101.ipynb) - core lesson on choosing the right simulator for a quantum algorithm workflow.
* [solutions/01_simulation101_solutions.ipynb](solutions/01_simulation101_solutions.ipynb) - worked reference implementation for every exercise in the student notebook.

These notebooks are designed to run on a GPU-equipped environment with CUDA-Q and `cudaq-qec` available. For local installation instructions, see the [CUDA-Q install guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q). For cloud-based launch options, visit the [CUDA-Q Academic Learning Paths](https://nvidia.github.io/cuda-q-academic/learningpath.html).
