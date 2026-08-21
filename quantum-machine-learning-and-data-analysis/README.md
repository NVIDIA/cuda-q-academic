# Quantum Machine Learning and Data Analysis

This collection of notebooks explores quantum and hybrid approaches to machine learning and data analysis with CUDA-Q. The lessons progress from hybrid quantum neural networks to performance and scaling techniques, quantum-kernel classification, and quantum graph inference with PageRank. Throughout, they emphasize comparison with classical baselines, resource requirements, and careful interpretation of results.

Notebooks 1 and 2 form a recommended sequence: the second extends the hybrid quantum neural-network workflow developed in the first. The support-vector-machine and PageRank notebooks can be completed independently once learners have the stated prerequisites.

*Pre-requisites:* Learners should have familiarity with Jupyter notebooks, Python, NumPy, and basic quantum-computing concepts such as qubits, gates, measurement, and probability amplitudes. Familiarity with vectors, matrices, and basic linear algebra is helpful. The [Quick Start to Quantum Computing](https://github.com/NVIDIA/cuda-q-academic/tree/main/quick-start-to-quantum) learning path provides the necessary CUDA-Q and quantum-computing foundations. Individual notebook introductions list any additional prerequisites and GPU requirements.

## Notebooks

The Jupyter notebooks in this folder are designed to run in an environment with CUDA-Q and Python. Some notebooks require a GPU; check the callout near the beginning of each notebook. For instructions on how to install CUDA-Q on your machine, see the [CUDA-Q quick start guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q).

If you have a Google Colab account, sign in and use the links below to open the notebooks.

| Notebook | Google Colab |
| ----------- | ----------- |
| An Introduction to Hybrid Quantum Neural Networks | [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/quantum-machine-learning-and-data-analysis/01_an_introduction_to_hybrid_quantum_neural_networks.ipynb) |
| Advanced Hybrid Quantum Neural Networks | [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/quantum-machine-learning-and-data-analysis/02_advanced_hqnns.ipynb) |
| Quantum Support Vector Machines | [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/quantum-machine-learning-and-data-analysis/03_quantum_svm.ipynb) |
| Quantum PageRank | [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/quantum-machine-learning-and-data-analysis/04_quantum_pagerank.ipynb) |

Explore the [Learning Pathways page](https://nvidia.github.io/cuda-q-academic/learningpath.html) for additional cloud-based options to run these notebooks.
