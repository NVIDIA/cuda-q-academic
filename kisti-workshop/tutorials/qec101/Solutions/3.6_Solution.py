"""
The different error sources should get increasingly worse, with the worst case involving measuremente rrro whci cannot be fixed by stabilizer measurements.

Case 1 is performed by adding the following code right after the encoding circuit and should produce a result around 0.04.


    for j in range(7):
            cudaq.apply_noise(cudaq.XError, p, data_qubits[j])
"""

"""
**Answer:**  
Case 2 is performed by adding individual errors following each gate in the encoding circuit. See example below.  The logical error rate should be around 0.11

    x.ctrl(data_qubits[0],data_qubits[1])
    cudaq.apply_noise(cudaq.Depolarization2, p, data_qubits[0], data_qubits[1])
"""


"""
Case 3 is performed by adding the following line before the CUDA-Q kernel.  This should produce a logical error rate of around 0.45. 

    noise = cudaq.NoiseModel()
    noise.add_all_qubit_channel("mz", cudaq.BitFlipChannel(0.1))
"""
