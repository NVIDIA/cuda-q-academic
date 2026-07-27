# Nonlocal layers researcher summary

This report is regenerated from this circuit's ledger only.

## Outcome

Round 12 is best at **1.137s**, a **2.62x speedup** over the 2.978s baseline.

Best settings:

- `precision`: `fp32`
- `controlled_rank`: `1`
- `path_reuse`: `False`
- `hyper_samples`: `8`
- `find_threads`: `1`
- `find_limit`: `True`
- `deterministic`: `False`
- `scratch_percentage`: `50`

## Evidence-backed learnings

- Round 2 — **baseline**: Established a 2.978s baseline. Hypothesis: FP32 will complete within 30 seconds and remain within the evaluator's correctness tolerance; otherwise precision alone is insufficient.
- Round 3 — **controlled_rank: 1 -> 2**: Runtime regressed 1.28x, from 2.978s to 3.809s. Hypothesis: Controlled rank 2 will remain correct and lower runtime by at least 5% relative to round 2; a smaller change will be treated as noisy.
- Round 4 — **repeat best settings**: Runtime improved 1.01x, from 2.978s to 2.937s. Hypothesis: Returning to controlled rank 1 will remain correct, beat round 3 by at least 15%, and land within 10% of round 2's 2.978-second runtime.
- Round 5 — **path_reuse: True -> False**: Runtime improved 2.12x, from 2.937s to 1.384s. Hypothesis: Disabling path reuse will remain correct and improve runtime by at least 5% versus round 4; otherwise reuse should remain enabled.
- Round 6 — **path_reuse: False -> True**: Runtime regressed 2.10x, from 1.384s to 2.906s. Hypothesis: Re-enabling path reuse will remain correct but regress above 2.5 seconds, confirming that reuse is harmful under these settings.
- Round 7 — **repeat best settings**: Runtime improved 1.02x, from 1.384s to 1.361s. Hypothesis: Disabling path reuse again will remain correct and reproduce within 10% of round 5's 1.384-second runtime.
- Round 8 — **hyper_samples: 8 -> 1**: Runtime improved 1.07x, from 1.361s to 1.267s. Hypothesis: One hyper sample will remain correct and improve runtime by at least 5% versus round 7; a regression would show that path quality needs sampling.
- Round 9 — **hyper_samples: 1 -> 8**: Runtime regressed 1.01x, from 1.267s to 1.281s. Hypothesis: Eight hyper samples will remain correct but run at least 5% slower than round 8, corroborating the lower sampling budget.
- Round 10 — **hyper_samples: 1 -> 8; find_threads: 10 -> 1**: Runtime improved 1.07x, from 1.267s to 1.183s. Hypothesis: One find thread will remain correct and improve runtime by at least 5% versus round 9; otherwise the thread count is not a useful lever here.
- Round 11 — **find_threads: 1 -> 10**: Runtime regressed 1.17x, from 1.183s to 1.380s. Hypothesis: Ten find threads will remain correct but run at least 5% slower than round 10, corroborating the single-thread result.
- Round 12 — **repeat best settings**: Runtime improved 1.04x, from 1.183s to 1.137s. Hypothesis: One find thread will remain correct and reproduce within 10% of round 10's 1.183-second runtime.
- Round 13 — **hyper_samples: 8 -> 1**: Runtime regressed 1.01x, from 1.137s to 1.144s. Hypothesis: One hyper sample with one find thread will remain correct and improve runtime by at least 5% versus round 12, demonstrating an interaction.
- Round 14 — **hyper_samples: 8 -> 1; find_limit: True -> False**: Runtime regressed 1.03x, from 1.137s to 1.168s. Hypothesis: Disabling find_limit will remain correct but regress runtime by at least 5% versus round 13 because unconstrained search adds overhead.
- Round 15 — **hyper_samples: 8 -> 1**: Runtime regressed 1.01x, from 1.137s to 1.153s. Hypothesis: Re-enabling find_limit will remain correct and reproduce within 5% of round 13's 1.144-second runtime, indicating no material limiter effect.
- Round 16 — **hyper_samples: 8 -> 1; deterministic: False -> True**: Runtime regressed 1.08x, from 1.137s to 1.223s. Hypothesis: Deterministic search will remain correct but regress runtime by at least 5% versus round 15 because it restricts path-search choices.
- Round 17 — **hyper_samples: 8 -> 1**: Runtime regressed 1.07x, from 1.137s to 1.212s. Hypothesis: Non-deterministic search will remain correct and recover to within 5% of round 15's 1.153-second runtime.
- Round 18 — **hyper_samples: 8 -> 1; scratch_percentage: 50 -> 95**: Runtime regressed 1.01x, from 1.137s to 1.151s. Hypothesis: A 95% scratch allowance will remain correct and improve runtime by at least 5% versus round 17 by enabling more efficient contractions.
- Round 19 — **controlled_rank: 1 -> 2; hyper_samples: 8 -> 1; scratch_percentage: 50 -> 95**: Runtime regressed 1.83x, from 1.137s to 2.085s. Hypothesis: Controlled rank 2 will remain correct but regress by at least 15% versus round 18, showing that rank 1 remains preferable without path reuse.
- Round 20 — **hyper_samples: 8 -> 1; scratch_percentage: 50 -> 95**: Runtime regressed 1.07x, from 1.137s to 1.218s. Hypothesis: Controlled rank 1 will remain correct and recover to within 10% of round 18's 1.151-second runtime; no further round is planned.

