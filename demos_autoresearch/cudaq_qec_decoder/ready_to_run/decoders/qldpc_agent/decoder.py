from __future__ import annotations

import numpy as np

try:
    import cudaq_qec as qec
except ImportError:
    qec = None


DECODER_NAME = "nv-qldpc-decoder"
MAX_ITERATIONS = 30
BP_METHOD = 1
USE_SPARSITY = True
ERROR_RATE = None
USE_OSD = True
OSD_METHOD = 1
OSD_ORDER = 0
N_THREADS = None
ITER_PER_CHECK = 5
CLIP_VALUE = None
REPEATABLE = None
SCALE_FACTOR = 0.75
PROC_FLOAT = "fp32"
COMPOSITION = None
GAMMA0 = None
GAMMA_DIST = None
EXPLICIT_GAMMAS = None
SRELAY_CONFIG = None
BP_SEED = None
USED_CUDAQ_QEC = False


def _result_to_bits(result, width: int) -> np.ndarray:
    values = np.asarray(getattr(result, "result", result), dtype=float)
    if values.size != width:
        return np.zeros(width, dtype=np.uint8)
    return (values > 0.5).astype(np.uint8)


def _zero(problem) -> np.ndarray:
    return np.zeros((problem.syndromes.shape[0], problem.H.shape[1]), dtype=np.uint8)


def _decoder_options(problem) -> dict:
    options = {
        "max_iterations": MAX_ITERATIONS,
        "use_sparsity": USE_SPARSITY,
        "use_osd": USE_OSD,
        "osd_method": OSD_METHOD,
        "osd_order": OSD_ORDER,
        "bp_method": BP_METHOD,
    }
    if ERROR_RATE is None:
        options["error_rate_vec"] = np.asarray(problem.priors, dtype=np.float64)
    else:
        options["error_rate"] = ERROR_RATE
    optional = {
        "n_threads": N_THREADS,
        "iter_per_check": ITER_PER_CHECK,
        "clip_value": CLIP_VALUE,
        "repeatable": REPEATABLE,
        "scale_factor": SCALE_FACTOR,
        "proc_float": PROC_FLOAT,
        "composition": COMPOSITION,
        "gamma0": GAMMA0,
        "gamma_dist": GAMMA_DIST,
        "explicit_gammas": EXPLICIT_GAMMAS,
        "srelay_config": SRELAY_CONFIG,
        "bp_seed": BP_SEED,
    }
    options.update({key: value for key, value in optional.items() if value is not None})
    return options


def decode(problem):
    global USED_CUDAQ_QEC
    USED_CUDAQ_QEC = False
    if qec is None:
        return _zero(problem)
    decoder = qec.get_decoder(
        DECODER_NAME,
        np.ascontiguousarray(problem.H, dtype=np.uint8),
        **_decoder_options(problem),
    )
    USED_CUDAQ_QEC = True
    corrections = np.zeros((problem.syndromes.shape[0], problem.H.shape[1]), dtype=np.uint8)
    for index, syndrome in enumerate(problem.syndromes):
        corrections[index] = _result_to_bits(decoder.decode(syndrome.tolist()), problem.H.shape[1])
    return corrections
