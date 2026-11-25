# pip install cudaq
import cudaq
from cudaq import spin
import itertools

mu = [0.80, 0.70, 0.25, 0.20]  # expected returns
Sigma = [
    [0.90, 0.45, 0.55, 0.10],  # variances / covariances
    [0.45, 0.40, 0.30, 0.08],
    [0.55, 0.30, 0.25, 0.05],
    [0.10, 0.08, 0.05, 0.05],
]
n = len(mu)

# The widget's return (alpha) and risk (beta) factors: change them and re-run.
alpha, beta = 1.0, 1.0

# QUBO: Q[i][i] = -alpha mu_i + beta Sigma_ii and Q[i][j] = 2 beta Sigma_ij (i < j).
# Each binary x_i becomes the operator (1 - Z_i) / 2, which is 1 when qubit i is |1>.
selected = [0.5 * (spin.i(i) - spin.z(i)) for i in range(n)]
H = sum((-alpha * mu[i] + beta * Sigma[i][i]) * selected[i] for i in range(n))
for i, j in itertools.combinations(range(n), 2):
    H += 2 * beta * Sigma[i][j] * selected[i] * selected[j]
print(H)

@cudaq.kernel
def portfolio(assets: list[int]):
    q = cudaq.qvector(len(assets))
    for i in range(len(assets)):
        if assets[i] == 1:
            x(q[i])


# The energy of each portfolio is its QUBO quality; the lowest is the optimal portfolio
quality = {
    p: cudaq.observe(portfolio, H, list(p)).expectation()
    for p in itertools.product([0, 1], repeat=n)
}
best = min(quality, key=quality.get)
print("Optimal portfolio (assets 1-4):", best)
print("Portfolio return:", sum(mu[i] * best[i] for i in range(n)))
print(
    "Portfolio risk:",
    sum(best[i] * Sigma[i][j] * best[j] for i in range(n) for j in range(n)),
)
print("QUBO quality:", quality[best])
