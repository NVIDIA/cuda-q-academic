# CUDA-Q Academic 


This repository contains Jupyter notebooks and supporting files for [quantum computing](https://www.nvidia.com/en-us/solutions/quantum-computing/) training using CUDA-Q.  These training materials have been developed by NVIDIA Corporation and are provided free of charge. Please see [LICENSE](LICENSE) for license details.

Instructions to install CUDA-Q can be found in the [instructions.md](instructions.md) file. If you do not have a local installation of CUDA-Q running on a GPU, the notebooks can be opened in qBraid Lab, CoCalc, or in Google Colab.  Directions for this are found in the README.md files in the main folder for each set of notebooks. 


# CUDA-Q Educational Resources 
* The [sample syllabus](Sample-Syllabus.md) is intended to assist faculty or students in identifying CUDA-Q resources that align with their quantum information science or quantum computing syllabi or learning path.

* The [Guide to CUDA-Q Backends](Guide-to-cuda-q-backends.ipynb) is a one-stop resource for code snippets and descriptions of the CUDA-Q backend simulator and hardware options for executing CUDA-Q kernels.

# Modules
Currently this repository contains two modules: Quick Start to Quantum Computing with CUDA-Q and QAOA for Max Cut. More folders will be added as material becomes available.

Instructions to install CUDA-Q can be found in the [instructions.md](instructions.md) file. If you do not have a local installation of CUDA-Q running on a GPU, the notebooks can be opened in qbraid or in Google Colab. Simply select the notebook and click on the qbraid icon or the Go to Colab icon at the top of the page. Note that using Google Colab will require additional steps outlined in the notebooks to install CUDA-Q and to view images. 

## Quick Start to Quantum Computing with CUDA-Q
The folder titled `quick-start-to-quantum` contains the Quick Start to Quantum Computing with CUDA-Q module which aims to take a learner from no knowledge of quantum computation to programming a variational algorithm in CUDA-Q. This material, which includes Jupyter notebooks, is organized into labs that build upon one another. 

## QAOA for Max Cut Module
The folder titled `qaoa-for-max-cut` contains the Divide-and-Conquer QAOA for Max Cut module.
The goal of the labs is to apply a divide-and-conquer QAOA algorithm to a large max cut problem using parallel computation. [Lab 0](qaoa-for-max-cut/00_StartHere.ipynb) gives an overview of the learning material and an introduction to working with the Jupyter notebooks in Google CoLaboratory. [Labs 1](qaoa-for-max-cut/01_Max-Cut-with-QAOA.ipynb), [2](qaoa-for-max-cut/02_One_level_divide_and_conquer_QAOA.ipynb), and [3](qaoa-for-max-cut/03_Recursive-divide-and-conquer.ipynb) provide instructional material including solutions to exercises, while [Lab 4](qaoa-for-max-cut/04_Assessment.ipynb) can serve as an open-ended assessment.

Pre-requisites:
* Familiarity with Python with enough comfort to refer to Python package documentation, specifically [NetworkX](https://networkx.org/documentation/stable/tutorial.html), as needed
* Familiarity with variational quantum algorithms (e.g. VQE or QAOA) such as the material covered in the Quick Start to Quantum Computing module.

## Conference Presentations
The conference presentations folder contains tutorial notebooks presented at conferences and workshops.

