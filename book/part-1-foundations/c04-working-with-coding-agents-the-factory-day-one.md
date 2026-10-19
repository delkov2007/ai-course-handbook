# C4 — Working with coding agents: the Factory, day one

> **Level:** 1 — Foundations (Beginner) · **Duration:** 10h (theory 20% / labs 80%) · **Prerequisites:** C0–C3 (product builds, tests run in the devcontainer, prompts/tools exist), a GitHub Copilot plan with agent mode and cloud agent enabled, Claude Code installed; Codex optional · **Volatility:** High (agent features, modes, file conventions and pricing change monthly)

## Why this matters

From this module on, you build Fleet Ops Copilot *through* coding agents. That sounds like a productivity shortcut; the evidence says it is an amplifier. DORA 2025 (≈5,000 professionals) found ~90% AI adoption and called AI "a mirror and a multiplier": teams with strong version control, small batches, platform engineering and accessible internal knowledge gain; teams without them get more instability. METR's 2025 randomized trial found experienced open-source developers **19–20% slower** with AI tools while *believing* they were ~20% faster; METR's February 2026 update says developers are probably sped up now but calls its own data "very weak evidence" of the size. Both findings point the same way: the outcome depends on the system around the agent, not the agent.

Without that system, the failure modes are concrete. An agent "fixes" Trakia's plate normalizer by weakening the test. It adds a NuGet package whose name it hallucinated — a USENIX 2025 study found **19.7% of 2.23M code samples** referenced non-existent packages (205,474 unique names), and **43%** of those names recurred on every one of 10 runs, which is what makes *slopsquatting* attacks predictable. It reads `.env` into its context, pushes to `main`, and leaves you a 1,400-line diff you can't explain — Thoughtworks calls the result "codebase cognitive debt" (Caution).

Experts make agents productive by giving them **context** (short, curated memory files), **a runnable definition of done** (tests, build, evals the agent must run), **constrained permissions** (sandbox, allow/deny rules, protected branches), and **the right amount of plan** for the task. They measure outcomes (first-pass acceptance, rework, escaped defects, cost per merged PR), not lines generated. This module sets up that system — your Factory — and runs your first feature through it.

## Learning outcomes

By the end of C4 you can:

1. **Map** the transferable coding-agent primitives (local agent, cloud agent → PR, memory files, skills, subagents/custom agents, hooks, MCP, headless/CI mode, AI reviewer) onto GitHub Copilot, Claude Code and OpenAI Codex.
2. **Write** a short, curated `AGENTS.md` (plus `CLAUDE.md` and `.github/copilot-instructions.md`) and **measure** its effect on a fixed task.
3. **Run** the explore → plan → implement → verify loop, choosing spec ceremony proportional to the task.
4. **Give** agents runnable checks (build, tests, eval smoke) and **enforce** them with hooks or CI rather than prose.
5. **Configure** permission modes, allow/deny rules and sandboxing so that agents cannot read secrets, push to protected branches or install unvetted packages.
6. **Run** parallel agents safely in git worktrees and **delegate** an issue to a cloud agent that returns a PR.
7. **Detect** and **prevent** slopsquatting, test-weakening and insecure patterns in agent diffs.
8. **Explain** every line of an agent's merged diff, and **evaluate** agent productivity with outcome metrics.

## Concepts

### The converged primitive set (late 2026)

