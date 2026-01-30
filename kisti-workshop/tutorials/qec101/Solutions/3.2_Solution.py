import cudaq
import numpy as np

cudaq.set_target("density-matrix-cpu")

@cudaq.kernel
def zeros():
    reg = cudaq.qvector(2)

@cudaq.kernel
def ones():
    reg = cudaq.qvector(2)
    x(reg)

rho = (.5*np.array(cudaq.get_state(zeros)) + .5*np.array(cudaq.get_state(ones))) 
print("Density Matrix")
print(rho)
rho_squared = rho@rho
print("Density Matrix Squared")
print(rho_squared)
print("Trace of Density Matrix Squared")
print(np.trace(rho_squared))


cudaq.set_target("density-matrix-cpu")

@cudaq.kernel
def bell():
    reg = cudaq.qvector(2)
    
    h(reg[0])
    x.ctrl(reg[0],reg[1])

print("Density Matrix")
print(np.array(cudaq.get_state(bell)))
print("Density Matrix Squared")
print(np.array(cudaq.get_state(bell))@np.array(cudaq.get_state(bell)))
print("Trace of Density Matrix Squared")
print(np.trace(np.array(cudaq.get_state(bell))))

