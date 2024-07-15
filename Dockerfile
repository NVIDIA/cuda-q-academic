FROM nvcr.io/nvidia/quantum/cuda-quantum:0.7.1
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r /app/requirements.txt
ADD *.ipynb *.py images/ /app/
ENV JUPYTER_LAB_PORT=8888
EXPOSE ${JUPYTER_LAB_PORT}
ENTRYPOINT []
CMD /usr/local/bin/jupyter-lab --port=${JUPYTER_LAB_PORT} --NotebookApp.token=''
