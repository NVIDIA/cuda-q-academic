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
docker build -t cuda-quantum-academic:latest .
```

To run the container, use the following command. 

```sh
docker run -p 8888:8888 cuda-quantum-academic:latest
```

You can now open a web browser to http://localhost:8888/lab to access the labs.

### Changing the port
If you cannot use port 8888 on your local machine then you can specify a differnt
port when running the the container.  For example, if you want to connect to your 
Jupyter Lab on port 8000 using http://localhost:8000/lab, then you'd do the following:

```sh
docker run -p 8000:8888 cuda-quantum-academic:latest
```

Here `8888` is the port used within the container. Docker is routing your local 
traffic on `8000` to the container port `8888`.  If you need to change the port used within
the container, then you can also specify that port when running your container. For example,
if you wish to direct your browser to port 8888 but run the Jupyter lab within the container 
on port 8000, then you'd run the following: 

```sh
docker run -e JUPYTER_LAB_PORT=8000 -p 8888:8000  cuda-quantum-academic:latest
```


## Running the notebooks in Google Colab
Simply click on the icon at the top of each notebook in github to open it up in Google Colab.  In each notebook there instructions for running CoLab.
