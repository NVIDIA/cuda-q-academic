import cudaq
import numpy as np

cudaq.set_target("density-matrix-cpu")

noise = cudaq.NoiseModel()
noise.add_channel('x', [0], cudaq.BitFlipChannel(.1))
noise.add_channel('x', [1], cudaq.BitFlipChannel(.25))


@cudaq.kernel
def test():
    reg = cudaq.qvector(2)
    x(reg)


print(cudaq.sample(test, noise_model=noise))