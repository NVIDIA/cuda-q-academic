# Quantum Information Science Examples
This folder contains example code and explanations of foundational quantum algorithms often appearing in Quantum Information Science courses.  It is intended to complement quantum information science textbooks and courses, rather than being self-contained.

 ---
## Pre-requisites 
Learners should have familiarity with Jupyter notebooks and programming in Python and CUDA-Q.  It is assumed the reader has some familiarity already with quantum computation and is comfortable with braket notation and the concepts of qubits, quantum circuits, measurement, and circuit sampling. The  CUDA-Q Academic course entitled "[Quick Start to Quantum Computing with CUDA-Q](https://github.com/NVIDIA/cuda-q-academic/tree/main/quick-start-to-quantum)" provide a walkthrough of this prerequisite knowledge if the reader is new to quantum computing and CUDA-Q or needs refreshing.


---
## Notebooks
The Jupyter notebooks in this folder are designed to run in an environment with CUDA-Q and Python.  For instructions on how to install CUDA-Q on your machine, check out this [guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q).  A Dockerfile and requirements.txt are also included in the main directory of the repository to help get you set up.

Otherwise, if you have set up an account in any of the platforms listed below, 
simply log in to the account, then click on the icons below to run the notebooks on the listed platform.   


| Notebook    |qBraid[^1] | CoCalc[^2]  | Google Colab[^3] |
| ----------- | ----------- |  ----------- | ----------- |
|Grover's Algorithm  |<a href="https://account.qbraid.com/?gitHubUrl=https://github.com/NVIDIA/cuda-q-academic.git&redirectUrl=qis-examples/grovers.ipynb" target="_parent"><img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" alt="Launch On qBraid" width="150"/></a> | [<img src="https://cocalc.com/_next/static/media/icon.9f1b8851.svg" width=20/> Open in CoCalc](https://cocalc.com/github/NVIDIA/cuda-q-academic/blob/main/qis-examples/grovers.ipynb)| [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/qis-examples/grovers.ipynb)|
| Check back here as new notebooks are added  | | | |

[^1]:If using qBraid Lab, use the [Environment Manager](https://docs.qbraid.com/lab/user-guide/environments) to install the CUDA-Q environment and then activate it in your notebook. In qBraid Lab you can switch to a GPU instance using the [Compute Manager](https://docs.qbraid.com/lab/user-guide/compute-manager).
[^2]:After following the link, select the "Edit your own copy" button, and either select or create a project. Use the run icon in the upper toolbar to execute Python cells.
[^3]:You will need to run the command `!pip install cudaq` in a python code block in each notebook to run on Google CoLab.
