# CUDA-Q Hands-on Lab

<img align="right" width="150"
src="https://developer.nvidia.com/sites/default/files/akamai/nvidia-cuquantum-icon.svg"
/>

Explore CUDA-Q through hands-on labs covering quantum computing fundamentals, quantum chemistry simulations, quantum error correction, and AI-powered quantum circuit synthesis. These tutorials have been tailored for the [KISTI Hybrid Quantum-Classical Applications Bootcamp](https://www.openhackathons.org/s/siteevent/a0CUP00003APKEp2AP/se000448), taking you from foundational CUDA-Q programming to advanced hybrid quantum-classical computing applications.

## Agenda

Navigate to the **`tutorials`** folder which contains 4 labs:

### 1. Getting started with CUDA-Q
* `quick-start-to-quantum/00_cudaq_basics.ipynb`
* `quick-start-to-quantum/01_quick_start_to_quantum.ipynb`
* `quick-start-to-quantum/02_quick_start_to_quantum.ipynb`

### 2. Advanced Applications with CUDA-Q - Quantum Chemistry
* `chemistry-simulations/vqe_basics.ipynb`
* `chemistry-simulations/adapt_vqe.ipynb`

### 3. Advanced Applications with CUDA-Q - Quantum Error Correction
* `qec101/01_QEC_Intro.ipynb`
* `qec101/02_QEC_Stabilizers.ipynb`

### 4. Advanced Applications with CUDA-Q - AI for Quantum
* `ai-for-quantum/00_[simplified]compiling_unitaries_using_diffusion_models.ipynb`

### [Bonus] Quantum Phase Classification using Quantum Convolutional Neural Networks (QCNN)
* `quantum-machine-learning/QCNN_phase_cudaq.ipynb`


<br>

# Self-Hosted Hands-on Lab Setup

## Docker Instructions (✅Recommended)

Follow these steps to set up the lab environment using a [Docker container](https://www.docker.com/):

### 1. Build the image

Go to the folder containing the [`Dockerfile`](./dockerfile), then run the following command to build the image:
```bash
docker build -t cudaq-env:latest .
```

### 2. Run the container

Start the container with GPU support and map port `8888` for JupyterLab access:
```bash
docker run -it --gpus all -p 8888:8888 cudaq-env:latest
```

### 3. Access JupyterLab

Once the container is running, open your browser and visit:
```
http://localhost:8888
```

## pip Install Instructions

An alternative method if you prefer installing packages directly in your local environment (⚠️The Docker method is still recommended as it provides a pre-configured environment with all dependencies).

### 1. Prerequisites

Make sure your system configuration (Python/driver/CUDA version) meets the [Dependencies and Compatibility](https://nvidia.github.io/cuda-quantum/latest/using/install/local_installation.html#dependencies-and-compatibility) requirements.

### 2. Install dependencies

Run the following commands in your local terminal, with the [`requirements.txt`](./requirements.txt) in your current directory:
```bash
sudo apt update && sudo apt install -y gfortran python3-pip git
pip install cudaq==0.13.0
pip install -r requirements.txt
```

### 3. Clone the repository

Clone this repository to get the tutorials:
```bash
git clone -b 2026-workshops https://github.com/NVIDIA/cuda-q-academic.git
cd kisti-workshop/tutorials
```

<br>

# Beyond This Lab

Highly recommend exploring official resources below to continue learning:
* 🎓 [CUDA-Q Academic](https://github.com/NVIDIA/cuda-q-academic) – Educational resources and research materials
* 📚 [NVIDIA CUDA-Q Documentation](https://nvidia.github.io/cuda-quantum/latest/) – Comprehensive guides and API references
* 💻 [CUDA-Q GitHub Repository](https://github.com/NVIDIA/cuda-quantum) – Source code, examples, and community discussions




