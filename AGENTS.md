# Workshop Guidance

This repository is a multi-exercise workshop. Each exercise lives in its own
subfolder and should be treated as an independent workspace.

## Personal Preferences

Mandatory startup requirement: The first action in every new assistant session
in this repository must be to read
`/home/cudaq/cuda-q-academic/USER.md` if it exists, before answering, greeting,
planning, or running any other task. This absolute path applies even when the
assistant is opened in an exercise subdirectory. Do not look only for a
`USER.md` file in the current working directory.

After reading `USER.md`, follow its preferences for explanation style, coding
style, and collaboration. If a direct user prompt conflicts with `USER.md`,
follow the prompt.
## Exercise Scope

- When working inside an exercise subfolder, treat that folder as the active
  scope.
- Do not inspect or modify sibling exercise folders unless the user explicitly
  asks.
- Prefer the instructions in the nearest exercise `AGENTS.md` for build, test,
  and completion criteria.
- If instructions conflict, the nested exercise instructions win.
- Keep shared root-level changes limited to workshop structure, documentation,
  or setup that is intended to apply to every exercise.

## Shared Workshop Conventions

- Use Python for workshop code unless an exercise explicitly asks for another
  language.
- Use CUDA-Q for quantum code and examples unless the user explicitly asks to
  compare against another framework.
- Keep examples runnable in the workshop environment. Prefer commands and paths
  that work from the active exercise folder.
- When changing code, preserve the baseline files unless the exercise asks to
  modify them. Put new or parallel implementations in the files named by the
  exercise instructions.
- Do not include personal data, credentials, private keys, or other sensitive
  information in prompts, files, outputs, saved conversations, or packaged
  submissions.
- Favor clear teaching-oriented explanations because this repository is used in
  a workshop setting.


  ## Sandbox Failure Handling

  - At startup, run one harmless read-only filesystem command as a sandbox
    preflight.
  - If it fails with `bwrap`, namespace, or `unprivileged_userns_clone` errors,
    treat the default sandbox as unavailable for the session.
  - Do not repeatedly retry commands with the same sandbox configuration.
  - Use the approved elevated execution path for subsequent necessary commands.
  - Clearly distinguish environment failures from project or test failures.

  ## Safe File Editing

  - Use the required `apply_patch` mechanism for source-file changes.
  - Apply one logically related file change at a time; avoid constructing large
    concatenated multi-file patches.
  - If `apply_patch` fails because its own sandbox cannot start:
    1. Retry once using workspace-relative paths.
    2. If it still fails, stop and report the editing blocker.
    3. Do not improvise with `cat`, redirection, Python file writes, or a generated
       multi-file patch unless the user explicitly authorizes a fallback and
       higher-priority instructions permit it.
  - If an authorized GNU `patch` fallback is used:
    - handle one file per patch;
    - run `patch --dry-run` first;
    - inspect the affected file immediately afterward;
    - run the smallest relevant syntax or formatting check;
    - check for and remove only newly generated `.orig` and `.rej` files after
      confirming the edit succeeded.
  - If any patch is malformed or partially applied, stop further editing and
    restore the affected file before continuing.