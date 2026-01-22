# Notebooks for the 2026 MIT Winter School
These notebooks are intended for attendees of the 2026 MIT Winter School. While they can be run on their own, significant context will be provided during the lecture portions of the workshop. 

## Notebooks
The Jupyter notebooks in this folder are designed to run in an environment with CUDA-Q and Python.  For instructions on how to install CUDA-Q on your machine, check out this [guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q).  A Dockerfile and requirements.txt are also included in the main directory of the repository to help get you set up.

For system uniformity during the Winter School we suggest that you run the notebooks using Google CoLab via the links below. 


| Notebook    | Google Colab[^1] |
| ----------- | ----------- |
| Lab 1 - CUDA-Q Quick Start | [![](https://colab.research.google.com/assets/colab-badge.svg)](https://github.com/NVIDIA/cuda-q-academic/blob/2026-workshops/MIT-Winter-School/01_CUDAQ-Q_Quick_Start.ipynb)|
| Lab 2 - Intros to Quantum Walks  |  [![](https://colab.research.google.com/assets/colab-badge.svg)](https://github.com/NVIDIA/cuda-q-academic/blob/2026-workshops/MIT-Winter-School/02_Intro_to_Quantum_Walks.ipynb)| 
| Lab 3 - Quantum Walks pt. 2 |  [![](https://colab.research.google.com/assets/colab-badge.svg)](https://github.com/NVIDIA/cuda-q-academic/blob/2026-workshops/MIT-Winter-School/03_Quantum_Walks_pt2.ipynb)| 
| Lab 4 - QAOA for Max Cut |  [![](https://colab.research.google.com/assets/colab-badge.svg)](https://github.com/NVIDIA/cuda-q-academic/blob/2026-workshops/MIT-Winter-School/04_QAOA_for_Max_Cut.ipynb)| 

[^1]:You will need to run the command `!pip install cudaq` in a python code block in each notebook to run on Google CoLab.