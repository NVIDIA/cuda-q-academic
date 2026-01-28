FROM nvcr.io/nvidia/quantum/cuda-quantum:cu13-0.13.0
USER root

RUN apt-get update && apt-get install -y \
    gfortran \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir -v jupyterlab

RUN pip3 install --no-cache-dir -v \
    cudaq-solvers==0.5.0 \
    cudaq_qec==0.5.0 \
    pyscf==2.6.2 \
    openfermionpyscf==0.5 \
    matplotlib==3.8.4 \
    openfermion==1.6.1 \
    genQC==0.1.0 \
    torch==2.9.1

RUN python3 -m jupyter --version

WORKDIR /home/cudaq
RUN git clone -b 2026-workshops https://github.com/NVIDIA/cuda-q-academic.git

EXPOSE 8888

ENV JUPYTER_TOKEN=''
ENV JUPYTER_PASSWORD=''

ENTRYPOINT ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]