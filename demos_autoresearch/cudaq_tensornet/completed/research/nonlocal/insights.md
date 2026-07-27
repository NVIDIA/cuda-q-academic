# Nonlocal study insights

The fresh study contains 20 recorded rounds. Round 1's fixed FP64 proposal
timed out after 30.11 seconds. Nineteen subsequent FP32 proposals were valid,
and the best valid observation was round 12 at 1.136976 seconds with
`precision="fp32"`, `controlled_rank=1`, `path_reuse=False`,
`hyper_samples=8`, `find_threads=1`, `find_limit=True`,
`deterministic=False`, and `scratch_percentage=50`.

## Strong findings

- FP32 changed the fixed baseline from a timeout to a correct 2.977698-second
  result under otherwise identical settings (rounds 1–2).
- Disabling path reuse was the largest isolated performance improvement.
  Runtime fell from 2.937259 to 1.384053 seconds (rounds 4–5), returned to
  2.905621 seconds when reuse was re-enabled (round 6), and reproduced at
  1.361089 seconds when disabled again (round 7).
- Controlled rank 1 consistently beat rank 2. With path reuse enabled, rank 2
  regressed from 2.977698 to 3.808556 seconds and rank 1 recovered to 2.937259
  seconds (rounds 2–4). In the later no-reuse context, rank 2 regressed from
  1.150668 to 2.085047 seconds and rank 1 recovered to 1.217698 seconds
  (rounds 18–20).
- One find thread was preferable to ten in the no-reuse, eight-sample context.
  Runtime moved from 1.280678 to 1.183357 seconds, regressed to 1.380329 when
  ten threads were restored, and improved to the 1.136976-second study minimum
  when one thread was restored (rounds 9–12).

## Interaction-dependent findings

- The controlled-rank penalty persisted both with and without path reuse, but
  its observed size differed: about 28% in the reuse-enabled comparison and
  about 81% in the later no-reuse comparison. Because the two contexts also
  differed in other search and scratch settings, the ledger supports a robust
  rank-1 preference but does not isolate which setting enlarged the penalty.
- Reducing hyper samples from eight to one initially improved 1.361089 to
  1.267142 seconds with ten threads, but the reversal to eight samples was only
  1.280678 seconds. With one thread, reducing to one sample slightly regressed
  1.136976 to 1.143657 seconds, so no beneficial sample/thread interaction was
  established.

## Negative results

- `find_limit=False` changed 1.143657 to 1.167793 seconds, and restoring
  `True` produced 1.153153 seconds (rounds 13–15). Both differences were below
  5%, providing no material limiter effect.
- A 95% scratch allowance produced 1.150668 seconds (round 18), essentially
  identical to round 15's 1.153153 seconds at 50% under otherwise matching
  settings. More scratch capacity did not establish a performance benefit.
- Every completed FP32 evaluation passed correctness, with absolute errors
  between approximately 1.5e-9 and 7.7e-9. None of the tested performance
  settings caused an invalid result.

## Weak or noisy evidence

- Deterministic search regressed 1.153153 to 1.222600 seconds, but reversing to
  non-deterministic search only improved to 1.212216 seconds rather than
  recovering the earlier timing. The apparent deterministic penalty was not
  corroborated by reversal.
- Hyper-sample differences were inconsistent and mostly below 5% after
  reversal or interaction testing, so eight samples are retained only because
  they occur in the best valid observed row, not because a strong sample-count
  effect was demonstrated.
- Round 12 improved 4% over round 10 at identical settings (1.136976 versus
  1.183357 seconds), illustrating residual timing variation. The restored
  proposal follows the required best observed row, while small differences
  near that minimum should not be over-interpreted.
