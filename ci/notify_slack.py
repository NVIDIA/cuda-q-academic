#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Post the nightly notebook-compatibility result to a Slack incoming webhook.

Reads the summary written by the `.test:notebooks` script:

    nb-logs/summary.env   passed=<n>, failed=<n>, image=<image ref>
    nb-logs/failed.txt    one failed notebook path per line

A missing summary means the job never reached the end of its script (timeout,
OOM, image pull failure), which is itself reported. Standard library only: the
job runs in the CUDA-Q image, which has no extra packages installed.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

LOG_DIR = Path(os.environ.get("CI_PROJECT_DIR", ".")) / "nb-logs"
MAX_LISTED_FAILURES = 25


def read_summary() -> Optional[Dict[str, str]]:
    summary_file = LOG_DIR / "summary.env"
    if not summary_file.exists():
        return None
    summary = {}
    for line in summary_file.read_text().splitlines():
        key, _, value = line.partition("=")
        summary[key.strip()] = value.strip()
    return summary


def read_failures() -> List[str]:
    failed_file = LOG_DIR / "failed.txt"
    if not failed_file.exists():
        return []
    return [line for line in failed_file.read_text().splitlines() if line.strip()]


def build_message() -> Dict[str, object]:
    summary = read_summary()
    failures = read_failures()
    image = (summary or {}).get("image") or os.environ.get("CUDAQX_NIGHTLY_IMAGE", "unknown")
    pipeline_url = os.environ.get("CI_PIPELINE_URL", "")
    branch = os.environ.get("CI_COMMIT_BRANCH", "unknown")
    commit = os.environ.get("CI_COMMIT_SHORT_SHA", "unknown")

    if summary is None:
        headline = ":rotating_light: CUDA-Q Academic nightly — run did not finish"
        detail = (
            "The nightly job produced no summary. It most likely timed out, was "
            "OOM-killed, or failed before executing notebooks. See the job log."
        )
    else:
        passed, failed = summary.get("passed", "?"), summary.get("failed", "?")
        icon = ":white_check_mark:" if failed == "0" else ":x:"
        headline = f"{icon} CUDA-Q Academic nightly — {passed} passed, {failed} failed"
        detail = "All notebooks passed." if failed == "0" else "Failed notebooks:\n" + "\n".join(
            f"• `{nb}`" for nb in failures[:MAX_LISTED_FAILURES]
        ) + (
            f"\n…and {len(failures) - MAX_LISTED_FAILURES} more"
            if len(failures) > MAX_LISTED_FAILURES
            else ""
        )

    context = f"*Image:* `{image}`\n*Branch:* `{branch}` @ `{commit}`"
    if pipeline_url:
        context += f"\n<{pipeline_url}|View pipeline>"

    return {
        "text": headline,
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": headline, "emoji": True}},
            {"type": "section", "text": {"type": "mrkdwn", "text": detail}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": context}]},
        ],
    }


def main() -> int:
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        print("SLACK_WEBHOOK_URL is not set; skipping Slack notification.")
        return 0

    payload = json.dumps(build_message()).encode()
    request = urllib.request.Request(
        webhook, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"Slack responded {response.status}: {response.read().decode()}")
    except urllib.error.URLError as exc:
        print(f"ERROR: could not post to Slack: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
