# pip install cudaq
import cudaq
import numpy as np
from cudaq import synth

# The widget's target unitary (its columns made orthonormal)
Q, R = np.linalg.qr(
    np.array([[0.567 - 0.234j, -0.345 + 0.678j], [0.789 + 0.123j, 0.456 - 0.567j]])
)
target = Q * (np.diag(R) / abs(np.diag(R)))


@cudaq.kernel
def my_circuit(start_in_one: bool):
    q = cudaq.qubit()
    if start_in_one:
        # run from |1> as well as |0> to get both columns of the unitary
        x(q)
    # Your gates, in order: edit these lines like clicking gates in the widget (x, y, z,
    # h, s, t)
    h(q)
    t(q)
    h(q)


# Run both basis inputs to recover the circuit unitary column by column.
U = np.column_stack([np.array(cudaq.get_state(my_circuit, s)) for s in (False, True)])
print("Unitary fidelity:", abs(np.trace(target.conj().T @ U) / 2) ** 2)

# Compile Rz(theta) into H, S and T; tighter tolerance costs more T gates.
theta = 0.6
for tolerance in (1e-1, 1e-2, 1e-4, 1e-8):
    sequence = synth.gridsynth(theta, tolerance, seed=1)
    print(
        f"tolerance {tolerance:g}: {sequence.t_count:3d} T gates, "
        f"error {synth.rz_error(theta, sequence):.1e}, "
        f"{str(sequence)[:20]}..."
    )
