import random
import matplotlib.pyplot as plt


def encode(bit, n):
    """Function that encodes a single bit rendundantly n times

    Parameters
    ----------
    bit: int
        Input bit (1 or 0)
    n : int
        repetitions to use for encoding

    Returns
    -------
    str
        string of length n redundantly encoding bit
    """
    return [bit] * n

def decode(bits):
    """Function that decodes a message using majority voting to determine the closest codeword

    Parameters
    ----------
    bits: str
        bitstring corresponding to message that has passed through noisy channel

    Returns
    -------
    int
        1 or 0 corresponding to decoded codeword
    """
    return 1 if sum(bits) > len(bits) // 2 else 0

def transmit(bits, p_error):
    """Function that receives a codeword, and randomly flips each bit with probability p_error to emulate transmission through noisy channel
    
    Parameters
    ----------
    bits: str
        bitstring corresponding to an encoded message without noise
    p_error: float
        probability that a bit will flip through transmission

    Returns
    -------
    int
        1 or 0 corresponding to decoded codeword
    """
    return [1 - bit if random.random() < p_error else bit for bit in bits]

def simulate_logical_error_rate(n, p_error, trials):    
    """Function to determine the logical error rate of an n-bit repetition code over specified number of trials.
    
    Parameters
    ----------
    n: int
        specifies n-bit repetition code to use
    p_error: float
        probability that a bit will flip through transmission
    trials: int
        number of trials used to determine logical error rate

    Returns
    -------
    float
        The logical error rate `n_errors/trials`
    """   
    errors = 0
    for _ in range(trials):
        bit = random.randint(0, 1)
        encoded = encode(bit, n)
        received = transmit(encoded, p_error)
        decoded = decode(received)
        if decoded != bit:
            errors += 1
    return errors / trials

def plot_logical_vs_physical_error_rate(n, trials):
    """Function to plot logical vs physical error rate for fixed n and number of trials.
    
    Parameters
    ----------
    n: int
        specifies n-bit repetition code to use
    trials: int
        number of trials used to determine logical error rate
    """  

    p_values = [i * 0.01 for i in range(51)]  # Physical error rates from 0 to 0.3
    logical_error_rates = [simulate_logical_error_rate(n, p, trials) for p in p_values]

    plt.figure(figsize=(10, 6))
    plt.plot(p_values, logical_error_rates, marker='o')
    plt.title('Logical Error Rate vs Physical Error Rate')
    plt.xlabel('Physical Error Rate')
    plt.ylabel('Logical Error Rate')
    plt.grid(True)
    plt.show()

def plot_logical_vs_repetitions(p_error, max_n, trials):
    """Function to plot logical error rate vs bits used for redundant encoding
    
    Parameters
    ----------
    max_n: int
        specifies the maximum n-bit repetition code to use
    p_error: float
        probability that a bit will flip through transmission
    trials: int
        number of trials used to determine logical error rate
    """   
    n_values = range(1, max_n + 1)  # Repetition sizes from 1 to max_n
    logical_error_rates = [simulate_logical_error_rate(n, p_error, trials) for n in n_values]

    plt.figure(figsize=(10, 6))
    plt.plot(n_values, logical_error_rates, marker='o')
    plt.title('Logical Error Rate vs Number of Repetitions (n)')
    plt.xlabel('Number of Repetitions (n)')
    plt.ylabel('Logical Error Rate')
    plt.grid(True)
    plt.show()

# Example Usage
n = 3         # Number of repetitions for the first plot
p_error = 0.1       # Physical error rate for the second plot
trials = 10000

# Generate the plots
plot_logical_vs_physical_error_rate(n, trials)
"""Notice how the logical error rate is an improvement over the physical error rate as long as an error is less that 50% likley."""

max_n=20
plot_logical_vs_repetitions(p_error, max_n, trials)
"""Encoding the data with more bits improves the logical error rate to the point where logical errors are virtually nonexistent.  Notice how going from n to n+1 when n is odd does not add much improvement as even numbers can result in voting where a tie occurs."""




