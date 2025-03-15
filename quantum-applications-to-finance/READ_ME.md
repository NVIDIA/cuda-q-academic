# Quantum Applications to Finance

**What the Quantum Applications to Finance is:** These notebooks provide a quick and practical introduction to the basic quantum concepts sufficient to program and interpret variational algorithms. Additionally, through the interactive coding exercises, readers will learn the basics of the CUDA-Q platform.

**What the Quick Start to Quantum Computing is not:** These notebooks do not claim to provide an exhaustive introduction to quantum information science.  We make several unspoken assumptions and simplifications to give the reader, who may be unfamiliar with quantum mechanics, a general sense of quantum computing so that they can begin to explore variational algorithms. Readers interested in a more thorough introduction to quantum information science are encouraged to read one of several texts on the subject for instance [Introduction to Classical and Quantum Computing](https://www.thomaswong.net/introduction-to-classical-and-quantum-computing-1e4p.pdf), [Quantum Computer Science](http://mermin.lassp.cornell.edu/qcomp/CS483.html), [Introduction to Quantum Information, Computation, and Communication](https://girvin.sites.yale.edu/sites/default/files/files/_Girvin_Introduction_to_Quantum_2024_04_21_v45.pdf) or [Introduction to Quantum Information Science](https://qubit.guide), or watch online lectures such as [this series](https://www.youtube.com/playlist?list=PLkespgaZN4gmu0nWNmfMflVRqw0VPkCGH).

** Pre-requisites:** Learners should have familiarity with Jupyter notebooks and programming in Python and CUDA-Q. It is assumed the reader has some familiarity already with quantum computation and is comfortable with braket notation and the concepts of qubits, quantum circuits, measurement, and circuit sampling. The CUDA-Q Academic course entitled "[Quick Start to Quantum Computing with CUDA-Q](https://github.com/NVIDIA/cuda-q-academic/tree/main/quick-start-to-quantum)" provide a walkthrough of this prerequisite knowledge if the reader is new to quantum computing and CUDA-Q or needs refreshing.


## Notebooks
The Jupyter notebooks in this folder are designed to run in an environment with CUDA-Q with Python.  For instructions on how to install CUDA-Q on your machine, check out this [guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q).  A Dockerfile and requirements.txt are also included in the main directory of the repository to help get you set up.

Otherwise, if you have set up an account in any of the platforms listed below, 
simply click on the icons below to run the notebooks on the listed platform.   



| Notebook    |qBraid[^1] | CoCalc[^2]  | Google Colab[^3] |
| ----------- | ----------- |  ----------- | ----------- |
|Quantum Walks for Finance Part 1 |<a href="https://account.qbraid.com/?gitHubUrl=https://github.com/NVIDIA/cuda-q-academic.git&redirectUrl=quantum-applications-to-finance/01_quantum_walks.ipynb" target="_parent"><img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" alt="Launch On qBraid" width="150"/></a> | [<img src="https://cocalc.com/_next/static/media/icon.9f1b8851.svg" width=20/> Open in CoCalc](https://cocalc.com/github/NVIDIA/cuda-q-academic/blob/main/quantum-applications-to-finance/01_quantum_walks.ipynb)| [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/quantum-applications-to-finance/01_quantum_walks.ipynb)|
| Quantum Walks for Finance Part 2 |<a href="https://account.qbraid.com/?gitHubUrl=https://github.com/NVIDIA/cuda-q-academic.git&redirectUrl=quantum-applications-to-finance/02_quantum_walks.ipynb" target="_parent"><img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" alt="Launch On qBraid" width="150"/></a> | [<img src="https://cocalc.com/_next/static/media/icon.9f1b8851.svg" width=20/> Open in CoCalc](https://cocalc.com/github/NVIDIA/cuda-q-academic/blob/main/quantum-applications-to-finance/02_quantum_walks.ipynb)| [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/quantum-applications-to-finance/02_quantum_walks.ipynb)|
| Portfolio Optimization (Coming Soon!)  | | | |
[^1]:If using qBraid Lab, use the [Environment Manager](https://docs.qbraid.com/lab/user-guide/environments) to install the CUDA-Q environment and then activate it in your notebook. In qBraid Lab you can switch to a GPU instance using the [Compute Manager](https://docs.qbraid.com/lab/user-guide/compute-manager).
[^2]:After following the link, select the "Edit your own copy" button, and either select or create a project. Use the run icon in the upper toolbar to execute Python cells.
[^3]:You will need to uncomment out the `pip install cudaq` code in each notebook to run on Google CoLab.readme
