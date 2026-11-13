# pip install cudaq
import cudaq
from cudaq import ptsbe


@cudaq.kernel
def three_qubits(p: float):
    # all start in |0>: no error means 0, an error means 1
    # Code qubits 0, 1, 2 = the widget's Qubit 1, 2, 3.
    qubits = cudaq.qvector(3)
    for q in range(3):
        # flip qubit q with probability p
        cudaq.apply_noise(cudaq.XError, p, qubits[q])
    mz(qubits)


# bit-flip probability per qubit; change it and re-run
p = 0.1

# Keep the most likely error paths and report their shot counts.
result = ptsbe.sample(
    three_qubits,
    p,
    shots_count=10000,
    noise_model=cudaq.NoiseModel(),
    max_trajectories=8,  # 2 x 2 x 2 = 8 paths through the tree
    # most likely paths first
    sampling_strategy=ptsbe.OrderedSamplingStrategy(),
    return_execution_data=True,
)

for trajectory in result.ptsbe_execution_data.trajectories:
    print(
        f"path {trajectory.trajectory_id}: "
        f"probability {trajectory.probability:.3f}, "
        f"shots {trajectory.num_shots}"
    )
# 000 = no errors, three 1s = an error on every qubit
print(result)
