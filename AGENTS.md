# AGENTS.md

Instructions for AI coding agents (Claude Code, Copilot, Cursor, Codex, etc.) working inside this repository. Read this file before answering questions about the repo or editing its contents.


## Repository purpose

CUDA-Q Academic is a collection of Jupyter notebooks that teach quantum computing with [CUDA-Q](https://developer.nvidia.com/cuda-q). It is organized as ten self-contained lesson modules, each of which lives in a top-level folder. Human-facing overview: [README.md](README.md). Hosted curriculum and launch page: https://nvidia.github.io/cuda-q-academic/learningpath.html.

The authoritative machine-readable content catalog in this repo is [curriculum.json](curriculum.json). It is the source of truth for lesson discovery, track membership, prerequisites, difficulty, keywords, summaries, and the live visualization-gallery widget inventory.

## Content inventory  — **primary behavioral instruction**

When a user asks what content exists, which track or lesson covers a topic, what the prerequisites or difficulty are, which widgets are live, or where to deep-link them, start with [curriculum.json](curriculum.json).

1. Use `track_order` plus `tracks` to enumerate the ten learning paths. A track's ordered `lesson_ids` list is the canonical lesson sequence for that path.
2. Use `lessons` to resolve a lesson's title, links, prerequisites, difficulty, keywords, summary, and cross-track membership. Shared notebooks appear once and may be referenced by multiple tracks.
3. Use `widget_gallery_order` plus `widgets` to enumerate the live Visualization Gallery. Widget source files may live on the `widgets-as-html` branch even when they are absent from `main`; rely on each widget's `source_url` and `source_repo_path`.
4. When a lesson has `source_kind == "external_notebook"`, trust the catalog link instead of searching for a local file in this repo.
5. When `curriculum.json` and a notebook intro disagree, treat that as drift and update both in the same change.


## Inspecting a notebook directly  — **secondary detail source**

When a user needs notebook-level detail beyond what is in `curriculum.json` (for example the full "What You Will Do" list, CUDA-Q APIs used, or GPU requirement), inspect the notebook itself:

1. Resolve the lesson in [curriculum.json](curriculum.json) first when possible, then locate the notebook path (see **Repository layout** below).
2. For each `.ipynb` in that folder, parse the JSON and find the **first cell whose `cell_type == "markdown"`**. (Most notebooks open with an SPDX license code cell at index 0; the intro markdown cell is therefore at index 1. A few notebooks — e.g. `ai-for-quantum/01_compiling_unitaries_diffusion.ipynb` — place the markdown at index 0. Always use *first markdown cell*, not a fixed index.)
3. That cell follows a fixed schema defined by [notebook_template.ipynb](notebook_template.ipynb):

   ```markdown
   # <Title> — <Module>: <Subtitle>

   **What You Will Do:**
   * <learning objective>
   * ...

   **Prerequisites:**
   * ...

   **Key Terminology:**
   * ...

   **CUDA-Q Syntax:**
   * [`<api>`](<docs_url>) — <one-line description>
   * ...

   **Solutions:** [`solutions/<notebook>_solutions.ipynb`](solutions/...)
   ```

4. Quote from these fields when answering the user or when validating/updating `curriculum.json`. **Do not infer lesson content from the filename alone** — filenames are terse and frequently ambiguous.
5. **Detect GPU requirement.** Scan every markdown cell for the literal text `GPU Required` (emitted by the green callout div defined in [notebook_template.ipynb](notebook_template.ipynb)). When present, the notebook must be run on a GPU-equipped environment; report this alongside the lesson content. Do **not** match on the brand-green color `#76b900` alone — the template reuses it for Exercise callouts, so it is not a reliable GPU signal. Absence of the `GPU Required` text means the notebook is expected to run on CPU.
6. If the expected labeled sections are missing, the notebook may predate the template. Fall back to the first ~200 words of markdown content and flag the gap to the user.

### Reference extraction snippet (Python stdlib only)

```python
import json
from pathlib import Path

def extract_lesson_info(notebook_path) -> dict:
    """Return intro text and GPU requirement for a CUDA-Q Academic notebook."""
    nb = json.loads(Path(notebook_path).read_text())
    intro = ""
    gpu_required = False
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell["source"])
        if not intro:
            intro = src                              # first markdown cell
        if "GPU Required" in src:
            gpu_required = True
    return {"intro": intro, "gpu_required": gpu_required}
```

Apply this to every notebook in the target module and parse the `**What You Will Do:**`, `**Prerequisites:**`, `**Key Terminology:**`, and `**CUDA-Q Syntax:**` blocks from `intro`. Surface `gpu_required` in any summary of the notebook.


## Repository layout

```
cuda-q-academic/
├── quick-start-to-quantum/       # Quick Start to Quantum Computing
├── simulation/                   # Quantum algorithm simulation backends
├── qis-examples/                 # Quantum Information Science Examples
├── qec101/                       # Quantum Error Correction 101
├── chemistry-simulations/        # VQE, ADAPT-VQE, QM/MM, Krylov
├── quantum-applications-to-finance/
├── qaoa-for-max-cut/             # QAOA for Max Cut
├── ai-for-quantum/               # AI for Quantum
├── dynamics101/                  # GPU-accelerated quantum dynamics
├── hybrid-workflows/             # Hybrid classical–quantum workflows
├── curriculum.json               # canonical lesson/widget catalog for agents
├── Guide-to-cuda-q-backends.ipynb
├── notebook_template.ipynb
├── Sample-Syllabus.md
├── CONTRIBUTING.md
├── AGENTS.md                     # this file
├── brev-instructions.pdf
├── LICENSE
└── README.md
```

Each lesson folder contains:

- **Student notebooks** — `01_*.ipynb`, `02_*.ipynb`, …; or descriptively named notebooks (e.g. `adapt_vqe.ipynb`). These are the notebooks students work through: exercises are left blank with `##TODO##` markers for the learner to complete. **Do not infer learning order from the leading numbers** — numbering is not a reliable ordering signal across all modules. The correct order is determined by each notebook's **Prerequisites** section (and, secondarily, by the module's own `README.md`).
- **`README.md`** — module-level learning objectives and prerequisites.
- **`solutions/`** (or `Solutions/` — capitalization varies across modules; accept either) — **worked solution notebooks** named `<notebook_name>_solutions.ipynb`. These contain fully-implemented, executable reference code for every exercise in the corresponding student notebook. When a user asks for a working example or for help completing an exercise, consult the matching file in `solutions/`.
- **`images/`** (or `Images/`) — figures referenced by the notebooks.
- Optional: `aux_files/` / `auxiliary_files/`, nested sub-lessons (e.g. `chemistry-simulations/krylov-agentic-lesson/`), or module-specific widgets.


