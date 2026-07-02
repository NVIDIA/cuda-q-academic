import math

import cudaq
import matplotlib.pyplot as plt
from cudaq import spin
from cudaq.dynamics import InitialState, Schedule


cudaq.set_target("dynamics")

# Model one two-level spin and watch it for five relaxation times.
t1 = 10.0
number_of_steps = 101
time_steps = [
    5.0 * t1 * step / (number_of_steps - 1)
    for step in range(number_of_steps)
]
schedule = Schedule(time_steps, ["time"])

dimensions = {0: 2}
hamiltonian = 0.0 * spin.z(0)
initial_state = InitialState.ZERO
relaxation = math.sqrt(1.0 / t1) * spin.minus(0)

result = cudaq.evolve(
    hamiltonian,
    dimensions,
    schedule,
    initial_state,
    collapse_operators=[relaxation],
    observables=[spin.z(0)],
    store_intermediate_results=cudaq.IntermediateResultSave.EXPECTATION_VALUE,
)

# For this spin convention, (1 + <Z>) / 2 is the upper-state probability.
excited_state_probability = [
    (1.0 + values[0].expectation()) / 2.0
    for values in result.expectation_values()
]

print("Expected result:")
print("The excited-state probability should decay exponentially from 1 to 0.")
print(f"At T1 = {t1}, it should be about 1/e = {1.0 / math.e:.2f}.")

figure, axes = plt.subplots()
axes.plot(time_steps, excited_state_probability)
axes.set_title("CUDA-Q T1 Relaxation Experiment")
axes.set_xlabel("Time")
axes.set_ylabel("Excited-state probability")
axes.set_ylim(0.0, 1.05)
axes.grid(True)
figure.tight_layout()
figure.savefig("t1_experiment.png")
print("Saved plot to t1_experiment.png")
plt.show()
