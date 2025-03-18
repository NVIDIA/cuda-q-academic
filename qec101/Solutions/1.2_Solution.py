import numpy as np


message = np.array([0, 1, 1, 0])

G = np.array([
    [1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 1],
    [0, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 1, 1, 1, 1]
])

encoded = np.dot(message, G) % 2

print(encoded)



received = np.array([0, 0, 1, 0,1,1,0])
print(received)


# Define the parity check matrix H
H = np.array([
    [1, 1, 0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1]
])

decoded = np.dot(H,received) % 2
print(decoded)