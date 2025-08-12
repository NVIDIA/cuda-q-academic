import numpy as np
import galois


GF2 = galois.GF(2)

#parity check matrix as numpy array
H = np.array([[0, 1, 0, 0, 1, 0],
              [0, 0, 1, 0, 0, 1],
              [1, 0, 0, 1, 0, 0],
              [1, 0, 0, 0, 1, 1]])

bp_results = [0.05, 0.5, 0.01, 0.01, 0.82, 0.05]
s = GF2([1,0,0,1])

# Get indices that would sort bp_results in descending order
sorted_indices = sorted(range(len(bp_results)), key=lambda k: bp_results[k], reverse=True)

# Rearrange columns of numpy array
H_sorted = H[:, sorted_indices]

# Convert to GF2 matrix after rearrangement for mod 2 aritmatic
GF2 = galois.GF(2)
H_sorted = GF2(H_sorted)

# Perform Gaussian elimination to identify the first four columns of full rank.
def rref(matrix):
    rows, cols = matrix.shape
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        if matrix[r, c] == 0:
            for i in range(r + 1, rows):
                if matrix[i, c] != 0:
                    matrix[[r, i]] = matrix[[i, r]]
                    break
        if matrix[r, c] == 0:
            continue
        matrix[r] = matrix[r] / matrix[r, c]
        for i in range(rows):
            if i != r and matrix[i, c] != 0:
                matrix[i] = matrix[i] - matrix[i, c] * matrix[r]
        r += 1
    return matrix

print("Gaussian Elimination Result")
print(rref(H_sorted.copy())) # First four columns are pivot columns

# Build H_s from the first full rank columns
Hs = H_sorted[:,:4]
print("Hs 4x4 Matrix")
print(Hs)

# Compute Hs_inverse
Hs_inverse = np.linalg.inv(Hs)

# Calculate e_s
e_s = Hs_inverse @ s.T
print("Error solution for Hs")
print(e_s)

# Pad result with zeros and reorder based on colum sorting from earlier.
e = np.pad(e_s, (0, 2), 'constant', constant_values=(0, 0))
print("Errors - Padded and Permuted")
print(e)


e_original = np.zeros_like(e)
for i in range(len(e)):
    e_original[sorted_indices[i]] = e[i]

print("Errors - Original Ordering")
print(e_original)

# Confirm that the errors produce the expected syndrome from the original H
print("Syndrome")
print(GF2(H) @ GF2(e_original.T))