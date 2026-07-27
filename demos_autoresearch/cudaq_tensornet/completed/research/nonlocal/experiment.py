"""Fixed round-one proposal copied into each researcher's experiment.py."""

SETTINGS = {
    "precision": "fp32",
    "controlled_rank": 1,
    "path_reuse": False,
    "hyper_samples": 8,
    "find_threads": 1,
    "find_limit": True,
    "deterministic": False,
    "scratch_percentage": 50,
}

RATIONALE = (
    "Restore the exact settings of round 12, the best valid observed result "
    "in the completed 20-round nonlocal ledger."
)

HYPOTHESIS = (
    "No additional evaluation is planned; these settings correspond to the "
    "recorded best valid runtime of 1.136976 seconds."
)
