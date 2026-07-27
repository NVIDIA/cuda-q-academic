"""Fixed round-one proposal copied into each researcher's experiment.py."""

SETTINGS = {
    "precision": "fp64",
    "controlled_rank": 1,
    "path_reuse": True,
    "hyper_samples": 8,
    "find_threads": 10,
    "find_limit": True,
    "deterministic": False,
    "scratch_percentage": 50,
}

RATIONALE = (
    "Use the fixed FP64 round-one template so every fresh study starts from "
    "the same conservative CUDA-Q TensorNet configuration."
)

HYPOTHESIS = (
    "This fixed FP64 baseline will remain correct and complete within the "
    "30-second limit, providing a common reference for later agent choices."
)
