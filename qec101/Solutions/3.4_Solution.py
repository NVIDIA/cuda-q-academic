import cudaq
import numpy as np

cudaq.set_target("nvidia")

def get_noisy_data(e_type =[], gate=[] , qubit=[], prob=[], shots=-1, trajectories=None):

    noise = cudaq.NoiseModel()

    for x in range(len(e_type)):
        
        if e_type[x] == 0:
            noise.add_channel(gate[x], [qubit[x]], cudaq.BitFlipChannel(prob[x]))

        if e_type[x] == 1:
            noise.add_channel(gate[x], [qubit[x]], cudaq.PhaseFlipChannel(prob[x]))

        if e_type[x] == 2:
            noise.add_channel(gate[x], [qubit[x]], cudaq.AmplitudeDampingChannel(prob[x]))

        if e_type[x] == 3:
            noise.add_channel(gate[x], [qubit[x]], cudaq.DepolarizationChannel(prob[x]))
            
    data =[]
    
    for x in range(40):
        data.append(cudaq.observe(uccsd, molecule.hamiltonian, shots_count=shots, noise_model=noise, num_trajectories=trajectories).expectation())

    normalized_data = [x - noiseless for x in data]
    return normalized_data


"""
Place these data sets int he notebook to see the plotted result


data = [
    get_noisy_data([0]*4, ['x']*4, [0,1,2,3], [0.01]*4, trajectories=10),
    get_noisy_data([0]*4, ['x']*4, [0,1,2,3], [0.01]*4, trajectories=100),
    get_noisy_data([0]*4, ['x']*4, [0,1,2,3], [0.01]*4, trajectories=1000),
    get_noisy_data([0]*4, ['x']*4, [0,1,2,3], [0.01]*4, trajectories=10000),
]

categories = ['10', '100', '1000', '10000']

plot_data([data], categories)


The bitflip errors seems to systematically overestimate the eenergy result.  In the first case with only 10 trajectories sampled, an error of 0 is within the confidence interval so this conclusion cannot be drawn with certainty.  As the number of trajectories increaces, the variability in results becomes very small.


datax = [get_noisy_data([0]*4,['x']*4,[0,1,2,3],[.1,.1,.1,.1]),
        get_noisy_data([0]*4,['x']*4,[0,1,2,3],[.01,.01,.01,.01]),
        get_noisy_data([0]*4,['x']*4,[0,1,2,3],[.001,.001,.001,.001]),
        get_noisy_data([0]*4,['x']*4,[0,1,2,3],[.0001,.0001,.0001,.0001]),
]

datah = [get_noisy_data([0]*4,['h']*4,[0,1,2,3],[.1,.1,.1,.1]),
        get_noisy_data([0]*4,['h']*4,[0,1,2,3],[.01,.01,.01,.01]),
        get_noisy_data([0]*4,['h']*4,[0,1,2,3],[.001,.001,.001,.001]),
        get_noisy_data([0]*4,['h']*4,[0,1,2,3],[.0001,.0001,.0001,.0001]),
]

categories = ['p=.1','p=.01', 'p=.001', 'p=.0001' ] 

plot_data([datax,datah], categories, labels=['errors on x gate', 'errors on h gate'])

Bitflip errors seem to be more problematic when they occur on Hadamard gates rather than X gates and the difference is more pronounced at high error rates.


datax = [get_noisy_data([0]*4,['x']*4,[0,1,2,3],[.1]*4),
         get_noisy_data([1]*4,['x']*4,[0,1,2,3],[.1]*4),
         get_noisy_data([2]*4,['x']*4,[0,1,2,3],[.1]*4),
         get_noisy_data([3]*4,['x']*4,[0,1,2,3],[.1]*4)]

datah = [get_noisy_data([0]*4,['h']*4,[0,1,2,3],[.1]*4),
         get_noisy_data([1]*4,['h']*4,[0,1,2,3],[.1]*4),
         get_noisy_data([2]*4,['h']*4,[0,1,2,3],[.1]*4),
         get_noisy_data([3]*4,['h']*4,[0,1,2,3],[.1]*4)]


categories = ['bitflip','phaseflip', 'amplitude damping', 'depolarization'] 

plot_data([datax,datah], categories, labels=['errors on x gate', 'errors on h gate'])

Depolarization errors on Hadamard gates are the most problematic while phaseflip errors seem to have no impact to the predicted energy when they occur on X gates.




data = [get_noisy_data([2]*4,['x']*4,[0,1,2,3],[.1,0,0,0]),
         get_noisy_data([2]*4,['x']*4,[0,1,2,3],[0,.1,0,0]),
         get_noisy_data([2]*4,['x']*4,[0,1,2,3],[0,0,.1,0]),
         get_noisy_data([2]*4,['x']*4,[0,1,2,3],[0,0,0,.1])]

datap = [get_noisy_data([2]*4,['h']*4,[0,1,2,3],[.1,0,0,0]),
         get_noisy_data([2]*4,['h']*4,[0,1,2,3],[0,.1,0,0]),
         get_noisy_data([2]*4,['h']*4,[0,1,2,3],[0,0,.1,0]),
         get_noisy_data([2]*4,['h']*4,[0,1,2,3],[0,0,0,.1])]



categories = ['q0','q1', 'q2', 'q3'] 

plot_data([data,datap], categories, labels=['errors on x gate', 'errors on h gate'])


Amplitude damping errors seem to have less impact when they ocure on q2 or q3, thus, if qubit A is prone to these errors, it should map to q2 or q3. 
"""



    