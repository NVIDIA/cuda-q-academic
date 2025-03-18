import cudaq
import numpy as np

cudaq.set_target('nvidia')



@cudaq.kernel
def shor_code(error_type: list[int], error_location: list[int], measure: int):
    """Prepares a kernel for the Shor Code

    Parameters
    -----------
    error_type: list[int]
        a list where each element is an applied error designated as 1 = z or 2 = x
    error_location: list[int]
        each element corresponds to the index of the qubit which the error occurs on
    measure: int
        Option to measure in the z basis (1) or the x basis (2)

    Returns
    -------
    cudaq.kernel
        Kernel for running the Shor code
    """   


    data_qubits = cudaq.qvector(9) 
    ancilla_qubits = cudaq.qvector(8)

    #Start Psi in the 0 state
    
    
    #Start Psi in the plus state
    #h(data_qubits[0])
    
    #Start with Psi in a state which will make a 75/25 distribution in the Z and X basis.
    #ry(np.pi/8,data_qubits[0])
    #Encoding circuit
    
    cx(data_qubits[0],data_qubits[3])
    cx(data_qubits[0],data_qubits[6])

    h(data_qubits[0])
    h(data_qubits[3])
    h(data_qubits[6])

    x.ctrl(data_qubits[0],data_qubits[1])
    x.ctrl(data_qubits[0],data_qubits[2])

    x.ctrl(data_qubits[3],data_qubits[4])
    x.ctrl(data_qubits[3],data_qubits[5])

    x.ctrl(data_qubits[6],data_qubits[7])
    x.ctrl(data_qubits[6],data_qubits[8])

    # Apply optional errors
    for i in range(len(error_type)):
        if error_type[i] == 1:
            x(data_qubits[error_location[i]])
        if error_type[i] == 2:
            z(data_qubits[error_location[i]])
    
    # Prepare ancilla qubits
    h(ancilla_qubits)
    
    # Bit Flip Syndromes
    z.ctrl(ancilla_qubits[0], data_qubits[0])
    z.ctrl(ancilla_qubits[0], data_qubits[1])

    z.ctrl(ancilla_qubits[1], data_qubits[1])
    z.ctrl(ancilla_qubits[1], data_qubits[2])

    z.ctrl(ancilla_qubits[2], data_qubits[3])
    z.ctrl(ancilla_qubits[2], data_qubits[4])

    z.ctrl(ancilla_qubits[3], data_qubits[4])
    z.ctrl(ancilla_qubits[3], data_qubits[5])

    z.ctrl(ancilla_qubits[4], data_qubits[6])
    z.ctrl(ancilla_qubits[4], data_qubits[7])

    z.ctrl(ancilla_qubits[5], data_qubits[7])
    z.ctrl(ancilla_qubits[5], data_qubits[8])

    # Phase Flip Syndromes
    x.ctrl(ancilla_qubits[6], data_qubits[0])
    x.ctrl(ancilla_qubits[6], data_qubits[1])
    x.ctrl(ancilla_qubits[6], data_qubits[2])
    x.ctrl(ancilla_qubits[6], data_qubits[3])
    x.ctrl(ancilla_qubits[6], data_qubits[4])
    x.ctrl(ancilla_qubits[6], data_qubits[5])

    x.ctrl(ancilla_qubits[7], data_qubits[3])
    x.ctrl(ancilla_qubits[7], data_qubits[4])
    x.ctrl(ancilla_qubits[7], data_qubits[5])
    x.ctrl(ancilla_qubits[7], data_qubits[6])
    x.ctrl(ancilla_qubits[7], data_qubits[7])
    x.ctrl(ancilla_qubits[7], data_qubits[8])
    
  
    # Apply Hadamard gate to ancilla qubits 
    h(ancilla_qubits)

  # Perform mid-circuit measurements to determine syndromes   
    s0 = mz(ancilla_qubits[0])
    s1 = mz(ancilla_qubits[1])
    s2 = mz(ancilla_qubits[2])
    s3 = mz(ancilla_qubits[3])
    s4 = mz(ancilla_qubits[4])
    s5 = mz(ancilla_qubits[5])
    s6 = mz(ancilla_qubits[6])
    s7 = mz(ancilla_qubits[7])

    # Apply the appropriate corrections based on the results from the syndrome measurements
    if s0 and s1:
        x(data_qubits[1])
    elif s0:
        x(data_qubits[0])
    elif s1:
        x(data_qubits[2])

    if s2 and s3:
        x(data_qubits[4])
    elif s2:
        x(data_qubits[3])
    elif s3:
        x(data_qubits[5])

    if s4 and s5:
        x(data_qubits[7])
    elif s4:
        x(data_qubits[6])
    elif s5:
        x(data_qubits[8])

    if s6 and s7:
        z(data_qubits[3])
    elif s6:
        z(data_qubits[0])
    elif s7:
        z(data_qubits[6])

    if measure == 1:
        h(data_qubits)
        mz(data_qubits)
    if measure == 2:
        h(data_qubits)
        h(data_qubits)
        mz(data_qubits)
    

def post_process(results):
    """takes results from a CUDA-Q sample and prints the number of 0's and 1's by computing the parity of the bitstrings.

    Parameters
    -----------
    results: cudaq.SampleResult
                A dictionary of the results from sampling the quantum state
    """
    ones = 0
    zeros = 0
    for result in results:
        
        count = results.count(result)
        bits = [int(bit) for bit in result]
        
        parity = sum(bits[0:9]) % 2 
      

        if parity == 0:
            zeros += 1*count
        else: 
            ones += 1*count
    
    #print(results)
    print("Zeros:", zeros)
    print("Ones:",ones) 
print(cudaq.sample(shor_code,[], [],1 ,shots_count = 1))

#print("No Errors")
#post_process(cudaq.sample(shor_code,[], [],1 ,shots_count = 1000))
#post_process(cudaq.sample(shor_code,[], [],2 ,shots_count = 1000))

#print("X Errors")
#post_process(cudaq.sample(shor_code,[1], [0],1 ,shots_count = 1000))
#post_process(cudaq.sample(shor_code,[1], [0],2 ,shots_count = 1000))

#print("Z Errors")
#post_process(cudaq.sample(shor_code,[2], [0],1 ,shots_count = 1000))
#post_process(cudaq.sample(shor_code,[2], [0],2 ,shots_count = 1000))