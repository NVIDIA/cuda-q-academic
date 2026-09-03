import numpy as np
import stim


def c_m(x,y,N):
    return(y*N+x)

class StimCircuit:
   
    def __init__(self,d,height):
        self.d = d
        self.height = height
        self.circuit = stim.Circuit()
        self.measurement_count = 0 

    def initialise(self):
        width=2*self.d-1
        for i in range(0,width):
            for j in range (0,self.height):
                self.circuit.append("Qubit_COORDS",c_m(i,j,width),[j,i])

    def reset(self):
        width=2*self.d-1
        for j in range(self.height):
            for i in range(0,2*self.d-1,2):
                if j == 0:
                    self.circuit.append("R", c_m(i,j,width))
                else:
                    self.circuit.append("R", c_m(i,j,width))

    def round(self):
        width=2*self.d-1
        for j in range(self.height):
            for i in range(1,2*self.d-1,2):
                self.circuit.append("RX", c_m(i,j,width))
        self.circuit.append("TICK")
        for j in range(self.height):
            for i in range(1,2*self.d-1,2):
                self.circuit.append("CX",[c_m(i,j,width),c_m(i-1,j,width)])
        self.circuit.append("TICK")
        for j in range(self.height):
            for i in range(1,2*self.d-1,2):
                self.circuit.append("CX",[c_m(i,j,width),c_m(i+1,j,width)])
        self.circuit.append("TICK")
        for j in range(self.height):
            for i in range(1,2*self.d-1,2):
                self.circuit.append("MX", c_m(i,j,width))
                self.measurement_count += 1
        self.circuit.append("TICK")

    def cswap(self,a,b):
        width=2*self.d-1
        for i in range(0,2*self.d-1,2):
            self.circuit.append("CX", [c_m(i,a,width),c_m(i,b,width)])
        self.circuit.append("TICK")
        for i in range(0,2*self.d-1,2):
            self.circuit.append("CX", [c_m(i,b,width),c_m(i,a,width)])
        self.circuit.append("TICK")    

    def swap(self,a,b):
        width=2*self.d-1
        for i in range(0,2*self.d-1,2):
            self.circuit.append("CX", [c_m(i,a,width),c_m(i,b,width)])
        self.circuit.append("TICK")
        for i in range(0,2*self.d-1,2):
            self.circuit.append("CX", [c_m(i,b,width),c_m(i,a,width)])
        self.circuit.append("TICK")
        for i in range(0,2*self.d-1,2):
            self.circuit.append("CX", [c_m(i,a,width),c_m(i,b,width)])
        self.circuit.append("TICK")

    def cnot(self,a,b):
        width=2*self.d-1
        for i in range(0,2*self.d-1,2):
            self.circuit.append("CX", [c_m(i,a,width),c_m(i,b,width)])
        self.circuit.append("TICK") 

    def fswap(self,a,b):
        width=2*self.d-1
        for i in range(0,2*self.d-1,2):
            self.circuit.append("SWAP", [c_m(i,a,width),c_m(i,b,width)])



    def gate(self,gate,a):
        width=2*self.d-1
        for i in range(0,2*self.d-1,2):
            self.circuit.append(gate, c_m(i,a,width))
            if gate == "M" or gate == "MX":  # Count measurement gates
                self.measurement_count += 1



def AddNoise(circuit,p):

    result = stim.Circuit()



    qubit_processed = []

    for instruction in circuit:
        
        if instruction.name == 'RX':
            result.append(instruction)
            result.append("X_ERROR",[target.qubit_value for target in instruction.targets_copy()],p)
            qubit_processed += [target.qubit_value for target in instruction.targets_copy()]

        
        elif instruction.name == 'R':
            result.append(instruction)
            result.append("X_ERROR",[target.qubit_value for target in instruction.targets_copy()],p)
            qubit_processed += [target.qubit_value for target in instruction.targets_copy()]

        
        elif instruction.name == 'MX':
            result.append("X_ERROR",[target.qubit_value for target in instruction.targets_copy()],p)
            result.append(instruction)
            qubit_processed += [target.qubit_value for target in instruction.targets_copy()]

        elif instruction.name == 'M':
            result.append("X_ERROR",[target.qubit_value for target in instruction.targets_copy()],p)
            result.append(instruction)
            qubit_processed += [target.qubit_value for target in instruction.targets_copy()]

        
        elif instruction.name == 'CX':
            for index,target in enumerate(instruction.targets_copy()):
                if index%2 == 1:
                    result.append("X_ERROR",target.qubit_value,p/3)
            result.append(instruction)
            for index,target in enumerate(instruction.targets_copy()):
                if index%2 == 1:
                    result.append("X_ERROR",target.qubit_value,p/3)
                else:
                    result.append("X_ERROR",target.qubit_value,p/3)      
            qubit_processed += [target.qubit_value for target in instruction.targets_copy()]
        
        elif instruction.name == 'TICK':
            for i in range(circuit.num_qubits):
                if i not in qubit_processed:
                    result.append("X_ERROR",i,p)
            result.append(instruction)
            qubit_processed = []
        else:
            result.append(instruction)
            qubit_processed += [target.qubit_value for target in instruction.targets_copy()]

    circuit = result
    
    return circuit


