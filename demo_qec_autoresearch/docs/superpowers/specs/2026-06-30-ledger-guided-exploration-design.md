# Ledger-Guided Autoresearch Exploration Design

## Goal

Update the QEC autoresearch instructions so agents use ledger evidence to
balance broad exploration with local parameter refinement. The guidance should
discourage long, low-yield sweeps without prescribing a fixed search schedule
or requiring particular BP/OSD families.

Reset the exercise after the instruction update so a new autoresearch run starts
from the original decoder baseline without prior notes, ledger rows, plots, or
downloaded datasets.

## Instruction Changes

Add an `Exploration Strategy` section to `AGENTS.md` with these principles:

- Prefer experiments that provide information about meaningfully different
  decoder behavior before committing many rounds to fine-grained tuning.
- Use recent ledger results to decide whether to refine or explore.
- Continue parameter tuning while it materially improves the worst-case
  objective, runtime headroom, or understanding of a promising region.
- When several related tuning rounds provide little or no improvement, prefer a
  meaningfully different decoder configuration with higher information value.
- Treat this as guidance rather than a quota or mandatory family checklist.

Replace the existing concept of "one small decoder change" with "one coherent
decoder experiment." A coherent experiment may change multiple coupled settings
when they are jointly required for a valid candidate, such as selecting
`bp_method=3` together with its gamma, sparsity, composition, or relay options.
Every changed setting must be recorded. Unrelated hypotheses should remain in
separate rounds so results stay interpretable.

Update both the mission wording and the round-selection protocol so this concept
is visible at the top level and at the decision point for every round.

## Reset Behavior

Return the exercise to a fresh-run state after updating `AGENTS.md`:

- Restore the decoder search baseline: `MAX_ITERATIONS=30`,
  `ITER_PER_CHECK=5`, and `SCALE_FACTOR=None`; retain the other original decoder
  defaults.
- Replace `decoders/qldpc_agent/NOTES.md` with its initial blank run-log
  template.
- Remove generated ledger rows and plots.
- Remove downloaded benchmark datasets so the preparation workflow can fetch
  them again on the next run.
- Preserve directory placeholders such as `.gitkeep` files.
- Do not change the fixed evaluator, plotting scripts, benchmark documentation,
  or README.

## Verification

After implementation:

1. Confirm `AGENTS.md` describes ledger-guided exploration and coherent logical
   experiments, without mandating a fixed family order or numeric quota.
2. Confirm the decoder contains the original baseline values.
3. Confirm `NOTES.md` contains no completed iteration sections.
4. Confirm the ledger has no experiment rows, the plots directory has no
   generated plots, and the data directory has no downloaded datasets.
5. Run the existing focused tests for plotting/harness behavior if they do not
   repopulate the reset outputs.

