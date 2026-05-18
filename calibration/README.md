# Calibration

**Instructor resource.** A classroom-ready introduction to [NVIDIA's Ising Calibration NIM](https://www.nvidia.com/en-us/solutions/quantum-computing/ising/) — an open vision-language model purpose-built for analyzing quantum hardware calibration plots, benchmarked on superconducting qubits and neutral atoms. No setup, no API key; the playground runs in the browser.

→ Launch the [Ising Calibration NIM playground](https://build.nvidia.com/nvidia/ising-calibration-1-35b-a3b)

→ Sample plots: [QCalEval dataset on Hugging Face](https://huggingface.co/datasets/nvidia/QCalEval)

---

## What students can do

Upload any calibration experiment plot — from your own lab, a simulation run, or the QCalEval dataset — and ask the model to analyze it. The model returns structured responses across six question types:

* Technical description of the experiment
* Experimental conclusion
* Experimental significance
* Fit quality assessment
* Parameter extraction
* Experiment success classification

Students can ask for all six at once or target specific ones.

---

## Using this in class

A few ways to weave the playground into a course:

* **First-pass plot reader.** A starting point for interpreting an unfamiliar Rabi, Ramsey, T1, T2, or randomized benchmarking trace.
* **Second opinion.** A check on a student's own analysis of their lab data.
* **Reasoning exemplar.** A way to expose what structured calibration reasoning looks like across different experiment types — useful even when students disagree with the model.

The playground requires no environment setup, so it slots into a single lecture, a lab section, or a homework prompt without any deployment overhead.

## Notebooks

Hands-on tutorial notebooks for the Calibration track are in development. They will walk through using the Ising Calibration NIM end-to-end alongside CUDA-Q simulated calibration experiments. Today the folder contains a single `00_StartHere.ipynb` landing notebook that points back to this README.
