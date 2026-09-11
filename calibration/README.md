# Calibration Resources

Resources for exploring superconducting-qubit calibration through interactive visualizations, sample plots, and [NVIDIA Ising Calibration](https://www.nvidia.com/en-us/solutions/quantum-computing/ising/) plot analysis. Hardware access and prior laboratory experience are not required.

## Contents


| File                                                                   | Role                                                                                                                               |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| [Calibration_Resources_Guide.ipynb](Calibration_Resources_Guide.ipynb) | Orientation path through the visualizations, sample plots, and Ising options                                                       |
| [ising_calibration_intro.ipynb](ising_calibration_intro.ipynb)         | Hands-on Ising API notebook: zero-shot analysis and in-context learning comparison                                                 |
| `images/`                                                              | Loose sample PNGs used by widgets and references                                                                                   |
| [images/calibration_images.zip](images/calibration_images.zip)         | Plot pack for the intro notebook — extract to `calibration_images/` beside the notebook                                            |
| `README.md`                                                            | This inventory                                                                                                                     |


## Before you run the intro notebook

1. Install the API client: `pip install openai`
2. Create an NVIDIA API key at [NVIDIA Build](https://build.nvidia.com/) and set `NVIDIA_API_KEY` in the environment before launching Jupyter
3. Extract the plot pack so the folder sits beside the notebook:

```bash
cd calibration
unzip images/calibration_images.zip
# creates ./calibration_images/ next to ising_calibration_intro.ipynb
```

4. If needed, follow the [environment and API-key setup guide](https://nvidia.github.io/cuda-q-academic/interactive_widgets/ising_api_key_setup.html)


## Quick links


| Resource                            | Link                                                                                                              |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Visualization Gallery (Calibration) | [Open →](https://nvidia.github.io/cuda-q-academic/visualization-gallery.html)                                     |
| Learning path card                  | [Calibration track](https://nvidia.github.io/cuda-q-academic/learningpath.html?track=track-calibration)           |
| Ising NIM playground (no API key)   | [build.nvidia.com](https://build.nvidia.com/nvidia/ising-calibration-1-35b-a3b)                                   |
| Environment & API-key setup         | [ising_api_key_setup.html](https://nvidia.github.io/cuda-q-academic/interactive_widgets/ising_api_key_setup.html) |
| Sample plots                        | [QCalEval on Hugging Face](https://huggingface.co/datasets/nvidia/QCalEval)                                       |




## Visualization tools

Widgets follow a typical superconducting-qubit bring-up order. Live items also appear in the [Visualization Gallery](https://nvidia.github.io/cuda-q-academic/visualization-gallery.html).


| #   | Experiment                  | Status        | Visualization                                                                                        |
| --- | --------------------------- | ------------- | ---------------------------------------------------------------------------------------------------- |
| 0   | Time of Flight              | *Coming soon* | —                                                                                                    |
| 1   | Resonator Spectroscopy      | Live          | [Open →](https://nvidia.github.io/cuda-q-academic/interactive_widgets/resonator-spectroscopy.html)   |
| 2   | Resonator Punch Out         | Live          | [Open →](https://nvidia.github.io/cuda-q-academic/interactive_widgets/resonator-punch-out.html)      |
| 3   | Resonator Flux Spectroscopy | *Coming soon* | —                                                                                                    |
| 4   | Qubit Spectroscopy          | Live          | [Open →](https://nvidia.github.io/cuda-q-academic/interactive_widgets/qubit-spectroscopy-intro.html) |
| 5   | Amplitude Rabi              | Live          | [Open →](https://nvidia.github.io/cuda-q-academic/interactive_widgets/rabi-oscillations.html)        |
| 6   | T₁ (Energy Relaxation)      | Live | [Open ](https://nvidia.github.io/cuda-q-academic/interactive_widgets/t1-energy-lifetime.html)                                                                            |
| 7   | Ramsey                      | *Coming soon* | —                                                                                                    |
| 8   | Hahn Echo                   | *Coming soon* | —                                                                                                    |
| 9   | Single-Shot Readout         | *Coming soon* | —                                                                                                    |
| 10  | Randomized Benchmarking     | *Coming soon* | —                                                                                                    |
| 11  | DRAG Pulse Calibration      | Live          | [Open →](https://nvidia.github.io/cuda-q-academic/interactive_widgets/drag-pulse-calibration.html)   |
| 12  | Error Amplification         | *Coming soon* | —                                                                                                    |



## References

1. P. Krantz et al., *A Quantum Engineer's Guide to Superconducting Qubits*, Applied Physics Reviews **6**, 021318 (2019). [arXiv:1904.06560](https://arxiv.org/abs/1904.06560)
2. A. M. Souza et al., *A Tutorial for Characterizing Transmon Qubits*, [arXiv:2606.03815](https://arxiv.org/abs/2606.03815)
3. Qblox, *Hands-on Qubit Calibration* workshop slides — public link TBD
4. [NVIDIA Ising](https://developer.nvidia.com/ising) · [NIM playground](https://build.nvidia.com/nvidia/ising-calibration-1-35b-a3b) · [Solutions overview](https://www.nvidia.com/en-us/solutions/quantum-computing/ising/)
5. [Ising launch blog](https://developer.nvidia.com/blog/nvidia-ising-introduces-ai-powered-workflows-to-build-fault-tolerant-quantum-systems/) · [Ising Calibration 1.5 / ICL blog](https://developer.nvidia.com/blog/nvidia-ising-enables-fully-automated-quantum-computer-calibration-with-enhanced-in-context-learning/)
6. [Environment and API-key setup](https://nvidia.github.io/cuda-q-academic/interactive_widgets/ising_api_key_setup.html)
7. S. Cao et al., *QCalEval*, [arXiv:2604.25884](https://arxiv.org/abs/2604.25884); dataset: [nvidia/QCalEval](https://huggingface.co/datasets/nvidia/QCalEval)
