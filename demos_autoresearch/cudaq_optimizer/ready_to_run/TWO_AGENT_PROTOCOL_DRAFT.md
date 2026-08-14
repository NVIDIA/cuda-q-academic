# Two-agent protocol note

The finalized two-agent protocol is authoritative in `AGENTS.md`.

- Explorer proposes even rounds 2 through 20.
- Improver proposes odd rounds 3 through 19.
- The coordinator alone edits optimizer code and evaluates.
- Proposals are sequential and use only the study ledger as benchmark-result
  evidence.
- The objective is lowest energy within 300 counted observes. Close energies
  use convergence or early completion and elapsed time as tie-breakers.
