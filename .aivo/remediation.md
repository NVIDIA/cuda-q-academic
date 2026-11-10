## Build & test

The CI-declared notebook test script is `.test:notebooks` in `.gitlab-ci.yml`. It executes solution notebooks with `jupyter nbconvert`, filters modules by changed paths, and performs crash post-mortems for dead kernels. Source: `.gitlab-ci.yml:.test:notebooks`.

```bash
set -u

mapfile -t MODULES < <(
  printf '%s\n' "$NOTEBOOK_MODULES" | sed '/^[[:space:]]*$/d'
)

# GPU selection and CUDA_VISIBLE_DEVICES now happen in before_script,
# so the smoke probes and the notebooks share one device configuration.
if [ "${REQUIRE_GPU:-false}" = "true" ]; then
  echo "Notebooks will run with CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-<unset>}"
fi

mkdir -p "$CI_PROJECT_DIR/nb-logs"

# Host diagnostics (cgroup limits, kernel OOM messages, GPU state) describe
# the runner fleet, so collect them only for pipelines from this project.
if [ "${CI_PIPELINE_SOURCE:-}" != "merge_request_event" ] \
   || [ "${CI_MERGE_REQUEST_SOURCE_PROJECT_ID:-$CI_PROJECT_ID}" = "$CI_PROJECT_ID" ]; then
  TRUSTED_DIAGNOSTICS=true
else
  TRUSTED_DIAGNOSTICS=false
fi

POSTMORTEM_DIR="${TMPDIR:-/tmp}/nb-postmortem"
mkdir -p "$POSTMORTEM_DIR"

# -----------------------------------------------------------------------
# post_mortem <notebook> <module>
#
# nbconvert reports a dead kernel as a bare DeadKernelError: the kernel's
# own crash output is lost because nbclient tears the process down before
# anything is flushed. Re-run the same code as a plain script under
# `python -X faulthandler` (no ZMQ, no kernel indirection) so a native
# crash prints a real traceback pointing at the offending line, and
# record whether the kernel was killed from outside instead.
# -----------------------------------------------------------------------
post_mortem() {
  local nb="$1" mod="$2"
  local base; base=$(basename "$nb" .ipynb)
  echo "--- post-mortem: $nb"

  if [ "$TRUSTED_DIAGNOSTICS" = "true" ]; then
    echo "  cgroup memory events (non-zero oom_kill == the kernel was OOM-killed):"
    for f in /sys/fs/cgroup/memory.events /sys/fs/cgroup/memory.peak \
             /sys/fs/cgroup/memory/memory.failcnt; do
      [ -r "$f" ] && sed 's/^/    /' "$f"
    done
    if dmesg -T >/dev/null 2>&1; then
      dmesg -T | grep -iE 'oom|killed process' | tail -20 | sed 's/^/    /'
    else
      echo "    (dmesg unavailable in this container)"
    fi

    echo "  GPU state after the crash:"
    nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv 2>/dev/null \
      | sed 's/^/    /' || true
  else
    echo "  (diagnostics suppressed: merge request from a fork)"
  fi

  echo "  re-running as a plain script with faulthandler enabled:"
  local script="$CI_PROJECT_DIR/nb-logs/${base}.py"
  if jupyter nbconvert --to script --output-dir "$CI_PROJECT_DIR/nb-logs" \
       --output "$base" "$nb" >/dev/null 2>&1; then
    printf '%s\n' \
      'import faulthandler, sys; faulthandler.enable(all_threads=True)' \
      'def get_ipython():' \
      '    class _Shim:' \
      '        def __getattr__(self, _): return lambda *a, **k: None' \
      '    return _Shim()' \
      | cat - "$script" > "${script}.tmp" && mv "${script}.tmp" "$script"
    local log="$POSTMORTEM_DIR/${base}.postmortem.log"
    ( cd "$(dirname "$nb")" \
      && PYTHONPATH="$CI_PROJECT_DIR/$mod:${PYTHONPATH:-}" \
         timeout 1800 python -X faulthandler -u "$script" ) \
      > "$log" 2>&1
    local rc=$?
    echo "  plain-script exit code: $rc"
    if [ "$rc" -gt 128 ]; then
      echo "  -> killed by signal $((rc - 128)) (137=SIGKILL/OOM, 139=SIGSEGV, 134=SIGABRT)"
    fi
    echo "  last 60 lines of plain-script output:"
    tail -n 60 "$log" | sed 's/^/    /'
  else
    echo "  (could not convert notebook to script)"
  fi
  echo "--- end post-mortem: $nb"
}

echo "CI_COMMIT_BRANCH=${CI_COMMIT_BRANCH:-<unset>} CI_DEFAULT_BRANCH=${CI_DEFAULT_BRANCH:-<unset>} CI_PIPELINE_SOURCE=${CI_PIPELINE_SOURCE:-<unset>}"
if [ "${RUN_ALL_MODULES:-false}" = "true" ]; then
  echo "RUN_ALL_MODULES=true — running all modules."
elif [ -n "${CI_COMMIT_BRANCH:-}" ] && [ "${CI_COMMIT_BRANCH}" = "${CI_DEFAULT_BRANCH:-main}" ]; then
  echo "Running all modules (trigger: ${CI_PIPELINE_SOURCE:-unknown})"
else
  if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA:-}" ]; then
    CHANGED=$(git diff --name-only "$CI_MERGE_REQUEST_DIFF_BASE_SHA" HEAD || true)
  else
    CHANGED=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || echo "")
  fi
  echo "Changed files:"
  echo "$CHANGED" | sed 's/^/  /'

  if echo "$CHANGED" | grep -qE "^\.gitlab-ci\.yml$"; then
    echo ".gitlab-ci.yml changed — running all modules."
  else
    FILTERED=()
    for entry in "${MODULES[@]}"; do
      IFS='|' read -r MODULE _ _ <<< "$entry"
      if echo "$CHANGED" | grep -qE "^${MODULE}/"; then
        FILTERED+=("$entry")
      fi
    done
    MODULES=("${FILTERED[@]}")
  fi
fi

if [ "${#MODULES[@]}" -eq 0 ]; then
  echo "No modules to run."
  exit 0
fi

TOTAL_PASSED=0
TOTAL_FAILED=0
ALL_FAILED=()

for entry in "${MODULES[@]}"; do
  IFS='|' read -r MODULE SOLUTIONS_PATH PATTERN <<< "$entry"

  echo "================================"
  echo "Module         : $MODULE"
  echo "Solutions path : $SOLUTIONS_PATH"
  echo "Pattern        : $PATTERN"
  echo "================================"

  if [ ! -d "$SOLUTIONS_PATH" ]; then
    echo "SKIP: directory '$SOLUTIONS_PATH' does not exist"
    continue
  fi

  mapfile -t NOTEBOOKS < <(find "$SOLUTIONS_PATH" -maxdepth 1 -name "$PATTERN" | sort)

  if [ "${#NOTEBOOKS[@]}" -eq 0 ]; then
    echo "SKIP: no notebooks matching '$PATTERN' in '$SOLUTIONS_PATH'"
    continue
  fi

  for nb in "${NOTEBOOKS[@]}"; do
    echo "▶ $nb"
    if PYTHONPATH="$PWD/$MODULE:${PYTHONPATH:-}" jupyter nbconvert \
         --to notebook \
         --execute \
         --inplace \
         --ExecutePreprocessor.timeout=1800 \
         --ExecutePreprocessor.kernel_name=python3 \
         "$nb"; then
      echo "PASS: $nb"
      TOTAL_PASSED=$((TOTAL_PASSED + 1))
    else
      echo "FAIL: $nb"
      TOTAL_FAILED=$((TOTAL_FAILED + 1))
      ALL_FAILED+=("$nb")
      post_mortem "$nb" "$MODULE" || true
    fi
  done
done

echo "================================"
echo "Summary:"
echo "  Passed : $TOTAL_PASSED"
echo "  Failed : $TOTAL_FAILED"

{
  echo "passed=$TOTAL_PASSED"
  echo "failed=$TOTAL_FAILED"
  echo "image=${CUDAQX_NIGHTLY_IMAGE:-default}"
} > "$CI_PROJECT_DIR/nb-logs/summary.env"
: > "$CI_PROJECT_DIR/nb-logs/failed.txt"

if [ "$TOTAL_FAILED" -gt 0 ]; then
  echo "Failed notebooks:"
  printf '  %s\n' "${ALL_FAILED[@]}"
  printf '%s\n' "${ALL_FAILED[@]}" > "$CI_PROJECT_DIR/nb-logs/failed.txt"
  exit 1
fi
```

