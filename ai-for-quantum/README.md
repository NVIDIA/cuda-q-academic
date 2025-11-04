# AI for Quantum

Welcome to the AI for Quantum series!

Running quantum applications on a physical QPU is incredibly complex. The device needs to be calibrated, quantum circuits need to be efficiently compiled to run on each device, and errors need to be identified and corrected so the results of the algorithms are reliable. As devices scale, each of these tasks (and many more detailed in the review entitled ["Artificial Intelligence for Quantum Computing"](https://arxiv.org/abs/2411.09131)) become extremely complicated and potential bottlenecks for useful quantum computing. The fact that AI is scalable, fast, and capable of handling the multi-dimensional data associated with quantum computing makes it a powerful tool for overcoming these challenges. 

This series will cover use cases where AI can be used within quantum workflows and provide a greater appreciation for yet another reason why AI supercomputing needs to be tightly coupled to QPUs.

Users are not expected to have significant AI experience and will primarily treat the AI models as black box, or the required knowledge will be presented in the notebooks. Instead, the lessons will focus on where AI fits in the workflow, how the data is prepared as model input, and how the output can be used within the context of the CUDA-Q platform. 

For example, the first notebook guides learners through using a pretrained diffusion model to compile unitary matrices as quantum circuits. This allows for the flexibility to compile the same algorithm on QPUs with different qubit modalities and associated constraints.

## Learning Objectives
* ***Understand specific bottlenecks in quantum workflows:*** Learn why AI supercomputing is a crucial tool for running quantum computers at scale.
* ***Appreciate how AI can be used within quantum workflows:*** Learn how to use AI models to solve key challenges within quantum workflows.
* ***Hands-on experience inserting AI models within quantum workflows:*** Learn how to prepare quantum data for input.

## Notebooks
The Jupyter notebooks in this folder are designed to run on GPUs in an environment with CUDA-Q and Python.  For instructions on how to install CUDA-Q on your machine, check out this [guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q).  A Dockerfile and requirements.txt are also included in the main directory of the repository to help get you set up.

Otherwise, if you have set up an account in Google CoLab, 
simply log in to the account, then click on the icons below to run the notebooks on the listed platform.   

| Notebook      | Google Colab |
| -----------  | ----------- |
|Lab 1 - Compiling Unitaries with Diffusion Models | [![](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NVIDIA/cuda-q-academic/blob/main/ai-for-quantum/01_compiling_unitaries_using_diffusion_models.ipynb)|