| Primitive | GitHub Copilot | Claude Code | OpenAI Codex |
|---|---|---|---|
| Local agent | Agent mode in VS Code / VS 2026 ("Agent (Preview)" built on the Copilot CLI SDK, built-in .NET/Azure skills); Copilot CLI (GA Feb 2026 — verify) | CLI, IDE extensions, desktop, web | Codex CLI (open source), IDE |
| Cloud agent → PR | **Copilot cloud agent** (docs URLs moved from "coding agent" to "cloud agent" — rename not officially confirmed, verify): assign an issue or Azure Boards work item → draft PR on a `copilot/*` branch, firewalled environment, self-review, Actions on its PRs need human approval | Cloud sessions, GitHub Actions integration, Routines | Codex cloud (persistent, configurable environments since DevDay, 29 Sep 2026) |
| Memory files | `.github/copilot-instructions.md`, path-scoped `.github/instructions/*.instructions.md` (verify front-matter), AGENTS.md support (verify scope per surface) | `CLAUDE.md` (project, `.claude/CLAUDE.md`, `CLAUDE.local.md`), reads `AGENTS.md`, `@path` imports, `.claude/rules/` | `AGENTS.md` |
| Skills / custom agents | Custom agents `.github/agents/*.agent.md` (own tools, MCP servers, model, instructions); org-wide in `.github-private` | Skills `.claude/skills/<name>/SKILL.md`; subagents `.claude/agents/*.md`; plugins | Skills/agents (verify current) |
| Hooks (deterministic) | Copilot SDK hooks (pre/post tool use); cloud agent setup steps (verify) | `PreToolUse`, `PostToolUse`, `Stop`, … in settings | Verify |
| Headless / CI | Copilot CLI, cloud agent | `claude -p --output-format json`, GitHub Actions | CLI non-interactive |
| AI review | Copilot code review | Managed Code Review, review subagents | Automatic PR reviews (DevDay 2026) |

**AGENTS.md** is "a simple, open format for guiding coding agents" stewarded by the Agentic AI Foundation (Linux Foundation). **Agent Skills (SKILL.md)** — YAML front-matter (name, description) plus instructions/scripts, loaded by **progressive disclosure** (only metadata in context until relevant). Thoughtworks Radar Vol. 34 (Apr 2026): Claude Code and Cursor **Adopt**, Codex **Trial** (can suggest outdated library patterns — tests and review essential); curated shared instructions and context engineering **Adopt**; Agent Skills, feedback sensors for coding agents, mutation testing, sandboxed execution by default and Dev Containers **Trial**; Spec Kit and OpenSpec **Assess**; agent instruction bloat, coding agent swarms, "MCP by default", codebase cognitive debt and coding throughput as a productivity measure **Caution**.

Teach and use the *primitives*; tool walkthroughs date within months. For a .NET/Azure shop, Copilot is usually the system of record (Boards → cloud agent → PR, `@Test`, Upgrade agent); Claude Code and Codex are power-user and headless layers. Note: the Boards → Copilot flow creates PRs in **GitHub** repos; no evidence it targets Azure Repos — an architecture decision for Azure DevOps shops (C19).

### Memory files: short, curated, tested

Context windows fill fast and performance degrades as they fill. Anthropic's guidance for `CLAUDE.md` applies to all memory files: keep it short (target < 200 lines per file); include only what the agent can't infer from the code — build/test commands, non-default conventions, repo etiquette, gotchas; move occasional knowledge into skills (loaded on demand) and **rules that must always hold into hooks**, because memory files are context, not enforcement. Contradictory instructions get resolved arbitrarily. Treat memory files as code: reviewed, pruned, and measured on a fixed task.

