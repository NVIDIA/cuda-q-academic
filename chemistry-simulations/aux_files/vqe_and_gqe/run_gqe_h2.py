import argparse
import cudaq
import os
import torch
import json
import matplotlib.pyplot as plt
import numpy as np
import cudaq_solvers as solvers
from cudaq import spin
from lightning.fabric.loggers import CSVLogger
from cudaq_solvers.gqe_algorithm.gqe import get_default_config
from typing import List

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Run GQE for LiH/H2.")
parser.add_argument('--mpi', action='store_true', help='Enable MPI distribution.')
parser.add_argument('--max_iters', type=int, default=75, help='Maximum number of GQE iterations.')
parser.add_argument('--ngates', type=int, default=40, help='Number of gates (ansatz depth).')
parser.add_argument('--num_samples', type=int, default=10, help='Number of samples (population size).')
parser.add_argument('--temperature', type=float, default=5.0, help='Temperature for sampling.')
parser.add_argument('--lr', type=float, default=1e-7, help='Learning Rate.')
parser.add_argument('--output_file', type=str, default='gqe_convergence.png', help='Filename to save the convergence plot.')

args = parser.parse_args()

if args.mpi:
    try:
        cudaq.set_target('nvidia', option='mqpu')
        cudaq.mpi.initialize()
    except RuntimeError:
        print('Warning: NVIDIA GPUs or MPI not available. Skipping...')
        exit(0)
else:
    try:
        cudaq.set_target('nvidia', option='fp64')
    except RuntimeError:
        cudaq.set_target('qpp-cpu')

# Deterministic setup
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
torch.manual_seed(3047)
torch.use_deterministic_algorithms(True)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# ---------------------------------------------------------------------------
# 1. Update Geometry and Get FCI
# ---------------------------------------------------------------------------
geometry = [('H', (0., 0., 0.)), ('H', (0., 0., 0.74))]
molecule = solvers.create_molecule(geometry, '6-31g', 0, 0, nele_cas=2, norb_cas=3, casci=True)
spin_ham = molecule.hamiltonian
n_qubits = molecule.n_orbitals * 2
n_electrons = molecule.n_electrons

# Extract FCI Energy (R-CASCI)
energies = molecule.energies
fci_energy = energies['R-CASCI'] if 'R-CASCI' in energies else -0.9886377190903441

# Only print preamble on rank 0
if not args.mpi or cudaq.mpi.rank() == 0:
    print(f"Full CI Energy (R-CASCI): {fci_energy}")
    print(f"Configuration: max_iters={args.max_iters}, ngates={args.ngates}, "
          f"num_samples={args.num_samples}, temperature={args.temperature}")

# ---------------------------------------------------------------------------
# 2. Build Operator Pool
# ---------------------------------------------------------------------------

def get_identity(n_qubits: int) -> cudaq.SpinOperator:
    In = cudaq.spin.i(0)
    for q in range(1, n_qubits):
        In = In * cudaq.spin.i(q)
    return 1.0 * cudaq.SpinOperator(In)

def get_gqe_pauli_pool(num_qubits: int, num_electrons: int, params: List[float]) -> List[cudaq.SpinOperator]:
    uccsd_operators = solvers.get_operator_pool("uccsd", num_qubits=num_qubits, num_electrons=num_electrons)
    pool = [get_identity(num_qubits)]

    individual_terms = []
    for op in uccsd_operators:
        for term in op:
            pauli_word = term.get_pauli_word(num_qubits)
            pauli_op = None
            for qubit_idx, pauli_char in enumerate(pauli_word):
                if pauli_char == 'I': gate = spin.i(qubit_idx)
                elif pauli_char == 'X': gate = spin.x(qubit_idx)
                elif pauli_char == 'Y': gate = spin.y(qubit_idx)
                elif pauli_char == 'Z': gate = spin.z(qubit_idx)
                else: continue
                pauli_op = gate if pauli_op is None else pauli_op * gate

            if pauli_op is not None:
                individual_terms.append(cudaq.SpinOperator(pauli_op))

    for term_op in individual_terms:
        for param in params:
            pool.append(param * term_op)
    return pool

params = [0.003125, -0.003125, 0.00625, -0.00625, 0.0125, -0.0125, 
          0.025, -0.025, 0.05, -0.05, 0.1, -0.1]
op_pool = get_gqe_pauli_pool(n_qubits, n_electrons, params)

def term_coefficients(op): return [term.evaluate_coefficient() for term in op]
def term_words(op): return [term.get_pauli_word(n_qubits) for term in op]

@cudaq.kernel
def kernel(n_qubits: int, n_electrons: int, coeffs: list[float], words: list[cudaq.pauli_word]):
    q = cudaq.qvector(n_qubits)
    for i in range(n_electrons): x(q[i])
    for i in range(len(coeffs)): exp_pauli(coeffs[i], q, words[i])

def cost(sampled_ops, **kwargs):
    full_coeffs = []
    full_words = []
    for op in sampled_ops:
        full_coeffs += [c.real for c in term_coefficients(op)]
        full_words += term_words(op)

    if args.mpi:
        handle = cudaq.observe_async(kernel, spin_ham, n_qubits, n_electrons, full_coeffs, full_words, qpu_id=kwargs['qpu_id'])
        return handle, lambda res: res.get().expectation()
    else:
        return cudaq.observe(kernel, spin_ham, n_qubits, n_electrons, full_coeffs, full_words).expectation()

