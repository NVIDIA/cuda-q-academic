<div align="center">

# CUDA-Q ADAPT-QAOA Exercise

![NVIDIA CUDA-Q](https://img.shields.io/badge/NVIDIA%20CUDA--Q-Exercise-76B900?style=for-the-badge&logo=nvidia&logoColor=white)
![ADAPT-QAOA](https://img.shields.io/badge/ADAPT--QAOA-MaxCut-111111?style=for-the-badge)

</div>

---

You are provided a baseline CUDA-Q ADAPT-QAOA implementation based on the
CUDA-Q documentation and refactored using AI. You will use Codex to modify it
shortly to parallelize it for running on multiple QPUs. You will get there by
completing the tasks below to practice planning and verifying code with Codex,
as well as leveraging multiple agents in the workflow.

The QED-C MaxCut inputs used by the exercise are included locally in:

```text
maxcut_instances/
```

---

## 1. Survey the Code

First, use Codex to generate a brief survey of the code structure so you can
understand what the different parts of the code do.

Also ask Codex to summarize the tests that the refactored AI implementation
wrote to verify that it works.

Answer this question:

- How many of these tests were quantum-specific?

---

## 2. Prepare Quantum-Specific Tests

Before proceeding, prepare tests that verify the quantum properties of the
baseline ADAPT-QAOA code. This is good practice when code comes from AI or any
other source.

These tests can confirm that the baseline implementation works and ensure that
future modifications do not break the code.

### 2a. Plan the Tests

Use your domain knowledge and brainstorm with AI to prepare a few unit tests
that verify the quantum properties of the algorithm.

Add the test logic and verification criteria into a new Markdown file:

```text
quantum_test_planning.md
```

When you are done, compare with a neighbor to see what tests they landed on.

### 2b. Implement the Tests

Tell Codex to launch a subagent to write each test and place the tests in the
tests folder. Be sure to tell Codex to run all CUDA-Q code on the `nvidia` backend so it is faster.

When they are complete:

1. Review each test to make sure it looks sound.
2. Ensure the ADAPT-QAOA implementation passes them all.

---

## 3. Plan and Implement Parallel ADAPT-QAOA

Now assume you have access to multiple QPUs, physical or simulated, and want to
parallelize the algorithm to run faster using CUDA-Q.

Your next task is to make a comprehensive plan for parallelizing ADAPT-QAOA
with CUDA-Q, then implement and test it.

Copy your original code to a new folder to save it, and work in a new folder
called:

```text
parallel_adapt_qaoa
```

### 3a. Identify Parallelization Opportunities

First, ask Codex to summarize what parts of the code could plausibly be
parallelized on multiple QPUs.

This should not consider what code changes need to be made. It should only
consider the algorithm structure and where parallelization may be possible.

Add this information to a new Markdown file:

```text
parallelization_plan.md
```

### 3b. Research CUDA-Q APIs

Point Codex to the NVIDIA CUDA-Q GitHub repository.

Ask it to pull out any information about the proper APIs you will need for this
parallelization task and have it explain:

- what the APIs do,
- what they need as inputs.

Add this information to the plan.

### 3c. Plan User-Friendly Outputs and Benchmark

If you are modifying and using existing code, it is also a great opportunity to
make it more user-friendly so that it produces outputs in the format you want.

Consider what information you would want to see, such as:

- timings,
- intermediate steps,
- output data.

Also, consider what sort of benchmark would validate whether you achieved a
true speedup. Keep ADAPT-QAOA iterations around 5 for the sake of time.
Consider preparing a brief plan for Codex to benchmark the implementation and
present the data in a nice HTML interface that is easy to analyze.

Add your preferences to the plan, including how you want to see the output data.

### 3d. Review the Plan and Assign Subagents

Now you have a robust plan with clear context to hand to Codex to implement.

Before running it, share the plan with a colleague and see if you are missing
anything important.

Before proceeding, consider what parts of the plan might be completed in
parallel and have minimal overlap.

Modify the plan to note:

- where subagents should launch,
- what their scope should be.

Make sure to state rules so the same files are not modified by multiple agents
at the same time.

### 3e. Implement and Analyze

Tell Codex to implement the plan as written and share the changes it made so you
can confirm that they look reasonable.

Then:

1. Run the final code.
2. Analyze the data in the format you desire.
3. Try a larger problem.

Answer this question:

- Does parallelizing parts with CUDA-Q provide a speedup?

---

## 4. Reflect and Generalize

Reflect on the entire process.

For any of the tests, improvement opportunities, data output formats, or other
workflows, consider whether they could be generalized and used for applications
beyond ADAPT-QAOA.

If so, download the Superpowers plugin and use the Skill Builder skill to make a
`SKILL.md` file that you can use in other contexts.

---

## 5. Compare With the Brainstorm Superpower

You just did this entire process the long way, but there are tools to enable
faster and more rigorous planning, testing, and development.

Try using the Brainstorm superpower to prepare a full plan for a parallel
ADAPT-QAOA implementation. Make sure it references the skill file you just
prepared.

How does it do? Does it miss things in your plan?

Do not implement now for the sake of time, but you can run it later to see the
results.

---

<div align="center">

![Plan carefully](https://img.shields.io/badge/Plan%20carefully-Test%20quantum%20behavior-76B900?style=for-the-badge&logo=nvidia&logoColor=white)

</div>

## Data Source

The MaxCut instances in `maxcut_instances/` are from QED-C's
[`SRI-International/QC-App-Oriented-Benchmarks`](https://github.com/SRI-International/QC-App-Oriented-Benchmarks)
quantum benchmark repository.
