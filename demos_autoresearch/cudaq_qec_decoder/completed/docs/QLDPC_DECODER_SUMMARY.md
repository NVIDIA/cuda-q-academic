# QLDPC Decoder Summary

This file is the reusable research map for CUDA-Q QEC QLDPC decoder rounds.
Read it before proposing a round change, then cross-check the current ledger.

Sources:

- CUDA-Q QEC Python API:
  https://nvidia.github.io/cudaqx/api/qec/python_api.html
- CUDA-Q QEC decoder examples:
  https://nvidia.github.io/cudaqx/examples_rst/qec/decoders.html
- CUDA-QX 0.2.0 release datasets:
  https://github.com/NVIDIA/cudaqx/releases/tag/0.2.0

## Benchmark Target

Default datasets are five CUDA-QX 0.2.0 QLDPC syndrome files at physical error
rate `0.005`, chosen across increasing code sizes:

- `osd_216_865_0.005.json.bz2`
- `osd_288_1585_0.005.json.bz2`
- `osd_360_2305_0.005.json.bz2`
- `osd_432_3025_0.005.json.bz2`
- `osd_504_3745_0.005.json.bz2`

Each round evaluates all five datasets. The decision metric is the worst
dataset point for the chosen objective, so a candidate must be broadly good
rather than excellent on only one size.

## Decoder Family

Use `cudaq_qec.get_decoder("nv-qldpc-decoder", H, **options)`. The decoder is a
GPU-accelerated QLDPC decoder based on belief propagation (BP), with optional
ordered statistics decoding (OSD) post-processing when BP does not converge.

Other CUDA-Q QEC decoders exist, but this benchmark is QLDPC-specific:

- `nv-qldpc-decoder`: primary target for all rounds.
- `trt_decoder`: requires trained model artifacts; do not use unless they are
  already present and the run is explicitly changed to benchmark that path.
- Tensor Network and Sliding Window decoders are not the default QLDPC path for
  these release JSON parity-check datasets.

## Core BP Selection

`bp_method` selects the main BP algorithm:

- `bp_method=0`: sum-product. Most conservative first check; can be accurate
  but may be slower or less stable on some loopy matrices.
- `bp_method=1`: min-sum. Often faster and tunable through `scale_factor`.
- `bp_method=2`: min-sum+mem. Adds uniform memory strength. Requires
  `use_sparsity=True` and `gamma0`.
- `bp_method=3`: min-sum+dmem. Adds disordered memory strength. Requires
  `use_sparsity=True` and either `gamma_dist` or `explicit_gammas`.

Relay BP uses `composition=1` with `bp_method=3`, `use_sparsity=True`,
`gamma0`, and `srelay_config`. This runs multiple gamma legs sequentially.
Use it only as a deliberate round because it adds knobs and may trade runtime
for convergence robustness.

## OSD Selection

`use_osd=True` enables an OSD postprocessor after BP. This may lower LER, but it
can raise decode time.

`osd_method` choices:

- `1`: OSD-0. Cheapest OSD mode and the default postprocessor to survey.
- `2`: exhaustive search. Search grows with `2 ** osd_order`; use carefully
  under a runtime cap.
- `3`: combination sweep. Searches all weight-1 permutations and a controlled
  set of weight-2 permutations based on `osd_order`.

`osd_order` controls extra search for methods 2 and 3. Keep it small unless the
ledger shows runtime headroom.

## Runtime And Numeric Options

- `max_iterations`: BP iteration limit. Higher can improve convergence and
  increase time.
- `iter_per_check`: BP convergence-check cadence. Larger values can reduce
  checking overhead but may waste iterations after convergence.
- `use_sparsity`: should usually stay `True` for these sparse QLDPC matrices.
- `scale_factor`: min-sum scale. `1.0` is unscaled, `0.0` asks the decoder to
  compute a dynamic scale, and values such as `0.625`, `0.75`, or `0.8` damp BP
  messages.
- `clip_value`: clips BP messages when nonzero. Useful for stability and
  required by `repeatable=True`.
- `repeatable`: deterministic BP/Relay BP behavior. Slower, but useful when
  comparing subtle timing or syndrome effects.
- `proc_float`: `fp64` by default, `fp32` may improve speed with possible
  numerical differences.
- `n_threads`: decoder thread count. Leave unset unless testing a clear timing
  hypothesis.

## Relay BP Options

Relay BP is selected with:

- `bp_method=3`
- `composition=1`
- `use_sparsity=True`
- `gamma0=<float>`
- `srelay_config=<map>`

Relevant `srelay_config` fields:

- `pre_iter`: BP iterations before relay legs.
- `num_sets`: number of relay legs.
- `stopping_criterion`: `All`, `FirstConv`, or `NConv`.
- `stop_nconv`: required when `stopping_criterion="NConv"`.

For `bp_method=3`, provide either:

- `gamma_dist=[min_gamma, max_gamma]`
- `explicit_gammas=[[...], ...]`

Use a Relay BP round when the worst-case dataset has poor LER and there is
runtime headroom. Start with few relay legs and a conservative stopping rule.

## Fairness Rules

- Decode one syndrome at a time with `decode(...)`.
- Do not use multi-syndrome decoder calls or batch size options.
- Do not use lookup-table decoders.
- Do not hardcode syndrome labels, observable answers, dataset names, or exact
  expected corrections.
- Judge candidates by the ledger's five-dataset worst-case score.
