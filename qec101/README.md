# Quantum Error Correction 101 (QEC 101)
Whether you're a beginner or looking to deepen your understanding, this series will provide you with the skills and motivation to explore the cutting-edge field of quantum error correction.
For those new to quantum error correction, we suggest beginning with the first notebooks that introduces the fundamental concepts. This collection offers you several opportunities to implement and analyze error correction codes, from simple classical ones like the repetition code to more advanced quantum codes such as the Shor and Steane codes, gaining valuable insights into their performance and limitations. Additionally, you'll explore the fascinating process of magic state distillation, which is essential for creating high-fidelity quantum states necessary for fault-tolerant quantum computation, and learn about various applicaitons of AI for QEC. Whether you're a beginner or looking to deepen your understanding, this series will provide you with the skills and motivation to explore the cutting-edge field of quantum error correction.

 ---
## Pre-requisites 
Learners should have familiarity with Jupyter notebooks and programming in Python and CUDA-Q.  It is assumed the reader has some familiarity already with quantum computation and is comfortable with braket notation and the concepts of qubits, quantum circuits, measurement, and circuit sampling. The  CUDA-Q Academic course entitled "[Quick Start to Quantum Computing with CUDA-Q](https://github.com/NVIDIA/cuda-q-academic/tree/main/quick-start-to-quantum)" provide a walkthrough of this prerequisite knowledge if the reader is new to quantum computing and CUDA-Q or needs refreshing.

---
## Learning Objectives

* ***Understand Fundamental Concepts:*** Grasp the basic principles of classical and quantum error correction, including the differences between them and the importance of stabilizers in quantum error correction.
* ***Implement and Analyze Error Correction Codes:*** Explore, implement, and analyze simple classical error correction codes (e.g., repetition code) and advanced quantum error correction codes (e.g., Shor code, Steane code), understanding their performance and limitations.
* ***Simulate Noise:*** Apply noise models to quantum circuit simulation and explore how noisy data can be used to test the effectiveness of QEC protocols.

---
## Notebooks
The Jupyter notebooks in this folder are designed to run in an environment with CUDA-Q and Python.  For instructions on how to install CUDA-Q on your machine, check out this [guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q).  A Dockerfile and requirements.txt are also included in the main directory of the repository to help get you set up.

Otherwise, if you have set up an account in any of the platforms listed below, 
simply log in to the account, then click on the icons below to run the notebooks on the listed platform.   


| Notebook    |qBraid[^1] | CoCalc[^2]  | Google Colab[^3] |
| ----------- | ----------- |  ----------- | ----------- |
|Lab 1 - The Basics of Classical and Quantum Error Correction  |<a href="https://account.qbraid.com/?gitHubUrl=https://github.com/NVIDIA/cuda-q-academic.git&redirectUrl=qec101/01_QEC_Intro.ipynb" target="_parent"><img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" alt="Launch On qBraid" width="150"/></a> | [<img src="https://cocalc.com/_next/static/media/icon.9f1b8851.svg" width=20/> Open in CoCalc](https://cocalc.com/github/NVIDIA/cuda-q-academic/blob/main/qec101/01_QEC_Intro.ipynb)| [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/qec101/01_QEC_Intro.ipynb)|
| Lab 2 - Stabilizers, the Shor code, and the Steane code  |<a href="https://account.qbraid.com/?gitHubUrl=https://github.com/NVIDIA/cuda-q-academic.git&redirectUrl=qec101/02_QEC_Stabilizers.ipynb" target="_parent"><img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" alt="Launch On qBraid" width="150"/></a> |[<img src="https://cocalc.com/_next/static/media/icon.9f1b8851.svg" width=20/> Open in CoCalc](https://cocalc.com/github/NVIDIA/cuda-q-academic/blob/main/qec101/02_QEC_Stabilizers.ipynb) |  [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/qec101/02_QEC_Stabilizers.ipynb)| 
| Lab 3 - Noisy Simulation[^4]  |<a href="https://account.qbraid.com/?gitHubUrl=https://github.com/NVIDIA/cuda-q-academic.git&redirectUrl=qec101/03_QEC_Noisy_Simulation.ipynb" target="_parent"><img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" alt="Launch On qBraid" width="150"/></a> |[<img src="https://cocalc.com/_next/static/media/icon.9f1b8851.svg" width=20/> Open in CoCalc](https://cocalc.com/github/NVIDIA/cuda-q-academic/blob/main/qec101/03_QEC_Noisy_Simulation.ipynb) |  [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/qec101/03_QEC_Noisy_Simulation.ipynb)| 
| Lab 4 - Decoders[^4]  |<a href="https://account.qbraid.com/?gitHubUrl=https://github.com/NVIDIA/cuda-q-academic.git&redirectUrl=qec101/04_QEC_Decoders.ipynb" target="_parent"><img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" alt="Launch On qBraid" width="150"/></a> |[<img src="https://cocalc.com/_next/static/media/icon.9f1b8851.svg" width=20/> Open in CoCalc](https://cocalc.com/github/NVIDIA/cuda-q-academic/blob/main/qec101/04_QEC_Decoders.ipynb) |  [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/qec101/04_QEC_Decoders.ipynb)| 
| Lab 5 - Magic State Distillation (Coming soon!)  |
| Lab 6 - Toric and Surface Codes (Coming soon!)  |
| Lab 7 - QLDPC (Coming soon!)  ||||

[^1]:If using qBraid Lab, use the [Environment Manager](https://docs.qbraid.com/lab/user-guide/environments) to install the CUDA-Q environment and then activate it in your notebook. In qBraid Lab you can switch to a GPU instance using the [Compute Manager](https://docs.qbraid.com/lab/user-guide/compute-manager).
[^2]:After following the link, select the "Edit your own copy" button, and either select or create a project. Use the run icon in the upper toolbar to execute Python cells.
[^3]:You will need to run the command `!pip install cudaq` in a python code block in each notebook to run on Google CoLab.
[^4]:You will need to move the Images > noisy folder to your working environment to run the optional interactive widget.