## Decision trail

| Round | Change | Reasoning | Result | Next-round reasoning |
|---:|---|---|---|---|
| 1 | baseline | Use the fixed FP64 round-one template so every fresh study starts from the same conservative CUDA-Q TensorNet configuration. | timeout at 30.112659s. Evaluation exceeded 30.0s and was discarded as an outlier. | Round 1 timed out after 30.11 seconds with FP64 and produced no valid runtime. Change only precision to FP32 to test whether arithmetic and memory cost, rather than the path-search settings, caused the timeout. |
| 2 | baseline | Round 1 timed out after 30.11 seconds with FP64 and produced no valid runtime. Change only precision to FP32 to test whether arithmetic and memory cost, rather than the path-search settings, caused the timeout. | 2.977698s; keep. Established a 2.978s baseline. | Round 2 established a correct 2.978-second FP32 result. Change only controlled_rank from 1 to 2 to test whether a modestly less restrictive controlled-tensor representation reduces contraction overhead. |
| 3 | controlled_rank: 1 -> 2 | Round 2 established a correct 2.978-second FP32 result. Change only controlled_rank from 1 to 2 to test whether a modestly less restrictive controlled-tensor representation reduces contraction overhead. | 3.808556s; discard. Runtime regressed 1.28x, from 2.978s to 3.809s. | Round 3 at controlled rank 2 regressed 28% to 3.809 seconds. Reverse only that setting to rank 1 to test whether the large regression follows the rank choice rather than transient timing variation. |
| 4 | repeat best settings | Round 3 at controlled rank 2 regressed 28% to 3.809 seconds. Reverse only that setting to rank 1 to test whether the large regression follows the rank choice rather than transient timing variation. | 2.937259s; keep. Runtime improved 1.01x, from 2.978s to 2.937s. | Round 4 recovered to 2.937 seconds at controlled rank 1, supporting rank 1 as the better structural choice. Change only path_reuse to False to test whether reuse bookkeeping adds cost in this single-observation run. |
| 5 | path_reuse: True -> False | Round 4 recovered to 2.937 seconds at controlled rank 1, supporting rank 1 as the better structural choice. Change only path_reuse to False to test whether reuse bookkeeping adds cost in this single-observation run. | 1.384053s; keep. Runtime improved 2.12x, from 2.937s to 1.384s. | Round 5 improved 2.12x to 1.384 seconds when path reuse was disabled. Reverse only path_reuse to True to determine whether this large effect tracks the setting rather than an unusually fast trial. |
| 6 | path_reuse: False -> True | Round 5 improved 2.12x to 1.384 seconds when path reuse was disabled. Reverse only path_reuse to True to determine whether this large effect tracks the setting rather than an unusually fast trial. | 2.905621s; discard. Runtime regressed 2.10x, from 1.384s to 2.906s. | Round 6 regressed to 2.906 seconds when path reuse was restored, confirming the round-5 effect. Change only path_reuse back to False to restore the supported configuration and obtain a second timing at that setting. |
| 7 | repeat best settings | Round 6 regressed to 2.906 seconds when path reuse was restored, confirming the round-5 effect. Change only path_reuse back to False to restore the supported configuration and obtain a second timing at that setting. | 1.361089s; keep. Runtime improved 1.02x, from 1.384s to 1.361s. | Round 7 reproduced the no-reuse result at 1.361 seconds. Change only hyper_samples from 8 to 1 to test whether reducing path-search sampling overhead preserves a sufficiently good contraction path. |
| 8 | hyper_samples: 8 -> 1 | Round 7 reproduced the no-reuse result at 1.361 seconds. Change only hyper_samples from 8 to 1 to test whether reducing path-search sampling overhead preserves a sufficiently good contraction path. | 1.267142s; keep. Runtime improved 1.07x, from 1.361s to 1.267s. | Round 8 improved 7% to 1.267 seconds at one hyper sample, only modestly above the noise threshold. Reverse only hyper_samples to 8 to test whether the gain follows the sample budget. |
| 9 | hyper_samples: 1 -> 8 | Round 8 improved 7% to 1.267 seconds at one hyper sample, only modestly above the noise threshold. Reverse only hyper_samples to 8 to test whether the gain follows the sample budget. | 1.280678s; discard. Runtime regressed 1.01x, from 1.267s to 1.281s. | Round 9 at eight hyper samples was only 1% slower than round 8, so sample count is not a confirmed effect. Change only find_threads from 10 to 1 to test whether path-search thread coordination adds avoidable overhead. |
| 10 | hyper_samples: 1 -> 8; find_threads: 10 -> 1 | Round 9 at eight hyper samples was only 1% slower than round 8, so sample count is not a confirmed effect. Change only find_threads from 10 to 1 to test whether path-search thread coordination adds avoidable overhead. | 1.183357s; keep. Runtime improved 1.07x, from 1.267s to 1.183s. | Round 10 improved about 7.6% versus round 9 when find_threads fell to 1. Reverse only find_threads to 10 to test whether that modest gain follows the thread setting rather than timing variation. |
| 11 | find_threads: 1 -> 10 | Round 10 improved about 7.6% versus round 9 when find_threads fell to 1. Reverse only find_threads to 10 to test whether that modest gain follows the thread setting rather than timing variation. | 1.380329s; discard. Runtime regressed 1.17x, from 1.183s to 1.380s. | Round 11 regressed 17% to 1.380 seconds when ten find threads were restored. Change only find_threads back to 1 to restore the supported setting and verify recovery before interaction tests. |
| 12 | repeat best settings | Round 11 regressed 17% to 1.380 seconds when ten find threads were restored. Change only find_threads back to 1 to restore the supported setting and verify recovery before interaction tests. | 1.136976s; keep. Runtime improved 1.04x, from 1.183s to 1.137s. | Round 12 reproduced the one-thread result at 1.137 seconds. Earlier the hyper-sample effect was noisy with ten threads; change only hyper_samples to 1 to test whether it becomes useful with single-threaded search. |
| 13 | hyper_samples: 8 -> 1 | Round 12 reproduced the one-thread result at 1.137 seconds. Earlier the hyper-sample effect was noisy with ten threads; change only hyper_samples to 1 to test whether it becomes useful with single-threaded search. | 1.143657s; discard. Runtime regressed 1.01x, from 1.137s to 1.144s. | Round 13 was 1% slower at one hyper sample, falsifying a useful sample/thread interaction. Change only find_limit to False to test whether removing the path-search limiter expands work without enough path benefit. |
| 14 | hyper_samples: 8 -> 1; find_limit: True -> False | Round 13 was 1% slower at one hyper sample, falsifying a useful sample/thread interaction. Change only find_limit to False to test whether removing the path-search limiter expands work without enough path benefit. | 1.167793s; discard. Runtime regressed 1.03x, from 1.137s to 1.168s. | Round 14 was only 2.1% slower than round 13 with find_limit disabled, so the predicted meaningful penalty did not occur. Reverse only find_limit to True to classify the small difference as reproducible or noise-scale. |
| 15 | hyper_samples: 8 -> 1 | Round 14 was only 2.1% slower than round 13 with find_limit disabled, so the predicted meaningful penalty did not occur. Reverse only find_limit to True to classify the small difference as reproducible or noise-scale. | 1.153153s; discard. Runtime regressed 1.01x, from 1.137s to 1.153s. | Round 15 reproduced round 13 within 1%, showing no material find_limit effect. Change only deterministic to True to test the runtime cost of constraining contraction-path search reproducibility. |
| 16 | hyper_samples: 8 -> 1; deterministic: False -> True | Round 15 reproduced round 13 within 1%, showing no material find_limit effect. Change only deterministic to True to test the runtime cost of constraining contraction-path search reproducibility. | 1.222600s; discard. Runtime regressed 1.08x, from 1.137s to 1.223s. | Round 16 regressed 6.0% versus round 15 with deterministic search. Reverse only deterministic to False to test whether performance recovers under the otherwise identical proposal. |
| 17 | hyper_samples: 8 -> 1 | Round 16 regressed 6.0% versus round 15 with deterministic search. Reverse only deterministic to False to test whether performance recovers under the otherwise identical proposal. | 1.212216s; discard. Runtime regressed 1.07x, from 1.137s to 1.212s. | Round 17 was only 0.8% faster than deterministic round 16 and failed to recover to round 15, leaving the deterministic effect noisy. Change only scratch_percentage from 50 to 95 to test a larger workspace allowance. |
| 18 | hyper_samples: 8 -> 1; scratch_percentage: 50 -> 95 | Round 17 was only 0.8% faster than deterministic round 16 and failed to recover to round 15, leaving the deterministic effect noisy. Change only scratch_percentage from 50 to 95 to test a larger workspace allowance. | 1.150668s; discard. Runtime regressed 1.01x, from 1.137s to 1.151s. | Round 18 at 95% scratch took 1.151 seconds, essentially identical to round 15's 1.153 seconds at 50%, so scratch has no material effect. Change only controlled_rank to 2 to test its interaction with disabled path reuse. |
| 19 | controlled_rank: 1 -> 2; hyper_samples: 8 -> 1; scratch_percentage: 50 -> 95 | Round 18 at 95% scratch took 1.151 seconds, essentially identical to round 15's 1.153 seconds at 50%, so scratch has no material effect. Change only controlled_rank to 2 to test its interaction with disabled path reuse. | 2.085047s; discard. Runtime regressed 1.83x, from 1.137s to 2.085s. | Round 19 regressed 81% to 2.085 seconds at controlled rank 2 even with path reuse disabled. Reverse only controlled_rank to 1 to confirm recovery before completing the requested 20-round study. |
| 20 | hyper_samples: 8 -> 1; scratch_percentage: 50 -> 95 | Round 19 regressed 81% to 2.085 seconds at controlled rank 2 even with path reuse disabled. Reverse only controlled_rank to 1 to confirm recovery before completing the requested 20-round study. | 1.217698s; discard. Runtime regressed 1.07x, from 1.137s to 1.218s. | pending — the researcher has not selected the next round |

## Researcher interpretation

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
