import numpy as np 

H = np.array([
    [1, 1, 0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1]
])

#Build 2 round parity check matrix.
H2 =  np.array([
    [1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1]
])

#Syndrome for no error
e = np.array([0,0,0,0,0,0,0, 0,0,0,  0,0,0,0,0,0,0])

print(H2 @ e.T)

#syndrome for error on first data qubit
e = np.array([1,0,0,0,0,0,0, 0,0,0,  0,0,0,0,0,0,0])

print(H2 @ e.T)

#syndrome for error on first ancilla qubit
e = np.array([0,0,0,0,0,0,0, 1,0,0,  0,0,0,0,0,0,0])

print(H2 @ e.T)

# Notice measurement errors are the only cases where the forst three and last three bits of the syndrome with disagree.