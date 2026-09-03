import numpy as np
import stim


def c_m(x,y,N):
    return(y*N+x)


class StimCircuit:  #Class for creating elevator code circuits and placing detectors
   
    def __init__(self):
        self.circuit = stim.Circuit()
        self.measurement_count = 0 

    def initialise(self, d):
        width=2*d-1
        height=16
        for i in range(0,width):
            for j in range (0,height):
                self.circuit.append("Qubit_COORDS",c_m(i,j,width),[j,i])

    def reset(self,d):
        width=2*d-1
        height=16
        for j in range(height):
            for i in range(0,2*d-1,2):
                if j == 0:
                    self.circuit.append("R", c_m(i,j,width))
                else:
                    self.circuit.append("R", c_m(i,j,width))

    def round(self,d):
        width=2*d-1
        height=16
        for j in range(height):
            for i in range(1,2*d-1,2):
                self.circuit.append("RX", c_m(i,j,width))
        self.circuit.append("TICK")
        for j in range(height):
            for i in range(1,2*d-1,2):
                self.circuit.append("CX",[c_m(i,j,width),c_m(i-1,j,width)])
        self.circuit.append("TICK")
        for j in range(height):
            for i in range(1,2*d-1,2):
                self.circuit.append("CX",[c_m(i,j,width),c_m(i+1,j,width)])
        self.circuit.append("TICK")
        for j in range(height):
            for i in range(1,2*d-1,2):
                self.circuit.append("MX", c_m(i,j,width))
                self.measurement_count += 1
        self.circuit.append("TICK")

    def cswap(self,d,a,b):
        ###CSWAP[a,b]
        width=2*d-1
        height=16
        for i in range(0,2*d-1,2):
            self.circuit.append("CX", [c_m(i,a,width),c_m(i,b,width)])
        self.circuit.append("TICK")
        for i in range(0,2*d-1,2):
            self.circuit.append("CX", [c_m(i,b,width),c_m(i,a,width)])
        self.circuit.append("TICK")    

    def swap(self,d,a,b):
        width=2*d-1
        height=16
        ###SWAP[12,11]
        for i in range(0,2*d-1,2):
            self.circuit.append("CX", [c_m(i,a,width),c_m(i,b,width)])
        self.circuit.append("TICK")
        for i in range(0,2*d-1,2):
            self.circuit.append("CX", [c_m(i,b,width),c_m(i,a,width)])
        self.circuit.append("TICK")
        for i in range(0,2*d-1,2):
            self.circuit.append("CX", [c_m(i,a,width),c_m(i,b,width)])
        self.circuit.append("TICK")

    def cnot(self,d,a,b):
        ###CSWAP[a,b]
        width=2*d-1
        height=16
        for i in range(0,2*d-1,2):
            self.circuit.append("CX", [c_m(i,a,width),c_m(i,b,width)])
        self.circuit.append("TICK") 

    def fswap(self,d,a,b):
        width=2*d-1
        height=16
        ###SWAP[12,11]
        for i in range(0,2*d-1,2):
            self.circuit.append("SWAP", [c_m(i,a,width),c_m(i,b,width)])



    def gate(self,d,gate,a):
        width=2*d-1
        height=16
        for i in range(0,2*d-1,2):
            self.circuit.append(gate, c_m(i,a,width))
            if gate == "M" or gate == "MX":  # Count measurement gates
                self.measurement_count += 1



