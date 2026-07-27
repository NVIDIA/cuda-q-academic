# Controlled-circuit findings

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
