# Accelerated Decoders for Quantum Error Correction

## Tutorial Agenda

This hands-on tutorial consists of two 90-minute sessions combining short presentations with GPU-enabled Jupyter notebook exercises.

### Part 1: Algorithmic Decoding

| Time | Topic |
|---|---|
| 0–10 min | Welcome, tutorial overview, and cloud environment setup |
| 10–30 min | QEC decoding fundamentals and performance metrics |
| 30–50 min | [CUDA-Q QEC qLDPC decoder methods](qLDPC_decoder.ipynb) |
| 50–80 min | [Case Study: Using CUDA-Q QEC to Decode Elevator Codes](elevator_code_memory_experiment.ipynb) |
| 80–90 min | Questions, wrap-up, and additional resources |

### Part 2: AI-Based Decoding

| Time | Topic |
|---|---|
| 0–10 min | Welcome, session overview, and environment setup |
| 10–30 min | Introduction to AI-based decoding, training workflows, and the NVIDIA Ising Models|
| 30–60 min | Neutral-atom quantum computing and leakage/loss errors |
| 60–80 min | [Advanced AI decoding using models trained on leakage noise models](leakage_aware_neutral_atom_decoding.ipynb) |
| 80–90 min | Questions, wrap-up, and additional resources |

## Notebook Lessons

### CUDA-Q QEC qLDPC Decoder Methods

[`qLDPC_decoder.ipynb`](qLDPC_decoder.ipynb) introduces the CUDA-Q QEC qLDPC decoder through a common benchmark loop. It compares sum-product, min-sum, memory, disordered-memory, and sequential relay belief-propagation methods in both unbatched and batched modes. The first cell downloads its compact benchmark data set to the system temporary directory when needed.

### Elevator Code Memory Experiment

[`elevator_code_memory_experiment.ipynb`](elevator_code_memory_experiment.ipynb) is the Part 1 case study. It builds an elevator-code memory circuit, derives its detector error model, configures the CUDA-Q QEC RelayBP decoder, and explores logical-error scaling with physical error rate and code distance. Its additional exercise uses the adjacent [`Circuit_builder.py`](Circuit_builder.py) and [`Circuit_builder_advanced.py`](Circuit_builder_advanced.py) helpers.

### Leakage-Aware Neutral-Atom Decoding

[`leakage_aware_neutral_atom_decoding.ipynb`](leakage_aware_neutral_atom_decoding.ipynb) is the Part 2 advanced-decoding lesson. It compares PyMatching-only and NVIDIA Ising-decoder results for a leakage-aware neutral-atom memory experiment, using the bundled JSON metrics in [`precomputed_metrics/`](precomputed_metrics/) by default. Setting `RUN_GENERATION = True` runs an optional local data-generation workflow.

## Layout and Setup

The two notebooks expect their companion files to remain in this directory:

```text
ieee_26_decoding/
├── qLDPC_decoder.ipynb
├── elevator_code_memory_experiment.ipynb
├── leakage_aware_neutral_atom_decoding.ipynb
├── Circuit_builder.py
├── Circuit_builder_advanced.py
├── precomputed_metrics/
└── requirements.txt
```

Create an isolated Python environment and install the notebook dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The leakage notebook imports the `loss_decoder` branch of Ising-Decoding. If you plan to set `RUN_GENERATION = True`, install Git LFS before installing the requirements so the model artifacts are available. The default, precomputed-metrics workflow does not generate new experiment data.
