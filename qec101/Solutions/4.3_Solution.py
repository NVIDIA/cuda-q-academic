import cudaq
import numpy as np

p = 0.05
cudaq.unset_noise()
noise = cudaq.NoiseModel()

@cudaq.kernel
def steane_code():
    """Prepares a kernel for the Steane Code
    Returns
    -------
    cudaq.kernel
        Kernel for running the Steane code
    """   
    data_qubits = cudaq.qvector(7)
    ancilla_qubits = cudaq.qvector(3)

    # Create a superposition over all possible combinations of parity check bits
    h(data_qubits[4])
    h(data_qubits[5])
    h(data_qubits[6])

    #Entangle states to enforce constraints of parity check matrix

    x.ctrl(data_qubits[0],data_qubits[1])
    x.ctrl(data_qubits[0],data_qubits[2])

    x.ctrl(data_qubits[4],data_qubits[0])
    x.ctrl(data_qubits[4],data_qubits[1])
    x.ctrl(data_qubits[4],data_qubits[3])

    x.ctrl(data_qubits[5],data_qubits[0])
    x.ctrl(data_qubits[5],data_qubits[2])
    x.ctrl(data_qubits[5],data_qubits[3])

    x.ctrl(data_qubits[6],data_qubits[1])
    x.ctrl(data_qubits[6],data_qubits[2])
    x.ctrl(data_qubits[6],data_qubits[3])

    for j in range(7):
        cudaq.apply_noise(cudaq.XError, p, data_qubits[j])

    # Detect X errors
    h(ancilla_qubits)

    z.ctrl(ancilla_qubits[0],data_qubits[0])
    z.ctrl(ancilla_qubits[0],data_qubits[1])
    z.ctrl(ancilla_qubits[0],data_qubits[3])
    z.ctrl(ancilla_qubits[0],data_qubits[4])

    z.ctrl(ancilla_qubits[1],data_qubits[0])
    z.ctrl(ancilla_qubits[1],data_qubits[2])
    z.ctrl(ancilla_qubits[1],data_qubits[3])
    z.ctrl(ancilla_qubits[1],data_qubits[5])

    z.ctrl(ancilla_qubits[2],data_qubits[1])
    z.ctrl(ancilla_qubits[2],data_qubits[2])
    z.ctrl(ancilla_qubits[2],data_qubits[3])
    z.ctrl(ancilla_qubits[2],data_qubits[6])

    h(ancilla_qubits)

    ancilla = mz(ancilla_qubits)
    data = mz(data_qubits)

# Generate Data
nsamples = 10000
syndromes = []
data_qubits = []
logical_flips =[]

for x in range(nsamples):
    results = cudaq.sample(steane_code, noise_model=noise, shots_count=1)
    ancilla = [int(x) for x in np.array(results.get_register_counts('ancilla'))[0]]
    data = [int(x) for x in np.array(results.get_register_counts('data'))[0]]
    syndromes.append(ancilla)
    parity = (data[0] + data[1] + data[2] + data[3] + data[4] + data[5] + data[6]) %2
    logical_flips.append(parity)




print(syndromes[0:10])
print(logical_flips[0:10])