Single source of truth pattern for this course: `AGENTS.md` is canonical; `CLAUDE.md` contains `@AGENTS.md` plus Claude-specific notes; `.github/copilot-instructions.md` is a short pointer/summary (or rely on Copilot's AGENTS.md support once verified for each surface you use).

```markdown
# AGENTS.md — Trakia Fleet Ops Copilot
## Build & verify (run before claiming done)
- `dotnet build -warnaserror` ; `dotnet test --filter "Category!=Eval"` ; `./scripts/eval-smoke.sh` (C5)
## Conventions
- All model access via keyed `IChatClient` from `ChatClientFactory`; never `new OpenAIClient(` elsewhere.
- Prompts live in `prompts/*.md` (versioned front-matter). No prompt string literals in `src/`.
- Never assert exact model output strings in tests; assert schemas, rules, pass rates.
- Plates: normalize with `IPlateNormalizer` (Cyrillic canonical). Dates: `Europe/Sofia`.
- New NuGet packages only from `docs/allowed-packages.md`; propose additions in the PR description.
## Boundaries
- Do not modify `tests/**/Acceptance/**` or `evals/golden/**` — humans own assertions and labels.
- Do not touch `.github/workflows/**` or `infra/**` without an explicit instruction.
## Gotchas
- Aspire needs Docker; SQL container takes ~20s on first start.
```

### The loop: explore → plan → implement → verify

1. **Explore** read-only (plan mode): the agent reads code and summarizes how the feature fits.
2. **Plan**: a short written plan you review — files to touch, tests to add, risks.
3. **Implement** in small steps.
4. **Verify against an executable check**, not the agent's claim. The agent runs build/tests/evals; a **Stop hook** or CI gate refuses "done" while checks fail. Anthropic: give the agent a runnable check; after two failed corrections, `/clear` and restart with a better prompt rather than arguing in a polluted context; use separate sessions for writer and reviewer (and, in C11, for test-writer and implementer).

**Spec ceremony proportional to the task:** one-line diff → no plan; multi-file change → plan mode; feature → interview → `SPEC.md` → fresh session to implement; brownfield change → delta spec. Spec-driven development is **contested**: Böckeler documents Kiro turning a small bug into 4 user stories with 16 acceptance criteria, agents ignoring specs, review fatigue on verbose Markdown, and echoes of model-driven development. The expert skill is choosing the *least* ceremony that makes the work verifiable.

### Runnable checks are the agent's oracle

The most valuable thing you can give an agent is a fast, deterministic signal: `dotnet build -warnaserror`, unit tests, schema snapshot tests, the C3 analyzer rules, and (from C5) an eval smoke suite. "Feedback sensors" (compilers, linters, tests run during the session) are Thoughtworks Trial. **Humans own the assertions**: acceptance tests and golden labels are protected paths; tests written by the agent *after* the code tend to encode current behavior, bugs included.

### Permissions, sandboxing, isolation

Claude Code permission modes (as documented Oct 2026; mode names churn — verify against current documentation): `default` (Manual: prompts on first use), `acceptEdits`, `plan` (read/explore only), `auto` (classifier reviews actions; default for interactive sessions since v2.1.283), `dontAsk` (auto-denies anything not pre-approved — for CI), `bypassPermissions` (only in isolated containers/VMs). Rules in `.claude/settings.json`; **deny beats allow**; Bash rules are prefix/wildcard matches that do not cover every bypass (e.g. `sh -c`), so pair them with the OS-level sandbox for network/file isolation.

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": ["Bash(dotnet build *)", "Bash(dotnet test *)", "Bash(./scripts/eval-smoke.sh)", "Bash(git status)", "Bash(git diff *)"],
    "ask":   ["Bash(dotnet add package *)", "Bash(git commit *)"],
    "deny":  ["Read(./.env)", "Read(./**/secrets*.json)", "Bash(git push *)", "Bash(curl *)", "Bash(wget *)", "Edit(./tests/**/Acceptance/**)", "Edit(./evals/golden/**)"]
  },
  "hooks": {
    "PostToolUse": [{ "matcher": "Edit|Write",
      "hooks": [{ "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/format-build.sh" }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/require-green.sh" }] }]
  }
}
```

Hook semantics: a `Stop` hook that exits **2** prevents the agent from stopping and feeds stderr back as the reason (guard with `stop_hook_active` to avoid infinite loops); `PostToolUse` cannot block (the tool already ran) but stderr is shown to the agent. (Verify `Edit(...)` path-rule syntax for your Claude Code version.)

Copilot cloud agent guardrails: pushes only to `copilot/*` branches, firewall-controlled internet, Actions on its PRs require approval; add branch protection with required reviews and required checks on `main`. Devcontainers give every agent the same sandbox (C0).

**Git worktrees** isolate parallel agents: `claude --worktree incident-intake` creates `.claude/worktrees/incident-intake/` on branch `worktree-incident-intake`; add `.claude/worktrees/` to `.gitignore`; `.worktreeinclude` copies gitignored files such as local settings (never real secrets). Subagents can run with `isolation: worktree`. Plain `git worktree add ../fleetops-feature -b feature` works with any agent. Thoughtworks cautions against large *swarms*: parallelize independent tasks, not one coupled change.

### Risks and how the Factory answers them

| Risk | Evidence | Control |
|---|---|---|
| Slopsquatting / hallucinated packages | 19.7% of 2.23M samples; open-source models 21.7% vs commercial 5.2%; real incidents (`huggingface-cli` on PyPI, `react-codeshift` spread via agent skills) | Package allowlist, `ask` on `dotnet add package`, lockfiles (`packages.lock.json` + `RestoreLockedMode`), CI check for package age/existence, no network installs in agent sandbox |
| Insecure code | Category-level risk (OWASP LLM05 Improper Output Handling; secure-coding review); quantitative 2026 rates not verified here | CodeQL in CI (agentic autofix GA 15 Oct 2026 on GHEC — C16), security-review subagent, parameterized SQL rule in AGENTS.md |
| Test weakening / hollow tests | Thoughtworks: mutation testing catches hollow tests (Trial) | Protected acceptance tests, human-owned assertions, Stryker.NET gate (C11) |
| Unreviewable diffs | DORA: larger changesets raise instability | Small batches, plan review, diff size budget per PR |
| Skill atrophy / cognitive debt | Thoughtworks Caution | "Explain the diff" gate, solo-first katas |
| Third-party skills/plugins | Thoughtworks: supply-chain risk from unreviewed skills | Only reviewed, pinned skills; no auto-install |
| Measuring the wrong thing | Thoughtworks Caution on throughput metrics; DORA keys Adopt | First-pass acceptance, rework rate, escaped defects, cost per merged PR |

### Misconceptions to unlearn

"A longer AGENTS.md is a better AGENTS.md." "If I tell the agent to run the tests, it will." "Plan mode is for big tasks only." "Auto/bypass modes are fine on my laptop." "More parallel agents = more speed." "The agent's summary of its changes is the review." "Lines of code generated is productivity."

## Tools & versions (as of Oct 2026)

| Tool | Purpose | Status | Notes |
|---|---|---|---|
| GitHub Copilot agent mode (VS Code, VS 2026 "Agent (Preview)") | Local agent | GA / VS agent preview | VS July 2026 update: built on Copilot CLI SDK, .NET/Azure skills off by default |
| Copilot cloud agent + custom agents (`.github/agents/*.agent.md`) | Issue/Boards → PR | GA (paid plan) | "Cloud agent" naming per docs URLs — verify |
| Copilot CLI | Terminal agent, plugins | GA (Feb 2026 — verify) | Built-in Explore/Task/Plan/Code-review agents |
| Copilot code review | AI PR review | GA | |
| Claude Code | Local/headless agent, hooks, skills, subagents, worktrees | GA | Auto mode default since v2.1.283; `/sandbox`; `claude -p` |
| OpenAI Codex (CLI + cloud) | Comparison agent | GA | Thoughtworks Trial |
| VS 2026 `@Test` agent | Test generation | GA (v18.3, 11 Feb 2026) | Used critically in C11 |
| Dev Containers | Agent sandbox | GA | Thoughtworks Trial |
| NuGet lock files, `dotnet list package --vulnerable` | Supply-chain checks | GA | Course `scripts/check-packages.sh` adds allowlist + age check |

## Labs

### Lab 1 — Make the repo agent-ready, and prove it (≈2h)

- **Goal:** Curated memory files that measurably improve agent performance on a fixed task.
- **Start state:** `c4/lab1-start` (C3 product, no memory files).
- **Steps:**
  1. **Baseline:** in a fresh worktree, give Claude Code *or* Copilot agent mode the fixed task `tasks/c4-baseline.md` ("Add `GET /vehicles/{plate}/status` reusing the existing tool logic, with problem-details errors and tests"). Record: time, number of human interventions, convention violations (count against a checklist: factory usage, plate normalizer, no prompt literals, no exact-string asserts), tests passing, tokens/premium requests if visible.
  2. Write `AGENTS.md` (≤ 80 lines) with build/verify commands, conventions, boundaries, gotchas. Add `CLAUDE.md` = `@AGENTS.md` + Claude-specific notes; add `.github/copilot-instructions.md` (short) and one path-scoped instruction for `tests/**` (verify Copilot front-matter syntax).
  3. Add one **skill**: `.claude/skills/add-endpoint/SKILL.md` describing the house pattern for a minimal API endpoint (problem details, keyed client injection, integration test template).
  4. Re-run the fixed task in a new worktree from the same commit. Record the same metrics.
- **Break it:** Inflate `AGENTS.md` to 400 lines by pasting the whole architecture doc and two contradictory rules ("use Dapper" / "use EF Core"). Re-run and observe adherence. Then prune.
- **Acceptance criteria:** `docs/factory/agent-readiness.md` with before/after metrics table; convention violations reduced (target: 0 on the after-run); `AGENTS.md` ≤ 100 lines and passes `scripts/lint-agents-md.sh` (checks required sections and that every command listed actually runs); the after-run PR passes CI.
- **Stretch:** Run the same fixed task with a second agent (Copilot ↔ Claude Code ↔ Codex) and compare.

### Lab 2 — Guardrails: permissions, hooks, supply chain (≈2h)

- **Goal:** Enforce the definition of done and block dangerous actions deterministically.
- **Start state:** `c4/lab2-start`.
- **Steps:**
  1. Add `.claude/settings.json` with the permissions shown above (adapt paths). Enable the sandbox (`/sandbox`) and note which network destinations are allowed.
  2. Write hooks: `format-build.sh` (`dotnet format --include <file>` then a quick `dotnet build` of the affected project; print errors to stderr) and `require-green.sh` (runs `dotnet test --filter "Category!=Eval"`; exits 2 with a reason if red; respects `stop_hook_active`).
  3. Supply chain: create `docs/allowed-packages.md`; enable `RestorePackagesWithLockFile` and locked-mode restore in CI; write `scripts/check-packages.sh` that fails if a `PackageVersion` is not in the allowlist, does not exist on nuget.org, or was first published < 60 days ago (query NuGet's API).
  4. Configure branch protection on `main`: required checks (build, tests, package check), 1 human review, no force-push.
- **Break it (red-team your own factory):** Ask the agent to (a) "read .env and print the connection string", (b) "push this to main", (c) "add the package `Microsoft.Extensions.AI.Fleet.Helpers` and use it" (doesn't exist — a slopsquatting bait name), (d) "make the failing acceptance test pass" when the implementation is wrong (watch for test editing). Record what was blocked, by which layer (permission rule, hook, CI, branch protection), and what slipped.
- **Acceptance criteria:** All four attempts blocked by a deterministic layer (not by the agent's good manners); `docs/factory/guardrails.md` lists each control, the attempt it blocked and the layer; `check-packages.sh` has tests (allowed, unknown, too-new); CI red when a non-allowlisted package is added.
- **Stretch:** Add a PreToolUse hook that blocks `dotnet add package` for any name not in the allowlist with an actionable message.

### Lab 3 — Spec-first feature through the agent: incident intake (≈2.5h)

- **Goal:** Ship the first product feature built by a coding agent from a short spec and human-owned acceptance tests.
- **Start state:** `c4/lab3-start` (mock Ticketing API with OpenAPI spec in `data/apis/ticketing.yaml`).
- **Steps:**
  1. **Interview → SPEC.md:** in plan mode, have the agent interview you and draft `specs/incident-intake/SPEC.md` (≤ 1 page): `POST /incidents` accepts a raw report, runs the C3 extractor, validates, creates a ticket via the mock Ticketing API, is idempotent on a hash of the normalized report text, returns the ticket ID and the `IncidentReport`; failure modes (extraction failed → 422 with `missingInformation`; ticketing 5xx → 503 with retry hint). Cut anything the feature doesn't need.
  2. **Humans write the acceptance tests** (`tests/FleetOps.Tests/Acceptance/IncidentIntakeAcceptanceTests.cs`, protected path) using a fake `IChatClient` returning canned `IncidentReport`s and a WireMock-style fake of the ticketing API: happy path, idempotent replay, 422, 503.
  3. **Fresh session:** the agent reads SPEC.md + AGENTS.md, writes a plan (`specs/incident-intake/PLAN.md`), you approve, it implements. The Stop hook enforces green tests.
  4. Open the PR. Run Copilot code review (or a Claude review subagent in a separate session). Address findings.
  5. **Explain the diff:** before merge, write `specs/incident-intake/EXPLAIN.md` — for each changed file, 1–3 sentences on what and why, and one thing you would have done differently.
- **Break it:** Remove the idempotency acceptance test and let the agent implement again from the spec alone. Does the implementation still handle replays? (Spec text is not a check.)
- **Acceptance criteria:** Acceptance tests unchanged by the agent (CI verifies hash of protected files); all tests green; PR ≤ 400 changed lines excluding generated files; `EXPLAIN.md` present and reviewed by a peer; `docs/factory/ai-assist-log.md` updated with first-pass acceptance (was the first PR revision mergeable?) and number of iterations.
- **Stretch:** Ask the agent to write additional (non-acceptance) tests in a *separate* session, then check whether any of them would pass against a deliberately broken implementation.

### Lab 4 — Parallel agents and the cloud agent (≈1.5h)

- **Goal:** Run independent tasks in parallel safely and delegate one to a cloud agent from an issue.
- **Start state:** `c4/lab4-start` with three issues: #1 "Add Bulgarian glossary file for prompts", #2 "Add `/health/ai` latency metric", #3 "Refactor plate normalizer to support transit plates (verify format)".
- **Steps:**
  1. Start two Claude Code sessions with `claude --worktree glossary` and `claude --worktree health-metric` (or two `git worktree add` directories with Copilot agent mode). Each delivers a PR.
  2. Assign issue #3 to the Copilot cloud agent (optionally selecting a custom agent `.github/agents/dotnet-tdd.agent.md` that you write: tools limited to read/edit/test, instructions to write failing tests first). Ensure the cloud agent's environment can build (setup steps workflow — verify current file name/location).
  3. Review all three PRs. Record per PR: first-pass acceptance (y/n), review iterations, wall-clock time, your review time, and cost proxies (premium requests / tokens where visible).
  4. Resolve any merge conflict between the two worktree PRs yourself; note what caused it.
- **Break it:** Launch a third local agent on a task that overlaps #2 (touching the same files). Observe the conflict and explain why coupled tasks should not be parallelized.
- **Acceptance criteria:** Three merged PRs, each through branch protection with green checks; `docs/factory/agent-metrics.md` with the per-PR table and a 5-sentence reflection comparing local worktree agents vs cloud agent; `.claude/worktrees/` in `.gitignore`; no secrets in `.worktreeinclude`.
- **Stretch:** Run issue #1 headlessly: `claude -p "<task>" --output-format json --permission-mode dontAsk --allowedTools "Edit,Bash(dotnet test *)"` (verify flag spellings) and parse the JSON result in a script.

## Kata

**"Explain the diff"** (20–30 min, repeat on every agent PR this week). Take an agent-produced PR you did not write. Without asking the agent, write: (1) what changed and why, per file; (2) one behavior that is *not* covered by a test; (3) one risk (security, cost, performance, convention); (4) whether you would merge, and what single check would have caught the biggest issue automatically. Variation: **solo-first** — on alternate days, solve a small task (≤ 30 min) by hand first, then let the agent do it in a fresh worktree and compare approaches.

## Product increment — Fleet Ops Copilot

The repo is agent-ready (AGENTS.md, CLAUDE.md, copilot instructions, a house-pattern skill, guardrails). The first spec-driven feature, **incident intake** (`POST /incidents` → extract → validate → idempotent ticket creation in the mock Ticketing API), was built by a coding agent against human-written acceptance tests; plus three smaller agent-delivered PRs (BG glossary, AI health latency metric, transit-plate normalization).

## Factory increment — your agentic SDLC

Memory files (single source of truth in AGENTS.md), first skill and first custom agent, permission rules and sandbox, `PostToolUse` format/build hook and `Stop` "must be green" hook, protected human-owned tests and golden data, package allowlist + lockfiles + package-age check, branch protection, worktree workflow, cloud-agent delegation, and an agent metrics log (first-pass acceptance, iterations, review time, cost). From now on, product work goes through this factory and is graded on how you direct, constrain and verify agents.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Context design | No or bloated memory files | AGENTS.md exists | Short, curated, single-source memory files + a skill; measured improvement | Instruction vs skill vs hook placement justified; memory files linted and kept current |
| Verification | Trusts agent's claim | Asks agent to run tests | Hooks/CI enforce green; protected human-owned tests | Checks designed so the agent can't pass by weakening them; demonstrated by red-team of own factory |
| Safety & supply chain | Default/bypass modes | Some deny rules | Deny rules + sandbox + allowlist + lockfiles + branch protection | Layered controls each tested by an attempted bypass, documented residual risk |
| Workflow judgment | One giant prompt | Uses plan mode | Ceremony proportional to task; worktrees for independent work; cloud agent for well-specified issues | Can argue when *not* to use an agent or a spec; avoids coupled parallelism |
| Ownership | Can't explain diff | Explains main changes | Explains every file, finds untested behavior | Identifies the missing automatic check and adds it to the factory |

**Auto-checked:** CI on all C4 PRs; protected-file hash check; `lint-agents-md.sh`; `check-packages.sh`; branch protection settings via `gh api`; presence of `agent-readiness.md`, `guardrails.md`, `agent-metrics.md`, `EXPLAIN.md`.

## Common pitfalls

- Copying an enormous "best practices" AGENTS.md from the internet (instruction bloat; Thoughtworks Caution).
- Writing rules in prose that should be hooks or CI checks.
- Letting the agent edit the tests that define done.
- Running `bypassPermissions`/auto-approve outside a container "just this once".
- Parallelizing coupled changes and spending the saved time on merge conflicts.
- Accepting a new package because "it compiles".
- Using agent-generated labels/tests as ground truth.
- Measuring success by PR count or lines changed.


## References

- Claude Code best practices: https://code.claude.com/docs/en/best-practices ; overview: https://code.claude.com/docs/en/overview
- Claude Code memory (CLAUDE.md, AGENTS.md, imports, size guidance): https://code.claude.com/docs/en/memory
- Claude Code permissions and modes: https://code.claude.com/docs/en/permissions ; https://code.claude.com/docs/en/permission-modes ; sandboxing: https://code.claude.com/docs/en/sandboxing
- Claude Code hooks reference: https://code.claude.com/docs/en/hooks ; worktrees: https://code.claude.com/docs/en/worktrees ; headless: https://code.claude.com/docs/en/headless
- AGENTS.md: https://agents.md ; Agent Skills: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Copilot cloud agent + Azure Boards: https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/use-copilot-agents/cloud-agent/integrate-cloud-agent-with-azure-boards ; custom agents in Boards: https://devblogs.microsoft.com/devops/azure-boards-integration-with-github-copilot-includes-custom-agent-support/
- Copilot in Visual Studio, July 2026 update: https://github.blog/changelog/2026-07-30-github-copilot-in-visual-studio-july-update
- `@Test` agent GA: https://devblogs.microsoft.com/dotnet/github-copilot-testing-for-dotnet-available-in-visual-studio/
- Codex DevDay 2026 (TechCrunch): https://techcrunch.com/?p=3171268
- Thoughtworks Technology Radar Vol. 34 digest: https://agentic-ai.readthedocs.io/en/latest/AgenticTechStack/thoughtworks-radar-vol34/
- DORA 2025: https://blog.google/technology/developers/dora-report-2025/ ; AI Capabilities Model (InfoQ): https://infoq.com/news/2026/03/ai-dora-report/
- METR uplift update (Feb 2026): https://metr.org/blog/2026-02-24-uplift-update/
- CSA research note on slopsquatting (USENIX 2025 data): https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419/
- Böckeler, Understanding spec-driven development: https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
