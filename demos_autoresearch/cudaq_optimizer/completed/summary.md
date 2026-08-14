# CUDA-Q depth-15 QAOA observe-budgeted optimizer autoresearch

Each round receives the same seeded depth-fifteen starting point and a hard budget of 300 counted observes. Energy differences within 1e-6 use convergence/early completion and elapsed time as tie-breakers.

| Case | Rounds | Winning optimizer | Lowest energy | Elapsed s | Converged |
| --- | ---: | --- | ---: | ---: | --- |
| qaoa_depth15 | 20 | 10D Powell 180 + modes 5-6 residual 48 + COBYLA 0.25 | -5.714191035 | 17.963 | no |

See `lowest_energy_by_round.png`, `energy_trajectories_3d.png`, and `energy_trajectories_3d.html` for study visualizations.
