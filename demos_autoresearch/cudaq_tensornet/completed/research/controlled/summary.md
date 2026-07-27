# Controlled gates researcher summary

This report is regenerated from this circuit's ledger only.

## Outcome

Round 9 is best at **0.424s**, a **9.99x speedup** over the 4.232s baseline.

Best settings:

- `precision`: `fp32`
- `controlled_rank`: `4`
- `path_reuse`: `False`
- `hyper_samples`: `8`
- `find_threads`: `10`
- `find_limit`: `True`
- `deterministic`: `False`
- `scratch_percentage`: `50`

## Evidence-backed learnings

- Round 2 — **baseline**: Established a 4.232s baseline. Hypothesis: FP32 will complete within 30 seconds and pass the fixed expectation-value correctness check.
- Round 3 — **controlled_rank: 1 -> 2**: Runtime regressed 1.04x, from 4.232s to 4.421s. Hypothesis: controlled_rank=2 will remain valid and reduce runtime by at least 5% relative to round 2.
- Round 4 — **repeat best settings**: Runtime regressed 1.02x, from 4.232s to 4.335s. Hypothesis: Returning to controlled_rank=1 will remain valid, finish within 5% of round 2's 4.232 seconds, and be faster than round 3.
- Round 5 — **path_reuse: True -> False**: Runtime improved 2.34x, from 4.232s to 1.811s. Hypothesis: path_reuse=False will remain valid but increase runtime by at least 5% relative to round 4.
- Round 6 — **path_reuse: False -> True**: Runtime regressed 2.37x, from 1.811s to 4.293s. Hypothesis: Restoring path_reuse=True will remain valid but take more than 3.5 seconds, substantially slower than round 5.
- Round 7 — **repeat best settings**: Runtime improved 1.01x, from 1.811s to 1.802s. Hypothesis: path_reuse=False will remain valid and complete below 2.2 seconds.
- Round 8 — **controlled_rank: 1 -> 2**: Runtime improved 1.00x, from 1.802s to 1.801s. Hypothesis: controlled_rank=2 will remain valid but will not improve runtime by at least 5% relative to round 7.
- Round 9 — **controlled_rank: 2 -> 4**: Runtime improved 4.25x, from 1.801s to 0.424s. Hypothesis: controlled_rank=4 will remain valid and differ in runtime by at least 10% from round 8.
- Round 10 — **controlled_rank: 4 -> 2**: Runtime regressed 4.36x, from 0.424s to 1.846s. Hypothesis: controlled_rank=2 will remain valid but runtime will return above 1.5 seconds.
- Round 11 — **repeat best settings**: Runtime regressed 1.07x, from 0.424s to 0.454s. Hypothesis: controlled_rank=4 will remain valid and complete below 0.55 seconds.
- Round 12 — **controlled_rank: 4 -> 3**: Runtime regressed 1.05x, from 0.424s to 0.445s. Hypothesis: controlled_rank=3 will remain valid but take more than 1.5 seconds.
- Round 13 — **controlled_rank: 4 -> 3; hyper_samples: 8 -> 1**: Runtime regressed 1.05x, from 0.424s to 0.445s. Hypothesis: hyper_samples=1 will remain valid and reduce runtime by at least 10% relative to round 12.
- Round 14 — **controlled_rank: 4 -> 3; hyper_samples: 8 -> 128**: Runtime regressed 1.05x, from 0.424s to 0.446s. Hypothesis: hyper_samples=128 will remain valid but increase runtime by at least 20% relative to round 13.
- Round 15 — **controlled_rank: 4 -> 3**: Runtime regressed 1.06x, from 0.424s to 0.448s. Hypothesis: hyper_samples=8 will remain valid and finish within 5% of round 12's 0.445-second result.
- Round 16 — **controlled_rank: 4 -> 3; find_threads: 10 -> 1**: Runtime regressed 1.10x, from 0.424s to 0.467s. Hypothesis: find_threads=1 will remain valid and reduce runtime by at least 5% relative to round 15.
- Round 17 — **controlled_rank: 4 -> 3; find_threads: 10 -> 64**: Runtime regressed 1.11x, from 0.424s to 0.469s. Hypothesis: find_threads=64 will remain valid but will not improve by at least 5% relative to round 15's 0.448 seconds.
- Round 18 — **controlled_rank: 4 -> 3**: Runtime regressed 1.09x, from 0.424s to 0.462s. Hypothesis: find_threads=10 will remain valid and finish within 5% of round 15's 0.448-second result.
- Round 19 — **controlled_rank: 4 -> 3; deterministic: False -> True**: Runtime regressed 1.05x, from 0.424s to 0.446s. Hypothesis: deterministic=True will remain valid and change runtime by less than 10% relative to round 18.
- Round 20 — **controlled_rank: 4 -> 3**: Runtime regressed 1.05x, from 0.424s to 0.447s. Hypothesis: deterministic=False will remain valid and finish within 5% of round 18's 0.462-second result.

## Decision trail