def circ(d,rs):
    circuit=StimCircuit(d=d,height=8)
    circuit.initialise()
    circuit.reset()
    
    for r in range(rs):

        if r !=0:
            circuit.gate("R",0)
        circuit.round()
        circuit.cswap(0,1)
        circuit.round()
        circuit.swap(1,2)
        circuit.round()
        circuit.swap(2,3)
        circuit.round()
        circuit.cswap(3,4)
        circuit.round()
        circuit.swap(4,5)
        circuit.round()
        circuit.cswap(5,6)
        circuit.round()
        circuit.cnot(7,6)
        circuit.round()
        if d > 8:
            for i in range(d-8):
                circuit.round()
        circuit.gate("M",6)


        if r ==0:
            gap_0a=circuit.measurement_count
        if r == 1:
            gap_0b=circuit.measurement_count
        
        if r ==rs-1:
            c1=circuit.measurement_count
            
        if r == 0:
            circuit.circuit.append("DETECTOR", [stim.target_rec(-1 - i) for i in range(d)])
        if r  !=0:
            gap_0 = gap_0b-gap_0a 
            circuit.circuit.append("DETECTOR", 
                                   [stim.target_rec(-1 - i) for i in range(d)] + 
                                   [stim.target_rec(-1 - i - gap_0) for i in range(d)]
            )


        circuit.gate("R",6)
        circuit.round()
        circuit.cnot(7,6)
        circuit.round()
        circuit.swap(6,5)
        circuit.round()
        circuit.cswap(5,4)
        circuit.round()
        circuit.cswap(4,3)
        circuit.round()
        circuit.swap(3,2)
        circuit.round()
        circuit.cnot(1,2)
        if d > 6:
            for i in range(d-6):
                circuit.round()
        circuit.gate("M",2)

        if r ==rs-1:
            c2=circuit.measurement_count
        if r == 0:
            circuit.circuit.append("DETECTOR", [stim.target_rec(-1 - i) for i in range(d)])
        else:

            circuit.circuit.append("DETECTOR", 
                                   [stim.target_rec(-1 - i) for i in range(d)] + 
                                   [stim.target_rec(-1 - i - gap_0) for i in range(d)]
            )

        circuit.gate("R",2)
        circuit.round()
        circuit.cswap(2,3)
        circuit.round()
        circuit.swap(3,4)
        circuit.round()
        circuit.cswap(4,5)
        circuit.round()
        circuit.cswap(5,6)
        circuit.round()
        circuit.cnot(7,6)
        circuit.round()
        if d > 6:
            for i in range(d-6):
                circuit.round()
        circuit.gate("M",6)

        if r ==rs-1:
            c3=circuit.measurement_count
        if r == 0:
            circuit.circuit.append("DETECTOR", [stim.target_rec(-1 - i) for i in range(d)])
        else:

            circuit.circuit.append("DETECTOR", 
                                   [stim.target_rec(-1 - i) for i in range(d)] + 
                                   [stim.target_rec(-1 - i - gap_0) for i in range(d)]
            )


        if r != rs-1:
            circuit.fswap(6,5)
            circuit.fswap(5,4)
            circuit.fswap(4,3)
            circuit.fswap(3,2)
            circuit.fswap(2,1)
            circuit.fswap(1,0)



    for i in range(8):
        if i !=6:
            circuit.gate("M",i)
    final=circuit.measurement_count 


    circuit.circuit.append("Detector",[stim.target_rec(-1-i-(final-c1)) for i in range(d)]+
                           [stim.target_rec(-1-0*d-i)for i in range(d)]+
                           [stim.target_rec(-1-1*d-i)for i in range(d)]+
                           [stim.target_rec(-1-3*d-i)for i in range(d)]+
                           [stim.target_rec(-1-6*d-i)for i in range(d)]) 

    circuit.circuit.append("Detector",[stim.target_rec(-1-i-(final-c2)) for i in range(d)]+
                               [stim.target_rec(-1-0*d-i)for i in range(d)]+
                               [stim.target_rec(-1-2*d-i)for i in range(d)]+
                               [stim.target_rec(-1-3*d-i)for i in range(d)]+
                               [stim.target_rec(-1-5*d-i)for i in range(d)]) 

    circuit.circuit.append("Detector",[stim.target_rec(-1-i-(final-c3)) for i in range(d)]+
                               [stim.target_rec(-1-0*d-i)for i in range(d)]+
                               [stim.target_rec(-1-1*d-i)for i in range(d)]+
                               [stim.target_rec(-1-2*d-i)for i in range(d)]+
                               [stim.target_rec(-1-4*d-i)for i in range(d)]) 

    circuit.circuit.append("Observable_Include",[stim.target_rec(-1-6*d-i)for i in range(d)],0)
    circuit.circuit.append("Observable_Include",[stim.target_rec(-1-5*d-i)for i in range(d)],1)
    circuit.circuit.append("Observable_Include",[stim.target_rec(-1-4*d-i)for i in range(d)],2)


    return(circuit.circuit)

def noisy_circ(d,rs,p):
    return(AddNoise(circ(d,rs),p))
