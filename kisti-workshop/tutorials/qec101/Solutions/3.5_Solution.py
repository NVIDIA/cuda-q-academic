import matplotlib.pyplot as plt
import cudaq
import numpy as np
from cudaq import spin
cudaq.set_target("nvidia")

hamiltonian = 0

for i in range(20):
    hamiltonian += np.random.uniform(-1, 1)*spin.z(i)
    hamiltonian += np.random.uniform(-1, 1)*spin.y(i)
    hamiltonian += np.random.uniform(-1, 1)*spin.x(i)


error_prob = 0.1

noise = cudaq.NoiseModel()
for i in range(20):
    noise.add_channel('x', [i], cudaq.BitFlipChannel(error_prob))
    noise.add_channel('rx', [i], cudaq.AmplitudeDampingChannel(error_prob))

cudaq.set_noise(noise)

@cudaq.kernel
def zne(factor: int):
    q = cudaq.qvector(20)

    for i in range(factor):
        x(q)
        rx(np.pi,q)


factors = [1,3,5,7,9]
results = []
for i in range (5):
    results.append(cudaq.observe(zne, hamiltonian,2*i+1).expectation()) 

cudaq.unset_noise() 
noiseless = cudaq.observe(zne, hamiltonian,1).expectation()

linear = np.poly1d(np.polyfit(factors, results, 1))
quadratic = np.poly1d(np.polyfit(factors, results, 2))


def plot_zero_noise_extrapolation(noise_factors, measurements, poly_fit):

    # Create a range of noise values from 0 to slightly beyond the largest noise factor
    x_range = np.linspace(0, max(noise_factors) + 0.5, 50)
    y_fit = poly_fit(x_range)

    # Plot measured data points
    plt.scatter(noise_factors, measurements, label='Measured Data', color='blue')
    # Plot polynomial fit
    plt.plot(x_range, y_fit, label='Fit (degree = {})'.format(poly_fit.order), color='red')

    # Highlight the zero-noise extrapolation point
    extrapolated_value = poly_fit(0)
    plt.scatter([0], [extrapolated_value], color='green', zorder=5, 
                label='Zero-Noise Extrapolation = {:.3f}'.format(extrapolated_value))
    
    plt.xlabel('Noise Factor')
    plt.ylabel('Measured Expectation Value')
    plt.title('Zero-Noise Extrapolation')
    plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.legend()
    plt.grid(True)
    plt.show()
    print(f"Percent Error of ZNE Estimate {(extrapolated_value - noiseless)/noiseless*100} %")


print(f"Percent Error of Uncorrected Noisy Circuit: {(results[0] - noiseless)/noiseless*100} %")


plot_zero_noise_extrapolation(factors, results, linear)
plot_zero_noise_extrapolation(factors, results, quadratic)

#The ZNE results may vary each time you run.  Preliminary runs showed that a linear fit performed worse than the noiseless circuit while a quadratic fit greatly #improved the result. 