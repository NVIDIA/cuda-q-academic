# CUDA-Q ADAPT-QAOA Exercise

Use your favorite AI coding tool to complete the tasks below. The goal is to
practice using AI to understand, test, plan, implement, and verify a CUDA-Q
ADAPT-QAOA workflow.

## 1. Understand the Baseline

You are provided with a baseline CUDA-Q ADAPT-QAOA implementation based on the
[CUDA-Q documentation](https://nvidia.github.io/cuda-quantum/latest/) and
refactored with AI assistance.

The exercise folder contains:

| Path | Purpose |
| --- | --- |
| `README.md` | Exercise instructions. |
| `maxcut_instances/` | [QED-C](https://github.com/SRI-International/QC-App-Oriented-Benchmarks) MaxCut problem files and matching solution files. |
| `adapt_qaoa.py` | Baseline ADAPT-QAOA implementation, adapted from the [CUDA-Q ADAPT-QAOA example](https://nvidia.github.io/cuda-quantum/latest/applications/python/adapt_qaoa.html). |
| `run_qedc_input.py` | Runner for loading and solving QED-C MaxCut inputs. |
| `tests/` | Tests from the AI-assisted refactor that verify the baseline implementation and QED-C input handling. |

Complete the following:

1. Examine `adapt_qaoa.py` to get a high-level understanding of the
   implementation. Prompt your AI tool to explain the key parts and organization
   of the code so you can get up to speed quickly.
2. Run the script to make sure it works and produces the expected output.
3. Ask the AI to summarize the existing tests. Which tests verify quantum
   properties of the algorithm, and which tests verify general software or input
   handling behavior?

## 2. Prepare Quantum-Specific Tests

When using AI to modify or create code, prepare tests that verify the model's
output and guard against regressions. In this section, use AI to plan and write
tests before modifying the implementation.

### 2a. Plan the Tests

Use your quantum domain knowledge and brainstorm with your AI tool to identify
one or more quantum-specific tests that could verify ADAPT-QAOA's quantum
properties.

For example, a test for standard QAOA might confirm that all-zero parameters
produce an equal superposition.

Add the test logic and verification criteria to a new Markdown file:

```text
quantum_test_planning.md
```

Share your planned test or tests with the other participants.

### 2b. Implement the Tests

Prompt Codex to launch a subagent for each test, then collect the completed
tests in:

```text
tests/test_quantum.py
```

When the tests are complete:

1. Review each test to make sure its logic is sound.
2. Ensure the baseline ADAPT-QAOA implementation passes all tests.

## 3. Plan and Implement Parallel ADAPT-QAOA

[CUDA-Q multi-GPU workflows](https://nvidia.github.io/cuda-quantum/latest/using/examples/multi_gpu_workflows.html)
can parallelize hybrid quantum algorithms by scaling simulations to high qubit
counts with the MGPU backend or by parallelizing across multiple virtual QPUs
with the MQPU backend.

Your task is to use AI to modify the code so it can parallelize across four
available GPUs, each acting like its own QPU.

First, duplicate the original code into a folder named `baseline` so you can run
it later for comparison.

### 3a. Identify Parallelization Opportunities

There are often multiple ways to parallelize a hybrid algorithm across multiple
QPUs. Some choices can provide significant speedups, while others may not be
worth the overhead.

Prompt Codex to review the algorithm and identify which parts are best suited
for MQPU parallelization. Keep this discussion at a high level; do not consider
specific code changes or APIs yet.

Select the best option, then ask Codex to write a high-level plan and save it in:

```text
parallelization_plan.md
```

Share with the group where you plan to parallelize the code.

### 3b. Research CUDA-Q APIs

Point Codex to the
[CUDA-Q documentation](https://nvidia.github.io/cuda-quantum/latest/) and
[multi-GPU workflow guide](https://nvidia.github.io/cuda-quantum/latest/using/examples/multi_gpu_workflows.html)
so the latest API names and syntax are available in its context window.

Ask Codex to extract the CUDA-Q API information needed for your parallelization
plan, including:

- what each API does,
- what inputs each API needs.

Add this information to `parallelization_plan.md`.

### 3c. Plan Data Output and Visualization

The point of parallelizing the code is to produce a speedup, so the plan should
include timing data.

Prompt Codex to identify where timings should be captured in the code to verify
that the parallel implementation is faster. Add those timing points to the plan.
Remember that the same timing data must also be captured in the baseline code
for comparison.

Rather than inspecting raw timing data, update the plan so the implementation
directly produces figures that compare the parallel and baseline runs.

Prompt Codex to plan a script that produces a timing comparison figure.

Optional: If you want a more interactive presentation, ask Codex to plan an HTML
report that visualizes the data in a browser.

### 3d. Review the Plan and Assign Subagents

You now have a robust plan and prepared verification tests. Before handing the
plan to Codex for implementation, look for independent tasks that can be
completed in parallel.

Ask Codex to suggest where subagents could best be added to the plan for
non-overlapping implementation tasks. If you like the suggestion, ask Codex to
add the subagent instructions to `parallelization_plan.md`.

Share your subagent task breakdown with the group.

### 3e. Implement and Analyze

Tell Codex to implement the plan. You should see it launch subagents to complete
the tasks defined above.

When the code is complete:

1. Confirm that all tests pass.
2. Examine the plot comparing the parallel timing to the baseline timing.
3. Determine whether a speedup was realized.

If no speedup appears, try a larger problem instance and check whether the
results change.

If everything worked, share your end-to-end speedup with the group. If something
failed, share what went wrong.

## 4. Reflect and Generalize

Reflect on the process and consider where better prompting, planning, or custom
skill files might have improved the outcome or efficiency of the exercise.

Look for cases where:

- tasks generalize beyond this specific problem,
- the model got stuck or performed poorly.

These are good opportunities to build a custom `SKILL.md` file that you can use
in other contexts based on what you learned from this exercise.

Download the [Superpowers plugin](https://github.com/obra/superpowers) and use
the Skill Builder meta-skill to make a `SKILL.md` file. The
[Superpowers skills repository](https://github.com/obra/superpowers-skills) is a
useful reference for how reusable skills are structured.

Share with the group what skill you are building.

## 5. Optional: Compare With the Brainstorm Superpower

You just did this process the long way, but there are tools that enable faster
and more rigorous planning, testing, and development.

Try using the
[Brainstorm superpower](https://github.com/obra/superpowers/tree/main/skills/brainstorming)
to prepare a full plan for a parallel ADAPT-QAOA implementation. Start with a
simple prompt describing what you want to do, then observe how well the
brainstorm skill converses with you to build a complete plan.

How does it do? Does it miss anything from your plan, or does it capture ideas
your plan lacked?

Do not implement during the workshop if time is limited, but you can run the
plan later to see the results.

Share your observations with the group.

## Data Source

The MaxCut instances in `maxcut_instances/` are from QED-C's
[`SRI-International/QC-App-Oriented-Benchmarks`](https://github.com/SRI-International/QC-App-Oriented-Benchmarks)
quantum benchmark repository.

## Resources

- [NVIDIA CUDA-Q documentation](https://nvidia.github.io/cuda-quantum/latest/)
- [CUDA-Q ADAPT-QAOA example](https://nvidia.github.io/cuda-quantum/latest/applications/python/adapt_qaoa.html)
- [CUDA-Q multi-GPU workflows](https://nvidia.github.io/cuda-quantum/latest/using/examples/multi_gpu_workflows.html)
- [QED-C application-oriented benchmark repository](https://github.com/SRI-International/QC-App-Oriented-Benchmarks)
- [Superpowers plugin](https://github.com/obra/superpowers)
- [Superpowers skills repository](https://github.com/obra/superpowers-skills)