def circ(d,rs):  # d = Z distance, rs = outer code rounds
    circuit=StimCircuit()
    circuit.initialise(d)
    circuit.reset(d)
    for round in range(rs):
        circuit.gate(d,"R",0)
        circuit.round(d)
        circuit.cswap(d,0,1)
        circuit.round(d)
        circuit.swap(d,1,2)
        circuit.round(d)
        circuit.cswap(d,2,3)
        circuit.round(d)
        circuit.swap(d,3,4)
        circuit.round(d)
        circuit.cswap(d,4,5)
        circuit.round(d)
        circuit.cswap(d,5,6)
        if d > 6:
            for i in range(d-6):
                circuit.round(d)
        circuit.gate(d,"M",6)
        if round==0:
            gap_0a=circuit.measurement_count
        if round == 1:
            gap_0b=circuit.measurement_count
            gap_0 = gap_0b-gap_0a
        
        if round==rs-1:
            c1=circuit.measurement_count
        if round == 0:
            circuit.circuit.append("DETECTOR", [stim.target_rec(-1 - i) for i in range(d)])
        else:
            gap_0 = gap_0b-gap_0a  # Define gap_0 explicitly
            circuit.circuit.append("DETECTOR", 
                                   [stim.target_rec(-1 - i) for i in range(d)] + 
                                   [stim.target_rec(-1 - i - gap_0) for i in range(d)]
            )


        circuit.gate(d,"R",6)
        circuit.round(d)
        circuit.cswap(d,6,7)
        circuit.round(d)
        circuit.swap(d,7,8)
        circuit.round(d)
        circuit.swap(d,8,9)
        circuit.round(d)
        circuit.cswap(d,9,10)
        circuit.round(d)
        circuit.swap(d,10,11)
        circuit.round(d)
        circuit.swap(d,11,12)
        circuit.round(d)
        circuit.cswap(d,12,13)
        circuit.round(d)
        circuit.swap(d,13,14)
        circuit.round(d)
        circuit.cnot(d,15,14)
        if d > 9:
            for i in range(d-9):
                circuit.round(d)
        circuit.gate(d,"M",14)  
        if round ==rs-1:
            c2=circuit.measurement_count
        if round == 0:
            circuit.circuit.append("DETECTOR", [stim.target_rec(-1 - i) for i in range(d)])
        else:

            circuit.circuit.append("DETECTOR", 
                                   [stim.target_rec(-1 - i) for i in range(d)] + 
                                   [stim.target_rec(-1 - i - gap_0) for i in range(d)]
            )


        circuit.gate(d,"R",14)
        circuit.round(d)
        circuit.cswap(d,14,13)
        circuit.round(d)
        circuit.swap(d,13,12)
        circuit.round(d)
        circuit.swap(d,12,11)
        circuit.round(d)
        circuit.swap(d,11,10)
        circuit.round(d)
        circuit.cswap(d,10,9)
        circuit.round(d)
        circuit.cswap(d,9,8)
        circuit.round(d)
        circuit.swap(d,8,7)
        circuit.round(d)
        circuit.swap(d,7,6)
        circuit.round(d)
        circuit.cswap(d,6,5)
        if d > 9:
            for i in range(d-9):
                circuit.round(d)
        circuit.gate(d,"M",5) 
        if round ==rs-1:
            c3=circuit.measurement_count
        if round == 0:
            circuit.circuit.append("DETECTOR", [stim.target_rec(-1 - i) for i in range(d)])
        else:

            circuit.circuit.append("DETECTOR", 
                                   [stim.target_rec(-1 - i) for i in range(d)] + 
                                   [stim.target_rec(-1 - i - gap_0) for i in range(d)]
            )

        circuit.gate(d,"R",5)
        circuit.round(d)
        circuit.cnot(d,4,5)
        circuit.round(d)
        circuit.swap(d,5,6)
        circuit.round(d)
        circuit.swap(d,6,7)
        circuit.round(d)
        circuit.swap(d,7,8)
        circuit.round(d)
        circuit.swap(d,8,9)
        circuit.round(d)
        circuit.swap(d,9,10)
        circuit.round(d)
        circuit.cswap(d,10,11)
        circuit.round(d)
        circuit.cswap(d,11,12)
        circuit.round(d)
        circuit.cnot(d,13,12)
        if d > 9:
            for i in range(d-9):
                circuit.round(d)
        circuit.gate(d,"M",12) 
        if round ==rs-1:
            c4=circuit.measurement_count
        if round == 0:
            circuit.circuit.append("DETECTOR", [stim.target_rec(-1 - i) for i in range(d)])
        else:

            circuit.circuit.append("DETECTOR", 
                                   [stim.target_rec(-1 - i) for i in range(d)] + 
                                   [stim.target_rec(-1 - i - gap_0) for i in range(d)]
            )

        circuit.gate(d,"R",12)
        circuit.round(d)
        circuit.cswap(d,12,11)
        circuit.round(d)
        circuit.swap(d,11,10)
        circuit.round(d)
        circuit.swap(d,10,9)
        circuit.round(d)
        circuit.cswap(d,9,8)
        circuit.round(d)
        circuit.cswap(d,8,7)
        circuit.round(d)
        circuit.swap(d,7,6)
        circuit.round(d)
        circuit.swap(d,6,5)
        circuit.round(d)
        circuit.swap(d,5,4)
        circuit.round(d)
        circuit.cswap(d,4,3)
        if d > 9:
            for i in range(d-9):
                circuit.round(d)

        circuit.gate(d,"M",3)
        if round ==rs-1:
            c5=circuit.measurement_count
        if round == 0:
            circuit.circuit.append("DETECTOR", [stim.target_rec(-1 - i) for i in range(d)])
        else:

            circuit.circuit.append("DETECTOR", 
                                   [stim.target_rec(-1 - i) for i in range(d)] + 
                                   [stim.target_rec(-1 - i - gap_0) for i in range(d)]
            )

        circuit.swap(d,3,2)
        circuit.gate(d,"R",2)
        circuit.round(d)
        circuit.cnot(d,1,2)
        circuit.round(d)
        circuit.cswap(d,2,3)
        circuit.round(d)
        circuit.cswap(d,3,4)
        circuit.round(d)
        circuit.swap(d,4,5)
        circuit.round(d)
        circuit.swap(d,5,6)
        circuit.round(d)
        circuit.cnot(d,7,6)
        if d > 6:
            for i in range(d-6):
                circuit.round(d)

        circuit.gate(d,"M",6)
        if round ==rs-1:
            c6=circuit.measurement_count
        if round == 0:
            circuit.circuit.append("DETECTOR", [stim.target_rec(-1 - i) for i in range(d)])
        else:

            circuit.circuit.append("DETECTOR", 
                                   [stim.target_rec(-1 - i) for i in range(d)] + 
                                   [stim.target_rec(-1 - i - gap_0) for i in range(d)]
            )

        if round != rs-1:
            circuit.fswap(d,6,5)
            circuit.fswap(d,5,4)
            circuit.fswap(d,4,3)
            circuit.fswap(d,3,2)
            circuit.fswap(d,2,1)
            circuit.fswap(d,1,0)
        
    for i in range(15):
        circuit.gate(d,"M",i)
    final=circuit.measurement_count
    
    circuit.circuit.append("Detector",[stim.target_rec(-1-i-(final-c1)) for i in range(d)]+
                       [stim.target_rec(-1-14*d-i)for i in range(d)]+
                       [stim.target_rec(-1-12*d-i)for i in range(d)]+
                       [stim.target_rec(-1-10*d-i)for i in range(d)]+
                       [stim.target_rec(-1-9*d-i)for i in range(d)])

    circuit.circuit.append("Detector",[stim.target_rec(-1-i-(final-c2)) for i in range(d)]+
                       [stim.target_rec(-1-8*d-i)for i in range(d)]+
                       [stim.target_rec(-1-5*d-i)for i in range(d)]+
                       [stim.target_rec(-1-2*d-i)for i in range(d)]+
                       [stim.target_rec(-1-0*d-i)for i in range(d)])

    circuit.circuit.append("Detector",[stim.target_rec(-1-i-(final-c3)) for i in range(d)]+
                       [stim.target_rec(-1-9*d-i)for i in range(d)]+
                       [stim.target_rec(-1-6*d-i)for i in range(d)]+
                       [stim.target_rec(-1-5*d-i)for i in range(d)]+
                       [stim.target_rec(-1-1*d-i)for i in range(d)])

    circuit.circuit.append("Detector",[stim.target_rec(-1-i-(final-c4)) for i in range(d)]+
                       [stim.target_rec(-1-10*d-i)for i in range(d)]+
                       [stim.target_rec(-1-4*d-i)for i in range(d)]+
                       [stim.target_rec(-1-3*d-i)for i in range(d)]+
                       [stim.target_rec(-1-2*d-i)for i in range(d)])

    circuit.circuit.append("Detector",[stim.target_rec(-1-i-(final-c5)) for i in range(d)]+
                       [stim.target_rec(-1-11*d-i)for i in range(d)]+
                       [stim.target_rec(-1-7*d-i)for i in range(d)]+
                       [stim.target_rec(-1-6*d-i)for i in range(d)]+
                       [stim.target_rec(-1-3*d-i)for i in range(d)])

    circuit.circuit.append("Detector",[stim.target_rec(-1-i-(final-c6)) for i in range(d)]+
                       [stim.target_rec(-1-13*d-i)for i in range(d)]+
                       [stim.target_rec(-1-12*d-i)for i in range(d)]+
                       [stim.target_rec(-1-11*d-i)for i in range(d)]+
                       [stim.target_rec(-1-8*d-i)for i in range(d)])


    circuit.circuit.append("Observable_Include",
                   [stim.target_rec(-1-14*d-i)for i in range(d)],0)

    circuit.circuit.append("Observable_Include",
                       [stim.target_rec(-1-13*d-i)for i in range(d)],1)

    circuit.circuit.append("Observable_Include",
                       [stim.target_rec(-1-12*d-i)for i in range(d)],2)

    circuit.circuit.append("Observable_Include",
                       [stim.target_rec(-1-11*d-i)for i in range(d)],3)

    circuit.circuit.append("Observable_Include",
                       [stim.target_rec(-1-10*d-i)for i in range(d)],4)

    circuit.circuit.append("Observable_Include",
                       [stim.target_rec(-1-7*d-i)for i in range(d)],5)

    circuit.circuit.append("Observable_Include",
                       [stim.target_rec(-1-6*d-i)for i in range(d)],6)

    circuit.circuit.append("Observable_Include",
                       [stim.target_rec(-1-5*d-i)for i in range(d)],7)

    circuit.circuit.append("Observable_Include",
                       [stim.target_rec(-1-4*d-i)for i in range(d)],8)
    
    return(circuit.circuit)

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



def noisy_circ_advanced(d,rs,p):
    return(AddNoise(circ(d,rs),p))