| Round | Change | Reasoning | Result | Next-round reasoning |
|---:|---|---|---|---|
| 1 | baseline | Use the fixed FP64 round-one template so every fresh study starts from the same conservative CUDA-Q TensorNet configuration. | timeout at 30.126499s. Evaluation exceeded 30.0s and was discarded as an outlier. | Round 1 timed out above 30 seconds with FP64. Reducing only precision to FP32 should lower tensor memory traffic and arithmetic cost while directly testing whether precision was the main barrier to completion. |
| 2 | baseline | Round 1 timed out above 30 seconds with FP64. Reducing only precision to FP32 should lower tensor memory traffic and arithmetic cost while directly testing whether precision was the main barrier to completion. | 4.231636s; keep. Established a 4.232s baseline. | Round 2 established a correct 4.232-second FP32 result. Changing only controlled_rank from 1 to 2 tests whether a less restrictive treatment of controlled operations reduces contraction overhead on this circuit. |
| 3 | controlled_rank: 1 -> 2 | Round 2 established a correct 4.232-second FP32 result. Changing only controlled_rank from 1 to 2 tests whether a less restrictive treatment of controlled operations reduces contraction overhead on this circuit. | 4.421438s; discard. Runtime regressed 1.04x, from 4.232s to 4.421s. | Round 3 at controlled_rank=2 took 4.421 seconds, only 4.5% slower than round 2 and therefore potentially noisy. Reversing only this setting provides an immediate repeat of the rank-1 configuration. |
| 4 | repeat best settings | Round 3 at controlled_rank=2 took 4.421 seconds, only 4.5% slower than round 2 and therefore potentially noisy. Reversing only this setting provides an immediate repeat of the rank-1 configuration. | 4.334765s; discard. Runtime regressed 1.02x, from 4.232s to 4.335s. | Round 4 repeated the rank-1 configuration in 4.335 seconds, confirming that the small rank difference is not a strong effect. The observable contains multiple terms, so disabling only path reuse tests whether shared contraction planning materially benefits this workload. |
| 5 | path_reuse: True -> False | Round 4 repeated the rank-1 configuration in 4.335 seconds, confirming that the small rank difference is not a strong effect. The observable contains multiple terms, so disabling only path reuse tests whether shared contraction planning materially benefits this workload. | 1.811175s; keep. Runtime improved 2.34x, from 4.232s to 1.811s. | Round 5 unexpectedly improved to 1.811 seconds when path reuse was disabled, a 2.34x gain over the previous best. Reversing only path_reuse tests whether this large structural effect is reproducible. |
| 6 | path_reuse: False -> True | Round 5 unexpectedly improved to 1.811 seconds when path reuse was disabled, a 2.34x gain over the previous best. Reversing only path_reuse tests whether this large structural effect is reproducible. | 4.292782s; discard. Runtime regressed 2.37x, from 1.811s to 4.293s. | Round 6 took 4.293 seconds after path reuse was restored, reproducing a large penalty relative to round 5. Disabling only path reuse again tests whether the fast configuration itself repeats. |
| 7 | repeat best settings | Round 6 took 4.293 seconds after path reuse was restored, reproducing a large penalty relative to round 5. Disabling only path reuse again tests whether the fast configuration itself repeats. | 1.802030s; keep. Runtime improved 1.01x, from 1.811s to 1.802s. | Round 7 repeated the path_reuse=False result at 1.802 seconds. Testing controlled_rank=2 in this faster regime distinguishes whether the earlier weak rank result changes when path reuse is disabled. |
| 8 | controlled_rank: 1 -> 2 | Round 7 repeated the path_reuse=False result at 1.802 seconds. Testing controlled_rank=2 in this faster regime distinguishes whether the earlier weak rank result changes when path reuse is disabled. | 1.800706s; keep. Runtime improved 1.00x, from 1.802s to 1.801s. | Round 8 at controlled_rank=2 was effectively unchanged at 1.801 seconds. Because this circuit uses gates with three controls, increasing only the rank threshold to 4 tests a more structurally distinct tensor treatment. |
| 9 | controlled_rank: 2 -> 4 | Round 8 at controlled_rank=2 was effectively unchanged at 1.801 seconds. Because this circuit uses gates with three controls, increasing only the rank threshold to 4 tests a more structurally distinct tensor treatment. | 0.423730s; keep. Runtime improved 4.25x, from 1.801s to 0.424s. | Round 9 improved 4.25x to 0.424 seconds at controlled_rank=4. Reversing only the rank to 2 tests whether that unexpectedly large structural speedup is causal and reproducible. |
| 10 | controlled_rank: 4 -> 2 | Round 9 improved 4.25x to 0.424 seconds at controlled_rank=4. Reversing only the rank to 2 tests whether that unexpectedly large structural speedup is causal and reproducible. | 1.846291s; discard. Runtime regressed 4.36x, from 0.424s to 1.846s. | Round 10 regressed to 1.846 seconds after rank was lowered to 2, strongly supporting a causal threshold effect. Restoring only controlled_rank=4 tests whether the fast side of the effect repeats. |
| 11 | repeat best settings | Round 10 regressed to 1.846 seconds after rank was lowered to 2, strongly supporting a causal threshold effect. Restoring only controlled_rank=4 tests whether the fast side of the effect repeats. | 0.453777s; discard. Runtime regressed 1.07x, from 0.424s to 0.454s. | Round 11 repeated the rank-4 fast regime at 0.454 seconds. Testing only controlled_rank=3 now locates whether the sharp improvement begins exactly at rank 4 for the circuit's three-control gates. |
| 12 | controlled_rank: 4 -> 3 | Round 11 repeated the rank-4 fast regime at 0.454 seconds. Testing only controlled_rank=3 now locates whether the sharp improvement begins exactly at rank 4 for the circuit's three-control gates. | 0.444942s; discard. Runtime regressed 1.05x, from 0.424s to 0.445s. | Round 12 showed rank 3 is also fast at 0.445 seconds, so the boundary is below rank 4. With contraction work now small, lowering only path-search hyper_samples from 8 to 1 tests whether sampling overhead is material. |
| 13 | controlled_rank: 4 -> 3; hyper_samples: 8 -> 1 | Round 12 showed rank 3 is also fast at 0.445 seconds, so the boundary is below rank 4. With contraction work now small, lowering only path-search hyper_samples from 8 to 1 tests whether sampling overhead is material. | 0.445461s; discard. Runtime regressed 1.05x, from 0.424s to 0.445s. | Round 13 at one hyper-sample remained at 0.445 seconds, showing no detectable gain over eight samples. Raising only hyper_samples to 128 is a high-contrast test of whether search sampling affects this fast regime. |
| 14 | controlled_rank: 4 -> 3; hyper_samples: 8 -> 128 | Round 13 at one hyper-sample remained at 0.445 seconds, showing no detectable gain over eight samples. Raising only hyper_samples to 128 is a high-contrast test of whether search sampling affects this fast regime. | 0.446201s; discard. Runtime regressed 1.05x, from 0.424s to 0.446s. | Round 14 at 128 hyper-samples was still 0.446 seconds, falsifying a material sampling-cost effect across the tested range. Restoring only hyper_samples=8 provides a repeat of the rank-3 reference configuration. |
| 15 | controlled_rank: 4 -> 3 | Round 14 at 128 hyper-samples was still 0.446 seconds, falsifying a material sampling-cost effect across the tested range. Restoring only hyper_samples=8 provides a repeat of the rank-3 reference configuration. | 0.448110s; discard. Runtime regressed 1.06x, from 0.424s to 0.448s. | Round 15 repeated the rank-3 reference at 0.448 seconds and confirmed hyper-sample insensitivity. Reducing only find_threads from 10 to 1 tests whether thread-management overhead matters for this short path search. |
| 16 | controlled_rank: 4 -> 3; find_threads: 10 -> 1 | Round 15 repeated the rank-3 reference at 0.448 seconds and confirmed hyper-sample insensitivity. Reducing only find_threads from 10 to 1 tests whether thread-management overhead matters for this short path search. | 0.467193s; discard. Runtime regressed 1.10x, from 0.424s to 0.467s. | Round 16 at one find thread took 0.467 seconds, only 4.3% slower than the 10-thread round and within the noisy band. Raising only find_threads to 64 is a high-contrast test for a meaningful thread-count effect. |
| 17 | controlled_rank: 4 -> 3; find_threads: 10 -> 64 | Round 16 at one find thread took 0.467 seconds, only 4.3% slower than the 10-thread round and within the noisy band. Raising only find_threads to 64 is a high-contrast test for a meaningful thread-count effect. | 0.469472s; discard. Runtime regressed 1.11x, from 0.424s to 0.469s. | Round 17 at 64 threads took 0.469 seconds and did not improve on the 10-thread reference; both tested extremes were slightly slower. Restoring only find_threads=10 provides a direct repeat before the final control. |
| 18 | controlled_rank: 4 -> 3 | Round 17 at 64 threads took 0.469 seconds and did not improve on the 10-thread reference; both tested extremes were slightly slower. Restoring only find_threads=10 provides a direct repeat before the final control. | 0.461904s; discard. Runtime regressed 1.09x, from 0.424s to 0.462s. | Round 18 returned to 0.462 seconds at 10 threads, within the noisy band of the earlier reference. Changing only deterministic mode tests whether fixed path selection materially affects the fast rank-3 configuration. |
| 19 | controlled_rank: 4 -> 3; deterministic: False -> True | Round 18 returned to 0.462 seconds at 10 threads, within the noisy band of the earlier reference. Changing only deterministic mode tests whether fixed path selection materially affects the fast rank-3 configuration. | 0.445824s; discard. Runtime regressed 1.05x, from 0.424s to 0.446s. | Round 19 with deterministic search took 0.446 seconds, only 3.5% faster than round 18 and within the noisy band. Reversing only deterministic mode provides the final repeat of the rank-3 reference. |
| 20 | controlled_rank: 4 -> 3 | Round 19 with deterministic search took 0.446 seconds, only 3.5% faster than round 18 and within the noisy band. Reversing only deterministic mode provides the final repeat of the rank-3 reference. | 0.447012s; discard. Runtime regressed 1.05x, from 0.424s to 0.447s. | pending — the researcher has not selected the next round |

## Researcher interpretation

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
