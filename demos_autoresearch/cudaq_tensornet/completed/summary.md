# Two independent exact-tensornet searches

Each researcher optimizes one fixed circuit and sees only its own ledger. GPU evaluations are serialized for comparable timing.

| Circuit | Rounds | Baseline | Best | Speedup | Detailed summary |
|---|---:|---:|---:|---:|---|
| Nonlocal layers | 20 | 2.978s | 1.137s | 2.62x | [open](research/nonlocal/summary.md) |
| Controlled gates | 20 | 4.232s | 0.424s | 9.99x | [open](research/controlled/summary.md) |

## Final best settings

| Setting | Nonlocal | Controlled gates |
|---|---:|---:|
| `precision` | `fp32` | `fp32` |
| `controlled_rank` | `1` | `4` |
| `path_reuse` | `False` | `False` |
| `hyper_samples` | `8` | `8` |
| `find_threads` | `1` | `10` |
| `find_limit` | `True` | `True` |
| `deterministic` | `False` | `False` |
| `scratch_percentage` | `50` | `50` |
| Best runtime | `1.137s` | `0.424s` |
| Best round | `12` | `9` |

## Why path reuse can be slower

CUDA-Q reuses the contraction **path** (the planned order), not previously contracted intermediate tensors. Its reuse implementation prepares one all-qubit operator topology and executes it for each Pauli term. That saves repeated path finding, but it prevents term-specific light-cone simplification for sparse observables.

The nonlocal observable has only one Pauli-product term, so there is no second term over which to amortize reuse. The controlled observable has six sparse one-qubit Z terms; each can benefit from a small, term-specific causal cone. In both cases the lost simplification and reuse machinery cost more than the path-finding work saved.

## Nonlocal layers: researcher interpretation

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

## Controlled gates: researcher interpretation

## Best observed configuration

Round 9 was the fastest valid observation at **0.423730 s**:

```python
{
    "precision": "fp32",
    "controlled_rank": 4,
    "path_reuse": False,
    "hyper_samples": 8,
    "find_threads": 10,
    "find_limit": True,
    "deterministic": False,
    "scratch_percentage": 50,
}
```

This was 9.99x faster than the first valid FP32 result in round 2
(4.231636 s). The fixed FP64 round 1 timed out above 30 seconds, so the best
result was also more than 70x faster than that timeout threshold.

## Strong findings

- **FP32 was required for a valid result in the tested baseline
  configuration.** The fixed FP64 proposal timed out, while changing only
  precision to FP32 completed correctly in 4.231636 s.
- **Disabling path reuse was a large, repeatable improvement at
  `controlled_rank=1`.** The no-reuse runs took 1.811175 s and 1.802030 s.
  Restoring reuse between them took 4.292782 s, a 2.37x regression, while the
  earlier reuse-enabled FP32 runs were also consistently above 4.2 s.
- **The controlled-rank boundary was another large, repeatable effect with
  path reuse disabled.** Ranks 1 and 2 took about 1.80--1.85 s. Rank 4 took
  0.423730 s and 0.453777 s; reversing to rank 2 took 1.846291 s. Rank 3 was
  also consistently fast at roughly 0.445--0.462 s.

## Interaction-dependent findings

- The sharp controlled-rank improvement was established only with
  `path_reuse=False`. With reuse enabled, changing rank 1 to 2 changed
  4.334765 s to 4.421438 s, which is too small to distinguish from noise.
- Rank 3 clearly crossed into the fast regime, but the study does not establish
  that rank 4 is intrinsically faster than rank 3. The best single result used
  rank 4, while later rank-3 and rank-4 timings occupied a similar
  0.424--0.462 s band.

## Negative results

- At rank 3, changing `hyper_samples` across 1, 8, and 128 produced
  0.445461 s, 0.448110 s, and 0.446201 s representative results. The predicted
  sampling-overhead effects did not appear.
- `deterministic=True` took 0.445824 s versus neighboring false-mode results of
  0.461904 s and 0.447012 s. There is no evidence of a material deterministic
  mode penalty.
- Neither one nor 64 path-finding threads improved on 10 threads. Their
  0.467193 s and 0.469472 s results were modestly slower.

## Weak or noisy evidence

- Differences around 5% among the fast 0.42--0.47 s runs should be treated as
  timing variability. In particular, the isolated 0.423730 s minimum does not
  prove a stable rank-4 advantage over rank 3.
- The thread-count differences were at or below roughly 5% relative to nearby
  10-thread results, so they are weak evidence rather than a reliable tuning
  effect.
- `find_limit` and `scratch_percentage` were not varied, so this study supports
  no conclusion about them.
