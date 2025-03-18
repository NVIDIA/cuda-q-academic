import cudaq
import numpy as np

#First, create an empty noise model
noise_model = cudaq.NoiseModel()
p = 0.1

#Build a custom gate which applies the identity operation
cudaq.register_operation("custom_i", np.array([1, 0, 0, 1]))

#Add a bitflip noise channel to the custom_i gate applied to each qubit
noise_model.add_channel("custom_i", [0], cudaq.BitFlipChannel(p))
noise_model.add_channel("custom_i", [1], cudaq.BitFlipChannel(p))
noise_model.add_channel("custom_i", [2], cudaq.BitFlipChannel(p))

@cudaq.kernel
def three_qubit_repetition_code():
    data_qubits = cudaq.qvector(3)
    ancilla_qubits = cudaq.qvector(2)

    # Initialize the logical |1> state as |111>
    x(data_qubits)

    # Random Bit Flip Errors
    for i in range(3):
        custom_i(data_qubits[i])

    # Extract Syndromes

    h(ancilla_qubits)

    # First Parity Check
    z.ctrl(data_qubits[0],ancilla_qubits[0])
    z.ctrl(data_qubits[1],ancilla_qubits[0])

    # Second Parity Check
    z.ctrl(data_qubits[1],ancilla_qubits[1])
    z.ctrl(data_qubits[2],ancilla_qubits[1])

    h(ancilla_qubits)

    s0 = mz(ancilla_qubits[0])
    s1 = mz(ancilla_qubits[1])


    # Correct errors based on syndromes
    if s0 and s1:
        x(data_qubits[1])
    elif s0:
        x(data_qubits[0])
    elif s1:
        x(data_qubits[2])

    mz(data_qubits)


# Run the kernel and observe results
# The percent of samples that are 000 corresponds to the logical error rate
result = cudaq.sample(three_qubit_repetition_code, noise_model=noise_model)
print(result) 