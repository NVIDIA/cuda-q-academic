This directory contains Jupyter notebooks that can be run on a local installation of CUDA-Q.  The `requirements.txt` and `Dockerfile` are
included here. Please refer to the [Quick Start Guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#validate-installation)
for instructions on how to install CUDA-Q on your system.

Most of the material in these notebooks can be run without a GPU.  However, the portions of the notebook that use MPI will require
a GPU to execute.  

If you don't have CUDA-Q installed on your system, you can run the notebooks in Google Colab.

## Building the container for local execution

The following command will build the CUDA Quantum Academic container. To
customize this container, make edits to the included `Dockerfile`. 

```sh
# Login to NVIDIA GPU Cloud for access to CUDA-Q base container
docker login nvcr.io
# Follow the login instructions at ngc.nvidia.com
# Next, build the container locally
docker build -t cuda-quantum-academic:latest
```

To run the container, use the following command. By default Jupyter-lab will
use port 8888 and docker will expose this port. If you wish to use a different
port, see the directions below.

```sh
docker run cuda-quantum-academic:latest
```

You can now open a web browser to http://localhost:8888/lab to access the labs.

### Changing the port
You can either change the port that will be used by jupyter-lab at build time
(more permanent) or at runtime (more dynamic).

Build time:
```sh
docker build --build-arg JUPYTER_LAB_PORT=8000 -t cuda-quantum-academic:latest
docker run cuda-quantum-academic:latest
```

Run time:
```sh
docker run -p 8000:8888 cuda-quantum-academic:latest
```

## Running the notebooks in Google Colab
Simply click on the icon at the top of each notebook in github to open it up in Google Colab.  In each notebook there instructions for running CoLab.
