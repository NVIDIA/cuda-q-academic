# QAOA depth-15 optimizer autoresearch insights

## Outcome

Round 19 was the winning valid round. Its optimizer combined a 180-call
Powell search in ten low-frequency layer-mode coefficients, a 48-call
bidirectional residual search over cosine modes 5 and 6, and full-space COBYLA
polishing with `rhobeg=0.25`. It observed a lowest energy of
`-5.7141910348634983` at the 300-call cap. The optimizer did not converge, but
it did not reach the time cap and is the winner because energy is the primary
criterion.

Relative to the round-1 COBYLA baseline energy of
`-5.4467026331080071`, the winner lowered energy by
`0.2674884017554912`. The ledger's exact-error measure fell from
`0.35029736689199265` in round 1 to `0.08280896513650138` in round 19.

## Winning mechanism

The successful trajectory developed in three stages:

1. Smooth layer-correlated structure replaced unrestricted local search.
   Round 6's five-mode pattern search reached `-5.6295843246899535` in 165
   calls, outperforming the near-cap SPSA-Adam result in round 5.
2. Continuous joint optimization of those ten gamma/beta mode coefficients
   was more effective than fixed-radius polling. Powell improved energy to
   `-5.6781517593401682` in round 10, and additional Powell allowance produced
   smaller gains in rounds 11 and 13.
3. Medium-frequency residual modes and broader local polishing supplied the
   final gains. Adding modes 5 and 6 produced `-5.6877750169297148` in round
   14; a sixth fine residual sweep produced `-5.7121058506678075` in round 15;
   increasing COBYLA's radius from `0.20` to `0.25` produced the winning
   `-5.7141910348634983` in round 19.

This supports a multiresolution interpretation: first locate a basin in a
smooth low-dimensional schedule space, then admit selected medium-frequency
corrections, and finally polish all 30 parameters.

## Explorer and Improver contributions

Explorer supplied the major optimizer-family advances. Round 2 introduced the
SPSA-Adam plus COBYLA hybrid; round 6 introduced the low-frequency layer-mode
geometry; round 10 replaced fixed mode polling with continuous Powell search;
and round 14 added the useful modes-5-and-6 residual phase. These four rounds
all established new study leaders. Explorer's alternative families also
provided negative evidence: random orthogonal subspaces, layer-pair quadratic
models, full-covariance evolution, one-shot diagonal Newton, joint 14D
Nelder-Mead, and bounded 14D L-BFGS-B did not beat their incumbents.

Improver converted promising mechanisms into later leaders. Extending
SPSA-Adam produced the large round-3 gain and the smaller round-5 gain.
Changing the five-mode COBYLA radius from `0.35` to `0.20` made round 9 a new
leader. Increasing Powell allowance produced the round-11 and round-13
leaders. Extending the residual schedule produced the strong round-15
call-capped leader, and increasing the final COBYLA radius to `0.25` produced
the winning round 19.

## Convergence and budget-cap behavior

Rounds 1 through 14 all converged, with call counts ranging from 74 to 296.
The early baseline converged quickly but at poor energy. Several later
converged rounds used the budget more effectively, particularly rounds 10,
11, and 13, whose Powell hybrids improved energy while finishing at calls 165,
199, and 219.

The best energy results ultimately became budget-bound. Rounds 15, 16, 19,
and 20 reached call 300 without convergence. Rounds 15 and 19 were new
leaders; rounds 16 and 20 were not. Thus call-cap status alone was neither
good nor bad, but the two strongest energies came from productive COBYLA
trajectories that were still active at the boundary. Round 17 shows the
opposite tradeoff: reducing `rhobeg` to `0.12` caused convergence at call 268
but regressed to `-5.6930281124034572`.

## Useful mechanisms, reversals, and failures

Useful mechanisms were seeded low-dimensional structure, continuous Powell
line search in the ten smooth mode coefficients, selective release of modes 5
and 6, and a full-space COBYLA finish. Additional budget helped when it was
allocated to a mechanism that had already shown positive evidence, although
the gains diminished as Powell grew from 120 to 160 to 180 calls.

Several extensions were wasteful or harmful:

- Two extra fine sweeps of the original five-mode pattern search regressed
  from round 6 to round 7.
- Random orthogonal search in round 4 and layer-pair quadratic models in round
  8 were worse than the structured incumbents.
- The full-covariance evolution strategy in round 12 was much less
  call-efficient than Powell.
- The diagonal-Newton finish in round 16 spent most of its allowance on a
  single gradient model and regressed relative to adaptive COBYLA.
- The 14D Nelder-Mead basin search in round 18 and bounded L-BFGS-B finish in
  round 20 did not exploit their larger joint spaces efficiently within the
  fixed budget.

Important reversals prevented simple monotone conclusions. More fine
five-mode polling hurt in round 7, while one additional modes-5-and-6 sweep
helped strongly in round 15. A smaller COBYLA radius helped when moving from
`0.35` to `0.20` in round 9, but shrinking further to `0.12` hurt in round 17;
increasing from `0.20` to `0.25` then produced the final winner.

## Evidence strength and boundary sensitivity

The evidence is strongest for the broad design sequence because several
successive ledger rows support it: structured modes beat unstructured
alternatives, Powell beat fixed polling in the same basis, and selected
medium-frequency residuals improved the Powell basin. Evidence for exact
hyperparameters is weaker because each configuration was evaluated once from
the fixed deterministic start.

The final comparison is sensitive to the 300-observe boundary. Round 19 beat
round 15 by only `0.0020851841956908`, and both were still non-converged at
call 300. The ledger cannot establish whether either trajectory would retain
its advantage with more calls, whether round 19's gain occurred unusually
near the boundary, or whether a converged configuration would win under a
different budget. The selected source is therefore the correct winner for
this protocol, but its exact margin should not be generalized beyond the
fixed 300-call study.
