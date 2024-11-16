# CUDA-Q Academic 


This repository contains Jupyter notebooks and supporting files for [quantum computing](https://www.nvidia.com/en-us/solutions/quantum-computing/) training using CUDA-Q.  These training materials have been developed by NVIDIA Corporation and are provided free of charge. Please see [LICENSE](LICENSE) for license details.

Instructions to install CUDA-Q can be found in the [instructions.md](instructions.md) file. If you do not have a local installation of CUDA-Q running on a GPU, the notebooks can be opened in qBraid Lab or in Google Colab. Simply  click on the Launch on qBraid icon below or navigate to the notebook in github and select the Go to Colab icon at the top of the page.  Note that using Google Colab will require additional steps outlined in the notebooks to install CUDA-Q. 

[<img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" width="150">](https://account.qbraid.com?gitHubUrl=https://github.com/NVIDIA/cuda-q-academic.git)
If using qBraid Lab, use the [Environment Manager](https://docs.qbraid.com/lab/user-guide/environments) to install the CUDA-Q environment and then activate it in your notebook. In qBraid Lab you can switch to a GPU instance using the [Compute Manager](https://docs.qbraid.com/lab/user-guide/compute-manager).

# CUDA-Q Educational Resources 
[This document]() is intended to assist faculty or students in identifying CUDA-Q resources that align with their quantum information science or quantum computing syllabi or learning path.

# Modules
Currently this repository contains two modules: Quick Start to Quantum Computing with CUDA-Q and QAOA for Max Cut. More folders will be added as material becomes available.

Instructions to install CUDA-Q can be found in the [instructions.md](instructions.md) file. If you do not have a local installation of CUDA-Q running on a GPU, the notebooks can be opened in qbraid or in Google Colab. Simply select the notebook and click on the qbraid icon or the Go to Colab icon at the top of the page. Note that using Google Colab will require additional steps outlined in the notebooks to install CUDA-Q and to view images. 

## Quick Start to Quantum Computing with CUDA-Q
The folder titled `quick-start-to-quantum` contains the Quick Start to Quantum Computing with CUDA-Q module which aims to take a learner from no knowledge of quantum computation to programming a variational algorithm in CUDA-Q. This material, which includes Jupyter notebooks, is organized into labs that build upon one another. 

## QAOA for Max Cut Module
The folder titled `qaoa-for-max-cut` contains the Divide-and-Conquer QAOA for Max Cut module.

This material, which includes Jupyter notebooks and Python scripts, is organized into labs that build upon one another. The goal of the labs is to apply a divide-and-conquer QAOA algorithm to a large max cut problem using parallel computation. [Lab 0](qaoa-for-max-cut/00_StartHere.ipynb) gives an overview of the learning material and an introduction to working with the Jupyter notebooks in Google CoLaboratory. [Labs 1](qaoa-for-max-cut/01_Max-Cut-with-QAOA.ipynb), [2](qaoa-for-max-cut/02_One_level_divide_and_conquer_QAOA.ipynb), and [3](qaoa-for-max-cut/03_Recursive-divide-and-conquer.ipynb) provide instructional material including solutions to exercises, while [Lab 4](qaoa-for-max-cut/04_Assessment.ipynb) can serve as an open-ended assessment.

The Max Cut problem is an optimization problem defined as: *Given a graph G, find the maximum cut of G*, where the maximum cut (max cut) of a graph is defined to be a partitioning of the vertices into two disjoint sets so that the number of edges between the two partitions is maximized. The Max Cut problem is a [NP-hard problem](https://en.wikipedia.org/wiki/NP-hardness), and there is a rich body of research to develop classical and quantum algorithms to solve and/or approximate the max cut for large subclasses of graphs. Some of these algorithms fall under the divide-and-conquer paradigm. Divide and conquer breaks a large problem into smaller problems which are simple enough to be solved directly.  Additionally, this paradigm lends itself to parallel computation since the smaller problems can often be solved independently. Recently, the divide-and-conquer paradigm has been applied to the Quantum Approximation Optimization Algorithm (QAOA) for max cut ([arXiv:2205.11762v1](https://arxiv.org/abs/2205.11762), [arxiv.2101.07813v1](https://arxiv.org/abs/2101.07813), [arxiv:2304.03037v1](https://arxiv.org/abs/2304.03037), and [arxiv:2009.06726](https://arxiv.org/abs/2009.06726)). In this tutorial, we will introduce this algorithm and implement parallel computation with CUDA-Q.
 
This tutorial begins in [Lab 1](qaoa-for-max-cut/01_Max-Cut-with-QAOA.ipynb) with a demonstration of solving the Max Cut problem for a small graph with QAOA. To set the groundwork for the remaining labs, Lab 1 ends with a preview of the divide-and-conquer paradigm. In [Lab 2](qaoa-for-max-cut/02_One_level_divide_and_conquer_QAOA.ipynb), we walk through one level of the divide-and-conquer algorithm, and we follow that up in [Lab 3](qaoa-for-max-cut/03_Recursive-divide-and-conquer.ipynb) with the recursive implementation for much larger and denser graphs. Additionally in Labs 2 and 3, we experiment with running quantum circuits in parallel on GPUs. Finally, learners can take the assessment in [Lab 4](qaoa-for-max-cut/04_Assessment.ipynb) in which they are challenged to approximate the weighted max cut problem. 


The learning objectives of this tutorial are:
* Execute the QAOA algorithm to find approximate max cuts of a given graph using CUDA-Q
* Understand the limitations of the QAOA algorithm for solving max cut in the NISQ era 
* Apply QAOA to find an approximate solution to Quadratic Unconstrained Binary Optimization problems
* Make various adjustments to the QAOA algorithm to improve results
* Simulate quantum circuits in parallel on multiple GPUs to speed up overall run time using CUDA-Q

Pre-requisites:
* Familiarity with Python with enough comfort to refer to Python package documentation, specifically [NetworkX](https://networkx.org/documentation/stable/tutorial.html), as needed
* Familiarity with variational quantum algorithms (e.g. VQE or QAOA) such as the material covered in the Introduction to Quantum Computing module.

