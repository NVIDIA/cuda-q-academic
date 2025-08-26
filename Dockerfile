FROM nvcr.io/nvidia/quantum/cuda-quantum:cu12-0.11.0
WORKDIR /app
RUN pip install --upgrade pip setuptools wheel
RUN pip install cudaq==0.12.0
COPY dynamics101/ /app/dynamics101/ 
COPY images/ /app/images/ 
COPY qaoa-for-max-cut/ /app/qaoa-for-max-cut/ 
COPY qec101/ /app/qec101/ 
COPY qis-examples/ /app/qis-examples/ 
COPY quick-start-to-quantum/ /app/quick-start-to-quantum/ 
COPY quantum-applications-to-finance/ /app/quantum-applicaitons-to-finance/
ADD *.ipynb *.py /app/
ENV JUPYTER_LAB_PORT=8888
EXPOSE ${JUPYTER_LAB_PORT}
ENTRYPOINT []
CMD /usr/local/bin/jupyter-lab --port=${JUPYTER_LAB_PORT} --ip=0.0.0.0 --NotebookApp.token='' 
