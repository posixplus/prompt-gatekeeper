# Prompt Gatekeeper

Stop paying for vague prompts with wasted iterations. Prompt Gatekeeper scores every request against a 6-pillar rubric **before** Claude executes it, asks only the clarifying questions that actually change the outcome, then builds and runs an enhanced version of your prompt.

```
## Gatekeeper Scorecard — 3/5

| Pillar     | Verdict | Note |
|------------|---------|------|
| Role       | pass    | implied: senior backend engineer |
| Task       | pass    | migrate auth to OAuth2 |
| Context    | GAP     | current auth implementation unknown |
| Process    | n/a     | no mandated order |
| Guardrails | GAP     | breaking-change tolerance unstated |
| Output     | pass    | working code + migration notes |
```

## How it works

**The 6 Pillars:** Role, Task, Context, Process, Guardrails, Output. Each pillar gets a verdict of pass, GAP, or n/a — you see a score like `4/5` and a one-line reason per gap, so you learn what your prompts habitually miss.

**The flow:** score → ask 1–3 targeted questions for real gaps only → build the enhanced prompt → you confirm → Claude executes it in the same conversation. No "fill in this template and resubmit" round trips. If you want a portable version for another model or a teammate, ask and you get the enhanced prompt with `[bracketed placeholders]` instead of execution.

**Clean prompts stay fast.** A well-specified request gets a one-line `Gatekeeper: 5/5 — executing.` and runs immediately. The skill is explicitly instructed not to invent gaps to look useful.

## Usage

Two ways to invoke:

1. **Explicit tag** — append `[gatekeeper]` (or `[Use Prompt Gatekeeper]`) to any prompt for a strict audit, even on simple tasks:
   ```
   Set up the database schema for the invoicing service [gatekeeper]
   ```
2. **Automatic** — broad, open-ended, multi-step requests trigger the skill on their own. Narrow tasks ("fix this syntax error") bypass it entirely.

Say "just run it" at any point to skip the questions and execute with stated best-guess assumptions.

## Installation

### As a Claude Code plugin (recommended: skill + optional hook)

```
/plugin marketplace add posixplus/prompt-gatekeeper
/plugin install prompt-gatekeeper@prompt-gatekeeper
```

### Skill only (Claude Code, Cowork, claude.ai)

Copy `skills/prompt-gatekeeper/` into your skills directory:

```bash
# personal (all projects)
cp -r skills/prompt-gatekeeper ~/.claude/skills/

# or per-project
cp -r skills/prompt-gatekeeper .claude/skills/
```

On claude.ai, upload the packaged `.skill` file under Settings → Capabilities.

## The hook (optional, Claude Code only)

Skills are opt-in by design: Claude consults them when the description matches or you invoke them. If you want **guaranteed interception of every prompt**, the plugin ships a `UserPromptSubmit` hook. It is a tiny local Python script — no model calls, no network, never blocks or rewrites your prompt. It only injects a context note telling Claude to apply the skill.

Modes, via the `GATEKEEPER_MODE` environment variable:

| Mode | Behavior |
|------|----------|
| `tag` (default) | Strict gatekeeping only when a prompt contains the tag |
| `auto` | Tag behavior, plus a soft nudge on prompts that look broad and under-specified |
| `off` | Hook does nothing |

Set it in your shell or in `.claude/settings.json` under `env`:

```json
{ "env": { "GATEKEEPER_MODE": "auto" } }
```

## Design notes (why it works this way)

- **One round trip, not two.** The original gatekeeper pattern hands you a bracketed template to fill in and resubmit. This version asks the questions, fills the template itself from your answers, and executes on your confirmation.
- **Process is conditional.** For open-ended tasks the model plans steps better than you can specify them; demanding process steps produces worse plans. The Process pillar only counts when the task has a mandated order (migrations, compliance flows, pipelines).
- **Scoring teaches.** The per-pillar scorecard means that over time you see which pillars you habitually omit and your raw prompts get better.

## Repository layout

```
prompt-gatekeeper/
├── .claude-plugin/
│   ├── plugin.json         # plugin manifest
│   └── marketplace.json    # lets the repo act as its own marketplace
├── skills/
│   └── prompt-gatekeeper/
│       └── SKILL.md        # the rubric, flow, and calibration examples
├── hooks/
│   ├── hooks.json          # UserPromptSubmit registration
│   └── gatekeeper.py       # tag/auto/off pre-filter (local, no model calls)
└── README.md
```

## License

MIT