# ---------------------------------------------------------------------------
# Configure GQE
# ---------------------------------------------------------------------------
cfg = get_default_config()
cfg.use_fabric_logging = False
logger = CSVLogger("gqe_lih_logs/gqe.csv")
cfg.fabric_logger = logger
cfg.save_trajectory = True
cfg.verbose = True
cfg.del_temperature = 0.05
cfg.max_iters = args.max_iters
cfg.ngates = args.ngates
cfg.num_samples = args.num_samples
cfg.temperature = args.temperature
cfg.lr = args.lr

# Run GQE
minE, best_ops = solvers.gqe(cost, op_pool, config=cfg)

# ---------------------------------------------------------------------------
# 3. Process Results & Plot (Rank 0 only)
# ---------------------------------------------------------------------------
if not args.mpi or cudaq.mpi.rank() == 0:
    print(f'Ground Energy = {minE}')    
    print('Ansatz Ops')
    for idx in best_ops: print(op_pool[idx])

    print("\nProcessing trajectory and generating plot...")
    trajectory_file = "gqe_logs/gqe_trajectory.json"
    
    if os.path.exists(trajectory_file):
        try:
            # Switch to Dark Background
            plt.style.use('dark_background')
            
            # Data storage
            iterations = []
            all_energies = [] # List of lists (all samples per epoch)
            losses = [] 
            
            # For finding global min
            global_min_val = float('inf')
            global_min_iter = 0

            with open(trajectory_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            current_iter = entry.get('iter', len(iterations))
                            
                            # Parse Energies (Population)
                            if 'energies' in entry and isinstance(entry['energies'], list) and entry['energies']:
                                epoch_energies = entry['energies']
                                all_energies.append(epoch_energies)
                                
                                # Check for global min in this batch
                                batch_min = min(epoch_energies)
                                if batch_min < global_min_val:
                                    global_min_val = batch_min
                                    global_min_iter = current_iter
                                    
                            elif 'energy' in entry:
                                val = entry['energy']
                                all_energies.append([val])
                                if val < global_min_val:
                                    global_min_val = val
                                    global_min_iter = current_iter
                            else:
                                continue 
                            
                            # Parse Loss
                            losses.append(entry.get('loss', None))
                            iterations.append(current_iter)
                                
                        except json.JSONDecodeError: continue
            
            if all_energies:
                # Setup 2 Subplots sharing X axis
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
                
                nvidia_green = '#76B900'
                bright_red = '#FF4444'
                
                # --- Plot 1: Energy Scatter ---
                # Flatten data for scatter plotting
                scatter_x = []
                scatter_y = []
                for idx, epoch_data in enumerate(all_energies):
                    iter_num = iterations[idx]
                    scatter_x.extend([iter_num] * len(epoch_data))
                    scatter_y.extend(epoch_data)

                ax1.scatter(scatter_x, scatter_y, color=nvidia_green, alpha=0.7, s=15, label='Sampled Energies')
                
                # Plot FCI Line
                ax1.axhline(y=fci_energy, color=bright_red, linestyle='--', linewidth=1.5, 
                            label=f'FCI Energy = {fci_energy:.5f} Ha')
                
                # Circle the Global Minimum
                ax1.plot(global_min_iter, global_min_val, marker='o', markersize=20, 
                         markeredgecolor='white', markerfacecolor='none', markeredgewidth=2, 
                         label='Global Minimum')

                # Annotation: Delta E
                energy_diff = abs(global_min_val - fci_energy)
                ax1.text(0.5, 0.95, f'ΔE (GQE - FCI) = {energy_diff:.2e} Ha', 
                         transform=ax1.transAxes, ha='center', va='top', 
                         fontsize=14, fontweight='bold', color='white',
                         bbox=dict(facecolor='#333333', alpha=0.9, edgecolor='gray', boxstyle='round'))

                # Formatting Plot 1
                ax1.set_ylabel('Energy (Hartree)', fontweight='bold', color='white')
                ax1.set_ylim(bottom=fci_energy - 0.02, top=-0.70) # Fixed range
                ax1.grid(True, which='both', linestyle='--', alpha=0.3, color='gray')
                ax1.legend(loc='upper right', facecolor='#333333', edgecolor='white')
                ax1.set_title(f'GQE Convergence (Gates={args.ngates}, Samples={args.num_samples})', color='white')

                # --- Plot 2: Loss ---
                valid_loss = [(i, l) for i, l in zip(iterations, losses) if l is not None]
                if valid_loss:
                    lx, ly = zip(*valid_loss)
                    # Using White for Loss line to pop against dark background
                    ax2.plot(lx, ly, color='white', marker='x', linestyle='-', linewidth=1, label='Loss')
                
                ax2.set_ylabel('Loss', fontweight='bold', color='white')
                ax2.set_xlabel('Iteration', fontweight='bold', color='white')
                ax2.set_ylim(0, 10) # Fixed range 0 to 10
                ax2.grid(True, which='both', linestyle='--', alpha=0.3, color='gray')
                ax2.legend(loc='upper right', facecolor='#333333', edgecolor='white')

                # Save
                plt.tight_layout()
                output_img = args.output_file
                plt.savefig(output_img, dpi=300, facecolor='black')
                print(f"Plot saved successfully to: {output_img}")
                print(f"Global Minimum: {global_min_val:.6f} at iter {global_min_iter}")
                
            else:
                print("No energy data found.")
                
        except Exception as e:
            print(f"Error plotting: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Error: {trajectory_file} not found.")

if args.mpi:
    cudaq.mpi.finalize()