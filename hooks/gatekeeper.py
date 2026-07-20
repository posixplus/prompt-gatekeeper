#!/usr/bin/env python3
"""Prompt Gatekeeper — UserPromptSubmit hook.

Runs before Claude sees each prompt. It never calls a model and never blocks
the prompt; it only injects context that tells Claude to apply the
prompt-gatekeeper skill when warranted.

Modes (env GATEKEEPER_MODE, default "tag"):
  off  — hook does nothing.
  tag  — strict gatekeeping only when the prompt contains [gatekeeper]
         or [Use Prompt Gatekeeper] (case-insensitive).
  auto — tag behavior, plus a soft nudge on prompts that look broad and
         under-specified (long, no code block, no file paths).
"""

import json
import os
import re
import sys

TAG_RE = re.compile(r"\[(gatekeeper|use prompt gatekeeper)\]", re.IGNORECASE)

STRICT_CONTEXT = (
    "GATEKEEPER HOOK (strict mode): The user tagged this prompt for gatekeeping. "
    "Before executing the task, apply the prompt-gatekeeper skill in strict mode: "
    "score the prompt against all 6 pillars and follow the skill's flow. "
    "Do not skip the scorecard even if the task looks simple."
)

NUDGE_CONTEXT = (
    "GATEKEEPER HOOK (auto mode): This prompt looks broad or under-specified. "
    "Consider applying the prompt-gatekeeper skill in judgment mode before "
    "executing. If the request is actually clear, execute it directly."
)


def looks_vague(prompt: str) -> bool:
    """Cheap heuristic for 'complex and under-specified'. Deliberately
    conservative: false negatives are fine (Claude can still judge on its
    own); false positives annoy the user on every message."""
    if "```" in prompt:
        return False  # code included -> usually a concrete task
    if re.search(r"\S+\.(py|js|ts|tsx|go|rs|java|sql|md|json|yaml|yml|toml|css|html)\b", prompt):
        return False  # references specific files -> concrete
    words = prompt.split()
    if len(words) < 12:
        return False  # too short to be a complex multi-step ask
    build_verbs = re.search(
        r"\b(build|design|architect|create|implement|plan|set ?up|develop|migrate|refactor)\b",
        prompt,
        re.IGNORECASE,
    )
    spec_signals = re.search(
        r"\b(format|output|must|should not|don't|avoid|constraint|exactly|using|version|schema:)\b",
        prompt,
        re.IGNORECASE,
    )
    return bool(build_verbs) and not spec_signals


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    prompt = payload.get("prompt", "") or ""
    mode = os.environ.get("GATEKEEPER_MODE", "tag").strip().lower()

    if mode == "off":
        return
    if TAG_RE.search(prompt):
        print(STRICT_CONTEXT)
        return
    if mode == "auto" and looks_vague(prompt):
        print(NUDGE_CONTEXT)


if __name__ == "__main__":
    main()
    sys.exit(0)
