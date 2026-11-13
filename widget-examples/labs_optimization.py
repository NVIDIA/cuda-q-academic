# pip install cudaq
import cudaq
from cudaq import spin
from collections import Counter

N = 7
# C_k = sum_i s_i s_(i+k), with s_i = +1 for |0> and -1 for |1>.
C = [sum(spin.z(i) * spin.z(i + k) for i in range(N - k)) for k in range(1, N)]
H = sum(c * c for c in C)  # E = sum over k of C_k^2


@cudaq.kernel
def sequence(s: list[int]):
    q = cudaq.qvector(len(s))
    for i in range(len(s)):
        if s[i] == -1:
            x(q[i])


# 1. The widget's sequence: change any +1 to -1 and re-run.
s = [1, 1, 1, 1, 1, 1, 1]
print("Energy of your sequence:", round(cudaq.observe(sequence, H, s).expectation()))


# 2. Put all 128 sequences in an equal superposition.
@cudaq.kernel
def all_sequences(n: int):
    q = cudaq.qvector(n)
    h(q)


print("Average energy of all 128 sequences:",
      round(cudaq.observe(all_sequences, H, N).expectation(), 3))


# 3. Each shot measures one uniformly random sequence.
def energy(bits):
    signs = [1 if bit == "0" else -1 for bit in bits]
    return sum(sum(signs[i] * signs[i + k] for i in range(N - k)) ** 2
               for k in range(1, N))


counts = cudaq.sample(all_sequences, N, shots_count=50)
histogram = Counter()
for bits in counts:
    histogram[energy(bits)] += counts.count(bits)
for E in sorted(histogram):
    print(f"E = {E:2d}: {'#' * histogram[E]}")
# Only 4 of the 128 sequences reach E = 3. A 50-shot run may miss them.
# The lesson's counterdiabatic circuit aims to favor lower-energy sequences.
