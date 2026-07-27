# QLDPC Autoresearch Notes

Use this file as the run log. For each iteration, record:

- hypothesis
- exact decoder change
- command run
- five-dataset result summary
- worst-case dataset
- next idea

## Iteration 1

- Hypothesis: the supplied min-sum + OSD-0 FP32 baseline with scale factor 0.75 provides a valid accuracy/runtime reference for later exploration.
- Exact decoder change: none; evaluated the starting configuration (`MAX_ITERATIONS=30`, `BP_METHOD=1`, `USE_OSD=True`, `OSD_METHOD=1`, `OSD_ORDER=0`, `ITER_PER_CHECK=5`, `SCALE_FACTOR=0.75`, `PROC_FLOAT="fp32"`).
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0004, 0.0081, 0.0284, 0.0531, 0.0806`; decode seconds `3.421, 4.649, 6.732, 9.528, 12.162`; worst-case LER `0.0806`; slowest decode `12.162s`, under the `30s` cap.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: isolate numerical precision by switching from FP32 to FP64 with all other settings fixed.

## Iteration 2

- Hypothesis: FP64 may alter convergence enough to lower worst-case LER while retaining sufficient runtime headroom.
- Exact decoder change: `PROC_FLOAT="fp32" -> "fp64"`; all other settings unchanged.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: failed the round time cap; first four LERs were `0.0004, 0.0081, 0.0284, 0.0530`, but the largest dataset timed out at `30.340s` and received LER `1.0`; whole round invalid for comparison.
- Worst-case dataset: `osd_504_3745_0.005` (`decode_timeout`).
- Next idea: restore FP32, omit `scale_factor`, and test the decoder's default min-sum scaling behavior.

## Iteration 3

- Hypothesis: the decoder's default min-sum scale may improve convergence accuracy over fixed `0.75` without giving up FP32 runtime headroom.
- Exact decoder change: `PROC_FLOAT="fp64" -> "fp32"` and `SCALE_FACTOR=0.75 -> None`; this coherent candidate restores viable precision while selecting default scaling.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0005, 0.0069, 0.0295, 0.0525, 0.0807`; decode seconds `3.414, 4.757, 6.845, 9.714, 12.092`; worst-case LER `0.0807`; slowest decode `12.092s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: test a meaningfully lower fixed scale (`0.625`) rather than fine-grained adjustment.

## Iteration 4

- Hypothesis: stronger min-sum damping at `0.625` may reduce overconfident loopy messages and lower the largest-code LER.
- Exact decoder change: `SCALE_FACTOR=None -> 0.625`; all other settings unchanged.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0003, 0.0117, 0.0335, 0.0618, 0.0887`; decode seconds `3.655, 5.040, 7.661, 10.451, 13.147`; worst-case LER `0.0887`; slowest decode `13.147s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: stop lower-scale refinement and explore sum-product BP.

## Iteration 5

- Hypothesis: sum-product BP may represent probabilities more accurately than min-sum and lower the worst-case LER within the available FP32 time headroom.
- Exact decoder change: `BP_METHOD=1 -> 0` and `SCALE_FACTOR=0.625 -> None` because scale is a min-sum knob; all other settings unchanged.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0003, 0.0081, 0.0241, 0.0475, 0.0635`; decode seconds `3.245, 4.075, 5.910, 7.883, 10.536`; new best worst-case LER `0.0635`; slowest decode `10.536s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: use runtime headroom to test 40 BP iterations in the promising sum-product family.

## Iteration 6

- Hypothesis: sum-product is accuracy- and runtime-promising, so 40 iterations may solve more hard syndromes while remaining well below the cap.
- Exact decoder change: `MAX_ITERATIONS=30 -> 40`; all other settings unchanged.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0004, 0.0078, 0.0245, 0.0456, 0.0635`; decode seconds `3.433, 4.352, 6.496, 8.846, 11.645`; worst-case LER tied at `0.0635`; slowest decode `11.645s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: make one broader iteration-budget check at 60 to see whether the largest code is plateaued.

## Iteration 7

- Hypothesis: 60 sum-product iterations may resolve additional hard largest-code syndromes; the 40-iteration timing leaves substantial cap headroom.
- Exact decoder change: `MAX_ITERATIONS=40 -> 60`; all other settings unchanged.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0006, 0.0077, 0.0244, 0.0427, 0.0605`; decode seconds `3.558, 5.166, 7.512, 10.507, 13.680`; new best worst-case LER `0.0605`; slowest decode `13.680s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: continue the productive iteration-budget refinement at 80 iterations.

## Iteration 8

- Hypothesis: the material 40-to-60 iteration improvement indicates that 80 sum-product iterations may further lower large-code LER while remaining under the cap.
- Exact decoder change: `MAX_ITERATIONS=60 -> 80`; all other settings unchanged.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0003, 0.0084, 0.0228, 0.0437, 0.0618`; decode seconds `3.593, 5.217, 8.659, 11.967, 16.234`; worst-case LER regressed to `0.0618`; slowest decode `16.234s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: return to the 60-iteration best and explore combination-sweep OSD.

## Iteration 9

- Hypothesis: combination-sweep OSD order 2 may correct additional nonconverged sum-product cases and beat OSD-0 while staying under the cap.
- Exact decoder change: `MAX_ITERATIONS=80 -> 60`, `OSD_METHOD=1 -> 3`, and `OSD_ORDER=0 -> 2`; the iteration reversion restores the best BP regime while the coupled OSD settings define the candidate.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0000, 0.0040, 0.0126, 0.0239, 0.0342`; decode seconds `3.518, 5.245, 8.824, 13.540, 20.541`; new best worst-case LER `0.0342`; slowest decode `20.541s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: cautiously increase combination-sweep OSD order from 2 to 3 given the large accuracy gain and remaining headroom.

## Iteration 10

- Hypothesis: OSD combination order 3 may lower the remaining nonconverged-case LER while preserving the 30-second cap.
- Exact decoder change: `OSD_ORDER=2 -> 3`; all other settings unchanged.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0000, 0.0040, 0.0127, 0.0240, 0.0343`; decode seconds `3.423, 5.333, 9.205, 14.061, 20.676`; worst-case LER `0.0343`; slowest decode `20.676s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: stop combination-order refinement and test exhaustive OSD at small order 3.

## Iteration 11

- Hypothesis: exhaustive OSD order 3 explores a different correction set than the combination sweep and may improve the remaining worst-case failures at manageable `2^3` search cost.
- Exact decoder change: `OSD_METHOD=3 -> 2`; keep `OSD_ORDER=3` and all other settings unchanged.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0006, 0.0078, 0.0245, 0.0426, 0.0607`; decode seconds `3.563, 5.241, 8.432, 12.587, 17.826`; worst-case LER `0.0607`; slowest decode `17.826s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: restore combination-sweep OSD order 2 and test it with 80 BP iterations.

## Iteration 12

- Hypothesis: extra BP work before the successful combination-sweep OSD may improve reliability of the ordering information and lower worst-case LER.
- Exact decoder change: `MAX_ITERATIONS=60 -> 80`, `OSD_METHOD=2 -> 3`, and `OSD_ORDER=3 -> 2`; restores the best OSD regime while testing a coupled larger BP budget.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0001, 0.0035, 0.0129, 0.0229, 0.0338`; decode seconds `3.656, 5.546, 9.635, 14.809, 22.598`; new best worst-case LER `0.0338`; slowest decode `22.598s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: test 100 BP iterations as the last comfortable increase under the observed timing slope.

## Iteration 13

- Hypothesis: 100 sum-product iterations may further improve OSD ordering and convergence, while projected largest-code time remains below 30 seconds.
- Exact decoder change: `MAX_ITERATIONS=80 -> 100`; all other settings unchanged.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0003, 0.0038, 0.0125, 0.0244, 0.0346`; decode seconds `3.797, 6.151, 10.601, 16.120, 24.256`; worst-case LER regressed to `0.0346`; slowest decode `24.256s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: stop the sum-product budget sweep and test min-sum+memory with the proven combination-sweep OSD postprocessor.

## Iteration 14

- Hypothesis: uniform-memory min-sum may stabilize loopy message updates differently from sum-product and, with combination OSD, improve hard-syndrome ranking.
- Exact decoder change: `MAX_ITERATIONS=100 -> 60`, `BP_METHOD=0 -> 2`, `SCALE_FACTOR=None -> 0.75`, and `GAMMA0=None -> 0.5`; `USE_SPARSITY=True` already satisfies the method requirement; OSD method 3/order 2 retained.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0004, 0.0089, 0.0309, 0.0515, 0.0742`; decode seconds `2.702, 3.288, 5.347, 8.106, 12.161`; worst-case LER `0.0742`; slowest decode `12.161s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: return to sum-product plus combination OSD and interpolate the iteration peak at 90.

## Iteration 15

- Hypothesis: 90 sum-product iterations may retain the 80-iteration accuracy gain while clarifying whether the regression begins only near 100 iterations.
- Exact decoder change: `MAX_ITERATIONS=60 -> 90`, `BP_METHOD=2 -> 0`, `SCALE_FACTOR=0.75 -> None`, and `GAMMA0=0.5 -> None`; restores the successful sum-product/OSD-3-order-2 family at the new budget.
- Command: `python scripts/run_round.py --rounds 1 --objective ler --time-cap-seconds 30`
- Result: pass on all five datasets; LERs `0.0001, 0.0038, 0.0125, 0.0236, 0.0335`; decode seconds `3.600, 5.816, 10.070, 15.356, 23.054`; new best worst-case LER `0.0335`; slowest decode `23.054s`.
- Worst-case dataset: `osd_504_3745_0.005`.
- Next idea: if research continues, test nearby budgets around 90 or reduce OSD runtime while preserving this accuracy; keep round 15 as the current best evidence-backed configuration.
