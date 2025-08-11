# Quantum Dynamics 101

Welcome to the Quantum Dynamics 101 series! 

Quantum dynamics describes how complex quantum systems evolve in time and interact with their surroundings. Simulating quantum dynamics is extremely challenging yet crucial for understanding and predicting the fundamental properties of materials. This is particularly important in the development of quantum processing units (QPUs), where quantum dynamics simulations help developers understand the intricacies of their hardware and improve its performance.

Quantum dynamics simulations differ from the more common circuit simulations, which model the evolution of qubits under the application of discrete quantum logical gates. Circuit simulations offer a simplified view, often idealizing qubit interactions and overlooking real-world noise and other factors. In contrast, quantum dynamics simulations provide a comprehensive representation of how quantum systems evolve over time, revealing fundamental limits on the speed and accuracy of quantum processes.

To draw a classical analogy: the logic of a classical computer can be modeled using binary logic gates (AND, OR, XOR) applied to transistors, abstractly represented as 0s and 1s. However, to design faster and higher-performing transistors, electrical engineers run complex models that fully simulate the device physics, including fluctuations in voltage, capacitance, and current. Similarly, designing better qubits and QPUs requires analog dynamics simulations that fully capture the physics of physical qubits, akin to modeling the physics of transistors in classical computing.

Designed for advanced users with a solid background in quantum mechanics and familiarity with Python programming, this series of notebooks guides you through GPU-accelerated quantum dynamics simulations. We start with the Jaynes-Cummings Hamiltonian to introduce the fundamental concepts and then progress to the Landau-Zener model to explore time-dependent Hamiltonian terms and custom operators.

## Learning Objectives

* ***Simulate Complex Quantum Dynamics:*** Explore, implement, and analyze the time evolution of quantum systems using advanced models such as the Jaynes-Cummings and Landau-Zener models with GPU-accelerated computations.
* ***Model Time-Dependent Interactions:*** Learn to implement time-dependent Hamiltonian terms and custom operators to simulate dynamic quantum interactions.

## Notebooks
The Jupyter notebooks in this folder are designed to run on GPUs in an environment with CUDA-Q and Python.  For instructions on how to install CUDA-Q on your machine, check out this [guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q).  A Dockerfile and requirements.txt are also included in the main directory of the repository to help get you set up.

Otherwise, if you have set up an account in Google CoLab, 
simply log in to the account, then click on the icons below to run the notebooks on the listed platform.   

| Notebook      | Google Colab |
| -----------  | ----------- |
|Lab 1 - Jaynes-Cummings Hamiltonian  | [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/dynamics101/01_Jaynes_Cummings.ipynb)|
| Lab 2 - Time Dependent Hamiltonians  |[![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/dynamics101/02_Time_Dependent.ipynb)  | |||

