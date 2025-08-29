# Chemistry Simulations
This collection of notebooks explores techniques for calculating molecular ground state energies, a fundamental problem in the field. The notebooks offer a deep dive into implementing and applying two approaches: the ADAPT-VQE algorithm and various Krylov subspace methods.  Additionally techniques will be added in the future.

*Pre-requisites:* Learners should have familiarity with Jupyter notebooks and programming in Python and CUDA-Q. Since these notebooks cover chemistry and materials science simulations, domain knowledge is helpful. It is assumed the reader has some familiarity already with quantum computation and is comfortable with braket notation and the concepts of qubits, quantum circuits, measurement, and circuit sampling. The CUDA-Q Academic course entitled "Quick Start to Quantum Computing with CUDA-Q" provide a walkthrough of this prerequisite CUDA-Q knowledge if the reader is new to quantum computing and CUDA-Q or needs refreshing.

## Notebooks
The Jupyter notebooks in this folder are designed to run on GPUs in an environment with CUDA-Q and Python.  For instructions on how to install CUDA-Q on your machine, check out this [guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q).  A Dockerfile and requirements.txt are also included in the main directory of the repository to help get you set up.

Otherwise, if you have set up an account in Google CoLab, 
simply log in to the account, then click on the icons below to run the notebooks on the listed platform.   

| Notebook      | Google Colab |
| -----------  | ----------- |
|Lab 1 - ADAPT VQE  | [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/chemistry-simulations/adapt_vqe.ipynb)|
| Lab 2 - Krylov Methods  | Coming soon!  | |||


