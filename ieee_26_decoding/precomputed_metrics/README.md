# Precomputed leakage-sweep metrics

These eight JSON files are full distance-9 Ising-decoder leakage-sweep results
(`262,144` shots per basis). They provide the reference curve used by the
workshop notebook.

The `p = 1e-4` point is intentionally not bundled. In `workshop` mode, a
participant generates that point locally with a small shot budget; the notebook
then merges it with these reference files and marks it with a star in the
plots. This makes the generation workflow observable without requiring each
participant to run the entire nine-point sweep.

The short generated point is pedagogical rather than publication-quality. Run
the `gpu` mode to regenerate a full, statistically meaningful sweep.