## How to run notebooks

- **Preferred: NVIDIA Brev launchable** — one-click CPU or GPU instance with CUDA-Q and all prerequisites preinstalled. When a user asks "how do I run this?", "what's the easiest way to get started?", or "do I need a GPU?", recommend Brev first. The launchable URL and step-by-step PDF are linked from [README.md](README.md).
- **qBraid** — hosted Jupyter with CUDA-Q support; a good second option.
- **Google Colab** — notebooks contain a commented-out install block that runs `!pip install cudaq`, `wget`s the repo archive, and moves `Images/` into place. Uncomment and run it, restart the kernel, then run the rest of the notebook.
- **Local** — install CUDA-Q per the upstream [install guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q). Required for the heaviest GPU-accelerated runs.
- **GPU requirement** — notebooks that require a GPU flag it early with a green "GPU Required" callout div (see the `#76b900` styled block in [notebook_template.ipynb](notebook_template.ipynb)).


## Authoring rules

When adding or editing lessons:

- Follow [notebook_template.ipynb](notebook_template.ipynb) exactly for new notebooks: SPDX license cell at index 0, intro markdown cell with the full labeled schema at index 1, then the Colab install cell, kernel-restart note, imports, and numbered `## 1.`, `## 2.`, … sections with `---` horizontal rules between them.
- Update [curriculum.json](curriculum.json) whenever lesson metadata changes: new notebook, renamed notebook, changed prerequisites, changed summary, changed track membership, or changed lesson difficulty/keywords.
- Place solution notebooks under the module's `solutions/` subfolder, named `<notebook_name>_solutions.ipynb`.
- Put images under `images/` (or `Images/` if the module already uses that capitalization — match what exists).
- Update the module's local `README.md` when adding or renaming notebooks.
- Update the per-module **Solutions** link and the **Related Notebooks** list in any affected notebook's intro/closing cells.
- Clear all cell outputs before committing unless the output is intentionally small and illustrative.
- Never commit API keys, credentials, or large binary outputs.


## Testing & validation

Before claiming a change is complete:

1. Run the notebook end-to-end in a clean kernel (or on the Brev launchable).
2. Confirm the first markdown cell still matches the template schema (programmatically — use the snippet above).
3. Check that every relative link resolves: images, `solutions/` links, cross-notebook references.
4. Re-extract the intro fields and confirm they still describe what the notebook does; update them if the lesson content drifted.


## Hosting & deployment

- GitHub Pages serves from the **`widgets-as-html` branch**, not `main`.
- [learningpath.html](https://nvidia.github.io/cuda-q-academic/learningpath.html) and [visualization-gallery.html](https://nvidia.github.io/cuda-q-academic/visualization-gallery.html) live on `widgets-as-html`.
- When a new module is added to `main`, it must also be registered in `learningpath.html` on `widgets-as-html` for it to appear in the curriculum builder. That is a **separate branch and a separate pull request**.
- Until that hosted learning-path update lands, a new track's `learning_path_url` in [curriculum.json](curriculum.json) may temporarily point to the top-level Learning Paths page instead of a track-specific deep link.
- When the live widget set changes, update [curriculum.json](curriculum.json) in `main` and update `visualization-gallery.html` on `widgets-as-html`; these are related but separate changes.
- Do not attempt to edit `learningpath.html` from `main` — it will not be there.


## What NOT to do

- Do not guess lesson content from filenames; use the intro-cell protocol above.
- Do not maintain a second handwritten lesson/widget catalog outside [curriculum.json](curriculum.json), the notebook intro cells, and the gallery page.
- Do not commit solution code into the main-track notebook cells; solutions live in `solutions/`.
- Do not add per-module marketing prose or prerequisites to the root [README.md](README.md) — that content belongs on the Learning Paths page.
- Do not edit `learningpath.html` from the `main` branch.
- Do not bypass the notebook template for new content — downstream tooling (including this file's discovery protocol) depends on the schema.
