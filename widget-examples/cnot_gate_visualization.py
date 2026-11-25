# pip install cudaq
import cudaq


@cudaq.kernel
def cnot_circuit():
    qubits = cudaq.qvector(2)  # q0 = control, q1 = target, both start in |0>

    # Prepare the inputs: x gives |1>, h gives |+>, x then h gives |->
    h(qubits[0])  # control in |+>
    # Target stays in |0>. Uncomment BOTH lines below for phase kickback:
    # x(qubits[1])
    # h(qubits[1])  # target in |->; the control becomes |-> after CNOT

    x.ctrl(qubits[0], qubits[1])  # CNOT: flip the target when the control is |1>


print(cudaq.draw(cnot_circuit))

# Amplitudes after the CNOT (bitstrings are written q0 q1).
# They are real for these input states; a minus sign is a negative phase.
state = cudaq.get_state(cnot_circuit)
for bits in ('00', '01', '10', '11'):
    amp = state.amplitude(bits)
    print(f"|{bits}>: amplitude = {amp.real:+.3f}, P = {abs(amp)**2:.3f}")

# Each shot measures both qubits and returns one bitstring.
shots = 1000
results = cudaq.sample(cnot_circuit, shots_count=shots)
for bits in ('00', '01', '10', '11'):
    print(
        f"{bits}: {results.count(bits):>4} shots  ->  sampled P = {results.count(bits) / shots:.3f}"
    )
