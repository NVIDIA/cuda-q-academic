# pip install cudaq scipy
import cudaq
import numpy as np
from scipy.optimize import curve_fit


@cudaq.kernel
def rabi_pulse(theta: float):
    q = cudaq.qubit()
    rx(theta, q)
    mz(q)


# simulated device; change it and calibrate again
pi_amplitude = 0.35
amplitudes = np.linspace(0.0, 1.10, 23)  # sweep; includes more than one Rabi maximum
shots = 200  # increase this and compare the fitted result

# Sample the excited-state probability at each drive amplitude.
probabilities = []
for amplitude in amplitudes:
    # This rotation reaches pi when amplitude equals pi_amplitude.
    theta = np.pi * amplitude / pi_amplitude
    counts = cudaq.sample(rabi_pulse, float(theta), shots_count=shots)
    probabilities.append(counts.probability("1"))
    print(f"Amplitude {amplitude:.2f}: P(1) = {probabilities[-1]:.3f}")


def rabi_curve(amplitude, fitted_pi):
    return np.sin(np.pi * amplitude / (2 * fitted_pi)) ** 2


# Fit the sweep to estimate the first pi-pulse amplitude.
fit, _ = curve_fit(
    rabi_curve, amplitudes, probabilities, p0=[0.35], bounds=(0.20, 0.50)
)
print(f"Fitted first pi-pulse amplitude: {fit[0]:.3f}")