## Style & conventions

Notebook and Markdown style is explicitly documented in `CONTRIBUTING.md`: inline directives, names, files, commands, and command-line arguments use double backticks; code blocks use fenced triple backticks; emphasis/new terms use single asterisks; notebooks start with a level 1 heading (`CONTRIBUTING.md:24-38`).

New notebooks follow `notebook_template.ipynb`: SPDX license cell first, intro markdown with labeled sections, Colab install cell, kernel restart note, imports, numbered sections, and horizontal rules (`AGENTS.md:146-157`).

Python style is mostly straightforward script/module style: standard library imports before third-party imports, module constants in uppercase, functions in `snake_case`, optional type hints in CI utilities, and sparse comments/docstrings for operational context (`ci/notify_slack.py:15-27`, `ci/notify_slack.py:45-101`). Scientific helper code uses `snake_case`, NumPy/CUDA-Q imports, and dense explanatory comments for equations and transformations (`chemistry-simulations/aux_files/krylov/qchem/hamiltonian.py:1-18`, `chemistry-simulations/aux_files/krylov/qchem/hamiltonian.py:54-86`).

No repository-wide Python formatter configuration was observed: no `pyproject.toml` was present in the scanned repository.

## Architecture rules

Treat `curriculum.json` as the authoritative machine-readable catalog for lessons, learning tracks, prerequisites, difficulty, keywords, summaries, and widget inventory. If it disagrees with a notebook intro, update both in the same change (`AGENTS.md:8-10`, `AGENTS.md:31-39`; `curriculum.json:1-9`).

