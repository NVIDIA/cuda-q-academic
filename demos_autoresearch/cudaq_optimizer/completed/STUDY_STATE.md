# Study state: complete

- Case: `qaoa_depth15`
- Graph: workshop weighted N=6 `small` graph
- QAOA layers: 15
- Parameters: 30 (`gamma[0:15]`, then `beta[0:15]`)
- Rounds: 20
- Scientific budget per round: 300 counted observes, including the fixed start
- Secondary evaluator time guard: 120 seconds
- Subprocess safety timeout: 135 seconds
- Convergence tolerance: `1e-6`
- Convergence patience: 3 accepted iterations
- Minimum accepted optimizer iterations: 5
- Close-energy tie tolerance: `1e-6`
- Score: lowest completed energy, with convergence/early-finish tie-breaks
- Exact weighted Max-Cut energy: `-5.797` (diagnostic only)
- Simulator: CUDA-Q `nvidia` target with `fp64`
- Round-one optimizer: COBYLA (`rhobeg=1.0`, `tol=1e-7`, `catol=0.0`)
- Proposal roles: Explorer on even rounds; Improver on odd rounds
- Recorded rounds: 20
- Winning round: 19
- Winning energy: `-5.7141910348634983`
- Runtime ledgers and generated deliverables: present

Call-capped non-converged rounds remain valid. The evaluator never begins call
301 and preserves the best energy among completed calls.
