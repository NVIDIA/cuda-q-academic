# CUDA-Q Sample Syllabus

This document is intended to assist faculty in selecting CUDA-Q resources that align with their syllabus 
and topic list for undergraduate or graduate courses in Quantum Information Science or Quantum Computing. 
CUDA-Q provides a variety of practical resources that can be seamlessly incorporated into these courses:

* Jupyter Notebooks: Self-paced modules, available for self hosting or on platforms such as qBraid Lab or 
Google Colab, offer hands-on learning experiences on topics the Quantum Approximate Optimization Algorithm (QAOA).
* Visualization Tools: These tools help students grasp abstract concepts by visualizing quantum circuits and 
Bloch spheres, making the learning process more intuitive.
* Hybrid Programming Examples: Code snippets demonstrate how to develop hybrid quantum-classical applications 
using CUDA-Q’s kernel-based programming model, supporting both Python and C++ for flexible integration.

The CUDA-Q resources are categorized by topic. The list of topics below combines key concepts identified by 
the [Quantum Information Science Learning: Future Pathways](https://qis-learners.research.illinois.edu) workshop, 
competencies from the Quantum Computing and Simulation section of the [European Competence Framework for Quantum Technologies](https://qtedu.eu/european-competence-framework-quantum-technologies) 
report, 
relevant [high performance computing competencies](https://figshare.com/s/4d7e3f73d91ba97c03ed), and topics common in the table of contents of several textbooks on quantum computing. 
This document will be updated with additional resources as they become available.

## CUDA-Q Resources
1. Overview of Quantum Information Science and Quantum Computing<br>
  a. Motivation and vision for accelerating quantum supercomputing 
([blog](https://developer.nvidia.com/blog/an-introduction-to-quantum-accelerated-supercomputing/) and
[video](https://www.youtube.com/watch?v=gevJ5xU_WUA))<br>
  b. Overview of fault tolerant computation and NISQ<br>
  c. Computational Complexity<br>
  d. Quick Start to Quantum Computing (A [full mini-course under development 
  that covers all of 
these topics is in the linked directory](https://github.com/NVIDIA/cuda-q-academic/tree/main/quick-start-to-quantum)  and short code samples that individually address the topics are linked in the bulleted items below)<br>

    * [Quantum states and gates](https://nvidia.github.io/cuda-quantum/latest/using/examples/quantum_operations.html)
    * [Quantum Measurement](https://nvidia.github.io/cuda-quantum/latest/examples/python/measuring_kernels.html)
    * Qubits: [Qubit visualization](https://nvidia.github.io/cuda-quantum/latest/examples/python/visualization.html) on the Bloch sphere<br>
    * Entanglement
    * [Quantum circuits and kernels structure, sampling, and expectation value computation](https://nvidia.github.io/cuda-quantum/latest/using/basics/basics.html)


  
3. Quantum algorithms and applications<br>
  a. [Quantum teleportation](https://nvidia.github.io/cuda-quantum/latest/applications/python/quantum_teleportation.html)<br>
  b. [Deutsch's Algorithm](https://nvidia.github.io/cuda-quantum/latest/applications/python/deutschs_algorithm.html)<br>
  c. [Bernstein-Vazirani](https://nvidia.github.io/cuda-quantum/latest/applications/python/bernstein_vazirani.html)<br>
  d. [Grover’s](https://github.com/NVIDIA/cuda-q-academic/blob/main/qis-examples/grovers.ipynb)<br>
  e. QPE<br>
  f. [QFT](https://nvidia.github.io/cuda-quantum/latest/applications/python/quantum_fourier_transform.html)<br>
  g. [Shor’s Factoring Algorithm](https://nvidia.github.io/cuda-quantum/latest/applications/python/shors.html)<br>
4. Variational hybrid algorithms and applications<br>
  a. [General structure of a variational hybrid algorithm](https://nvidia.github.io/cuda-quantum/latest/applications/python/cost_minimization.html)<br>
  b. [Variational quantum eigensolver](https://nvidia.github.io/cuda-quantum/latest/applications/python/vqe.html)<br>
  c. QAOA for max cut - [code only](https://nvidia.github.io/cuda-quantum/latest/applications/python/qaoa.html) and [course materials with exercises, video
explanations, etc.](https://github.com/NVIDIA/cuda-q-academic/tree/main/qaoa-for-max-cut)<br>
  d. [QAOA for portfolio optimization](https://github.com/NVIDIA/cuda-q-academic/blob/main/quantum-applications-to-finance/03_qchop.ipynb)
  e. Hybrid neural networks [basic code](https://nvidia.github.io/cuda-quantum/latest/applications/python/hybrid_qnns.html)
and application [blog on solar energy application](https://developer.nvidia.com/blog/accelerating-quantum-algorithms-for-solar-energy-prediction-with-nvidia-cuda-q-and-nvidia-cudnn/?ncid=so-link-818523&linkId=100000301600419)<br>
6. Quantum Computation<br>
  a. Classical Simulation of Quantum Algorithms<br>
  b. Executing code on Quantum Computers<br>

    * Quantum Communication
    * Coherence and Types of Noise
    * [Error mitigation](https://nvidia.github.io/cuda-quantum/latest/applications/python/readout_error_mitigation.html) and [error correction](https://github.com/NVIDIA/cuda-q-academic/tree/main/qec101)
    
7. Further topics in Applications and Algorithm Design<br>
  a. Circuit cutting ([introduction to circuit cutting through QAOA max cut example](https://github.com/NVIDIA/cuda-q-academic/tree/main/qaoa-for-max-cut))<br>
  b. GPT-QE [blog](https://developer.nvidia.com/blog/advancing-quantum-algorithm-design-with-gpt/?ncid=so-link-401079&linkId=100000294214594)<br>
  c. Divisive clustering [code](https://nvidia.github.io/cuda-quantum/latest/applications/python/divisive_clustering_coresets.html) and [blog](https://developer.nvidia.com/blog/cuda-q-enabled-resource-reduction-for-quantum-clustering-algorithms/)<br>
  d. Quantum annealing ([applied to portofolio optimization](https://github.com/NVIDIA/cuda-q-academic/blob/main/quantum-applications-to-finance/03_qchop.ipynb))
  e. [Infleqtion's QChop alogrithm](https://github.com/NVIDIA/cuda-q-academic/blob/main/quantum-applications-to-finance/03_qchop.ipynb)