Keep this repository scoped to educational material. Do not treat notebooks here as canonical CUDA-Q API, install, backend, or performance documentation; route API/reference questions or changes to upstream CUDA-Q documentation instead (`AGENTS.md:12-29`).

Each top-level lesson module is self-contained and normally contains student notebooks, a module README, solution notebooks, images, and optional auxiliary files. Match existing capitalization such as `solutions/` vs `Solutions/` and `images/` vs `Images/` (`AGENTS.md:99-133`; `README.md:40-58`).

Do not put completed solution code into main student notebooks. Student notebooks intentionally contain `##TODO##` exercise markers; worked solutions belong under module `solutions/` or `Solutions/` folders (`AGENTS.md:127-132`, `AGENTS.md:180-187`; examples in `chemistry-simulations/adapt_vqe.ipynb` and `qec101/01_QEC_Intro.ipynb`).

When adding or renaming notebook content, update the module README, affected notebook solution links/related-notebook lists, and `curriculum.json` metadata together (`AGENTS.md:146-157`; `README.md:100-103`).

Hosting pages for the live learning path and visualization gallery are maintained on the separate `widgets-as-html` branch, not in `main`; do not try to edit `learningpath.html` from this branch (`AGENTS.md:170-187`; `curriculum.json:5-8`).

## Danger zones

Do not edit `.ipynb_checkpoints/` files. They are Jupyter checkpoint artifacts and appear under lesson folders, while `.gitignore` excludes cache/generated Python artifacts (`.gitignore:1-17`; examples under `ai-for-quantum/.ipynb_checkpoints/` and `chemistry-simulations/aux_files/qmmm/qchem/.ipynb_checkpoints/`).

Avoid changing committed binary/image assets unless the finding is specifically in that asset. Module images and PDFs are lesson resources, not source logic (`README.md:58-65`; `AGENTS.md:127-133`).

Do not touch hosted gallery/learning path files on `main`; live pages are served from `widgets-as-html` and require a separate branch/PR (`AGENTS.md:170-187`).

Do not commit secrets or environment files. `.env` and virtual environments are ignored, and authoring rules explicitly prohibit API keys and credentials (`.gitignore:6-9`; `AGENTS.md:156-157`).

Do not clear or overwrite student `##TODO##` markers in non-solution notebooks unless the security finding directly targets those cells. They are part of the exercise design (`AGENTS.md:127-132`, `AGENTS.md:180-187`).

Be cautious with GPU-required notebooks and CUDA-Q target code. Many notebooks explicitly require NVIDIA GPUs or GPU-only targets, and CI has dedicated GPU jobs with `REQUIRE_GPU=true` (`.gitlab-ci.yml:516-545`; GPU callouts in `simulation/01_simulation101.ipynb`, `quantum-machine-learning-and-data-analysis/01_an_introduction_to_hybrid_quantum_neural_networks.ipynb`, and chemistry/qec notebooks).

## Fix preferences
