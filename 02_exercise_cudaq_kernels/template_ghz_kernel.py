import timeit

import cudaq


@cudaq.kernel
def ghz(#TODO enter typed input variable(s)):
    qubits = cudaq.qvector(#TODO initialize register with n qubits)

    #TODO implement GHZ circuit gates

cudaq.set_target(#TODO target 'nvidia' backend)

qubit_count = 3
print(cudaq.draw(ghz, qubit_count))
start = timeit.default_timer()
counts = cudaq.sample(ghz, qubit_count)
print(f"Sample time: {timeit.default_timer() - start:.6f} seconds")
print(counts)


# Later exercise: sample the circuit with depolarizing noise (p = 0.1).
# error_probability = 0.1
# noise = cudaq.NoiseModel()
# noise.add_all_qubit_channel(
#     "h", cudaq.Depolarization1(error_probability)
# )
# noise.add_all_qubit_channel(
#     "x",
#     cudaq.Depolarization2(error_probability),
#     num_controls=1,
# )
# noisy_counts = cudaq.sample(
#     ghz,
#     qubit_count,
#     shots_count=1000,
#     noise_model=noise,
# )
# print(noisy_counts)
