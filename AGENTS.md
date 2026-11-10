# AGENTS.md — widgets-as-html

This branch is the static GitHub Pages site for CUDA-Q Academic (https://nvidia.github.io/cuda-q-academic/).
It contains only HTML/JS/JSON/images: interactive widgets under `interactive_widgets/` and the
`*/interactive_widget/` and `*/images/` module folders, plus the entry pages `index.html`,
`learningpath.html`, and `visualization-gallery.html`. There is no application build step and no
GPU or CUDA-Q runtime dependency. Do not modify the notebook CI or anything that only exists on
`main` from this branch.

## Install and test

- Node >= 20. Install dependencies with `npm ci --ignore-scripts`, then `npx playwright install chromium`.
- `npm test` — unit tests (`node --test tests/unit.test.mjs`) plus the Playwright suite.
- `npm run test:unit` / `npm run test:widgets` — each half alone.
- `npm run test:live` — waits for the GitHub Pages deployment of `CI_COMMIT_SHA`, then runs the
  live smoke subset against the public site.
- Local runs serve the checkout at `http://127.0.0.1:4173/cuda-q-academic/` via
  `ci/widgets/serve.mjs` (started by Playwright's `webServer`). Absolute
  `https://nvidia.github.io/cuda-q-academic/…` URLs in pages are intercepted and fulfilled from
  that server, so tests exercise the checkout files, not the deployed site.

## What the checks cover — and what they do not

- Every `*.html` file on the branch is loaded in Chromium: HTTP 200, non-empty title, a visible
  heading, no page errors, and no failed essential resources (document/script/stylesheet/
  image/xhr/fetch). Font requests are non-blocking; Google Fonts stylesheets are also excluded from the essential-resource check.
- Rendered `href`/`src` attributes that resolve inside the site must exist in the checkout;
  external links are skipped.
- `curriculum.json` widget entries must map to committed pages (`coming_soon` entries are exempt).
- Three interactions only: the CNOT visualizer state, the binary fraction toggles, and the
  gallery preview iframe (which must also come from the local checkout in local runs).
- This is initial-render smoke plus those interactions — not exhaustive scientific validation of
  widget behavior.

## CI

`.gitlab-ci.yml` runs only for merge requests targeting `widgets-as-html` and pushes to
`widgets-as-html`. `widgets:check` runs `npm test`; `widgets:verify-live` runs only on branch
pushes after `widgets:check`. Run `glab ci lint .gitlab-ci.yml` after every CI edit.

`ci/widgets/wait-for-deployment.mjs` polls the GitHub deployments API for the *latest*
`github-pages` deployment and requires it to be exactly `CI_COMMIT_SHA` in state `success`,
then confirms `widgets-as-html` still points at that SHA. A newer or different latest deployment
is never accepted, and older matching deployments in the list do not shortcut the wait.

`WIDGETS_GITHUB_TOKEN` is an optional read-only token for GitHub API rate limits; configure it
masked/protected in CI/CD settings only, never commit or print it. The unauthenticated API works
within the default polling budget.

Branch protection and required-check settings are separate from this YAML. Before relying on
CI as a publishing gate, protect `widgets-as-html` against direct pushes and require a passing
merge-request pipeline; the GitHub mirror route must not permit unrelated writes. GitLab's
"pipeline must succeed" setting is project-wide, so changing it requires maintainer approval
and checking its effect on other branches. Do not change remote policies automatically.
