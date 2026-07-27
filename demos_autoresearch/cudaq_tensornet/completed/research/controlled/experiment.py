"""Fixed round-one proposal copied into each researcher's experiment.py."""

SETTINGS = {
    "precision": "fp32",
    "controlled_rank": 4,
    "path_reuse": False,
    "hyper_samples": 8,
    "find_threads": 10,
    "find_limit": True,
    "deterministic": False,
    "scratch_percentage": 50,
}

RATIONALE = (
    "Restore the exact settings from round 9, the best valid observation in "
    "the completed controlled-circuit ledger at 0.423730 seconds."
)

HYPOTHESIS = (
    "The study is complete; no additional evaluation is planned for this "
    "restored best-observed proposal."
)
