# CUDA-Q Academic 


This repository contains Jupyter notebooks and supporting files for [quantum computing](https://www.nvidia.com/en-us/solutions/quantum-computing/) training using CUDA-Q.  These training materials have been developed by NVIDIA Corporation and are provided free of charge. Please see [LICENSE](LICENSE) for license details.

Instructions to install CUDA-Q can be found in the [instructions.md](instructions.md) file. If you do not have a local installation of CUDA-Q running on a GPU, the notebooks can be opened in qBraid Lab, CoCalc, or in Google Colab.  Directions for this are found in the README.md files in the main folder for each set of notebooks. 


# Educational Resources and Modules
* The [sample syllabus](Sample-Syllabus.md) is intended to assist faculty or students in identifying CUDA-Q resources that align with their quantum information science or quantum computing syllabi or learning path.

* The [Guide to CUDA-Q Backends](Guide-to-cuda-q-backends.ipynb) is a one-stop resource for code snippets and descriptions of the CUDA-Q backend simulator and hardware options for executing CUDA-Q kernels.

* This repository contents are detailed below. To get started, we recommend beginning with [Quick Start to Quantum Computing with CUDA-Q](https://github.com/NVIDIA/cuda-q-academic/tree/main/quick-start-to-quantum) to grasp the fundamentals of CUDA-Q and quantum computing. Once you have the basics, you can proceed with the remaining three modules in any order. This repository is actively being developed, so be sure to check back regularly for new modules and notebooks.

---
## Quick Start to Quantum Computing with CUDA-Q
The Quick Start to Quantum Computing with CUDA-Q module aims to take a learner from no knowledge of quantum computation to programming a variational algorithm in CUDA-Q. This material, which includes Jupyter notebooks, is organized into labs that build upon one another. 

**Pre-requisites:** Learners should have familiarity with Jupyter notebooks and programming in Python.  Additionally, pre-requisite knowledge includes complex numbers, linear algebra, and statistics. In particular, we assume experience computing and understanding of arithmetic of complex numbers, probabilities, expectation values, vectors, dot products, and matrix multiplication. Knowledge of eigenvalues and eigenvectors will be helpful, but not necessarily a requirement.   

---
## Quantum Information Science Examples
[This folder](qis-examples) contains example code and explanations of foundational quantum algorithms often appearing in Quantum Information Science courses.  It is intended to complement quantum information science textbooks and courses, rather than being self-contained.

**Pre-requisites:** 
* Familiarity with Python with enough comfort to refer to Python package documentation, specifically [NetworkX](https://networkx.org/documentation/stable/tutorial.html), as needed
* Completion of the [Quick Start to Quantum Computing with CUDA-Q](https://github.com/NVIDIA/cuda-q-academic/tree/main/quick-start-to-quantum)

---
## QAOA for Max Cut Module
The Divide-and-Conquer QAOA for Max Cut module takes a learner from the implementation of QAOA to solve a small max problem
to an application of a divide-and-conquer QAOA algorithm to a large max cut problem using parallel computation. [Lab 0](qaoa-for-max-cut/00_StartHere.ipynb) gives an overview of the learning material and an introduction to working with the Jupyter notebooks. [Labs 1](qaoa-for-max-cut/01_Max-Cut-with-QAOA.ipynb), [2](qaoa-for-max-cut/02_One_level_divide_and_conquer_QAOA.ipynb), and [3](qaoa-for-max-cut/03_Recursive-divide-and-conquer.ipynb) provide instructional material including solutions to exercises, while [Lab 4](qaoa-for-max-cut/04_Assessment.ipynb) can serve as an open-ended assessment.

**Prerequisites:**
* Familiarity with Python with enough comfort to refer to Python package documentation, specifically [NetworkX](https://networkx.org/documentation/stable/tutorial.html), as needed
* Completion of the [Quick Start to Quantum Computing with CUDA-Q](https://github.com/NVIDIA/cuda-q-academic/tree/main/quick-start-to-quantum) course or equivalent familiarity with variational quantum algorithms (e.g. VQE or QAOA). 

---
## Quantum Applications for Finance
[This series of tutorials](https://github.com/NVIDIA/cuda-q-academic/tree/main/quantum-applications-to-finance) explores the intersection of quantum computing and finance through hands-on notebooks using CUDA-Q. You will learn the basics of quantum walks and their differences from classical random walks, apply quantum walks to model financial data, and discover how quantum computing can optimize investment portfolios. By implementing quantum algorithms with CUDA-Q, you will gain insights into financial modeling challenges and explore hybrid quantum-classical algorithms that can be applied to a wide range of other fields.

**Pre-requisites:** Learners should have familiarity with Jupyter notebooks and programming in Python and CUDA-Q. It is assumed the reader has some familiarity already with quantum computation and is comfortable with braket notation and the concepts of qubits, quantum circuits, measurement, and circuit sampling. The CUDA-Q Academic course entitled "[Quick Start to Quantum Computing with CUDA-Q](https://github.com/NVIDIA/cuda-q-academic/tree/main/quick-start-to-quantum)" provide a walkthrough of this prerequisite knowledge if the reader is new to quantum computing and CUDA-Q or needs refreshing.

---
## Quantum Error Correction 101 
Whether you're a beginner or looking to deepen your understanding, [this series](https://github.com/NVIDIA/cuda-q-academic/tree/main/qec101) will provide you with the skills and motivation to explore the cutting-edge field of quantum error correction.

**Pre-requisites:** 
Learners should have familiarity with Jupyter notebooks and programming in Python and CUDA-Q.  It is assumed the reader has some familiarity already with quantum computation and is comfortable with braket notation and the concepts of qubits, quantum circuits, measurement, and circuit sampling. The  CUDA-Q Academic course entitled "[Quick Start to Quantum Computing with CUDA-Q](https://github.com/NVIDIA/cuda-q-academic/tree/main/quick-start-to-quantum)" provide a walkthrough of this prerequisite knowledge if the reader is new to quantum computing and CUDA-Q or needs refreshing.
