# Workshop Guidance

This repository is a multi-exercise workshop. Each exercise lives in its own
subfolder and should be treated as an independent workspace.

## Personal Preferences

Startup requirement: The first action in every new assistant session in this
repository must be to read the root `USER.md` file if it exists, before
answering, greeting, planning, or running any other task.

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
