import cudaq
@cudaq.kernel
def steane_code():
    """Prepares a kernel for the Steane Code
    Returns
    -------
    cudaq.kernel
        Kernel for running the Steane code
    """   
    data_qubits = cudaq.qvector(7)
    ancilla_qubits = cudaq.qvector(3)

    # Create a superposition over all possible combinations of parity check bits
    h(data_qubits[4])
    h(data_qubits[5])
    h(data_qubits[6])

    #Entangle states to enforce constraints of parity check matrix

    x.ctrl(data_qubits[0],data_qubits[1])
    x.ctrl(data_qubits[0],data_qubits[2])

    x.ctrl(data_qubits[4],data_qubits[0])
    x.ctrl(data_qubits[4],data_qubits[1])
    x.ctrl(data_qubits[4],data_qubits[3])

    x.ctrl(data_qubits[5],data_qubits[0])
    x.ctrl(data_qubits[5],data_qubits[2])
    x.ctrl(data_qubits[5],data_qubits[3])

    x.ctrl(data_qubits[6],data_qubits[1])
    x.ctrl(data_qubits[6],data_qubits[2])
    x.ctrl(data_qubits[6],data_qubits[3])

    #x(data_qubits[1])
    #x(data_qubits[3])
    

    # Detect Z errors
    h(ancilla_qubits)

    x.ctrl(ancilla_qubits[0],data_qubits[0])
    x.ctrl(ancilla_qubits[0],data_qubits[1])
    x.ctrl(ancilla_qubits[0],data_qubits[3])
    x.ctrl(ancilla_qubits[0],data_qubits[4])

    x.ctrl(ancilla_qubits[1],data_qubits[0])
    x.ctrl(ancilla_qubits[1],data_qubits[2])
    x.ctrl(ancilla_qubits[1],data_qubits[3])
    x.ctrl(ancilla_qubits[1],data_qubits[5])

    x.ctrl(ancilla_qubits[2],data_qubits[1])
    x.ctrl(ancilla_qubits[2],data_qubits[2])
    x.ctrl(ancilla_qubits[2],data_qubits[3])
    x.ctrl(ancilla_qubits[2],data_qubits[6])

    h(ancilla_qubits)

    sz1 = mz(ancilla_qubits[0])
    sz2 = mz(ancilla_qubits[1])
    sz3 = mz(ancilla_qubits[2])

    #Reset ancillas
    reset(ancilla_qubits)

    # Detect X errors
    h(ancilla_qubits)

    z.ctrl(ancilla_qubits[0],data_qubits[0])
    z.ctrl(ancilla_qubits[0],data_qubits[1])
    z.ctrl(ancilla_qubits[0],data_qubits[3])
    z.ctrl(ancilla_qubits[0],data_qubits[4])

    z.ctrl(ancilla_qubits[1],data_qubits[0])
    z.ctrl(ancilla_qubits[1],data_qubits[2])
    z.ctrl(ancilla_qubits[1],data_qubits[3])
    z.ctrl(ancilla_qubits[1],data_qubits[5])

    z.ctrl(ancilla_qubits[2],data_qubits[1])
    z.ctrl(ancilla_qubits[2],data_qubits[2])
    z.ctrl(ancilla_qubits[2],data_qubits[3])
    z.ctrl(ancilla_qubits[2],data_qubits[6])

    h(ancilla_qubits)

    sx1 = mz(ancilla_qubits[0])
    sx2 = mz(ancilla_qubits[1])
    sx3 = mz(ancilla_qubits[2])


    # Correct X errors

    if sx1 and sx2 and sx3:
        x(data_qubits[3])
    elif sx1 and sx2:
        x(data_qubits[0])
    elif sx1 and sx3:
        x(data_qubits[1])
    elif sx2 and sx3:
        x(data_qubits[2])
    elif sx1:
        x(data_qubits[4])
    elif sx2:
        x(data_qubits[5])
    elif sx3:
        x(data_qubits[6])



    # Correct Z errors

    if sz1 and sz2 and sz3:
        z(data_qubits[3])
    elif sz1 and sz2:
        z(data_qubits[0])
    elif sz1 and sz3:
        z(data_qubits[1])
    elif sz2 and sz3:
        z(data_qubits[2])
    elif sz1:
        z(data_qubits[4])
    elif sz2:
        z(data_qubits[5])
    elif sz3:
        z(data_qubits[6])

    mz(data_qubits)

results = cudaq.sample(steane_code, shots_count=1000)
print(results)  

ones = 0
zeros = 0 
for bitstring in results:
    counts = results.count(bitstring)
    parity = sum(int(bit) for bit in bitstring) % 2

    if parity == 0:
        zeros += 1*counts
    else:
        ones += 1*counts

print("0:", zeros)
print("1:", ones)






#Testing if X0X1X4 is a logical operator

ones = 0
zeros = 0 
for bitstring in results:
    counts = results.count(bitstring)
    parity = (int(bitstring[0])+int(bitstring[1])+int(bitstring[4])) % 2

    if parity == 0:
        zeros += 1*counts
    else:
        ones += 1*counts

print("0:", zeros)
print("1:", ones)



#Testing if X0X4X5 is a logical operator

ones = 0
zeros = 0 
for bitstring in results:
    counts = results.count(bitstring)
    parity = (int(bitstring[0])+int(bitstring[5])+int(bitstring[4])) % 2

    if parity == 0:
        zeros += 1*counts
    else:
        ones += 1*counts

print("0:", zeros)
print("1:", ones)
