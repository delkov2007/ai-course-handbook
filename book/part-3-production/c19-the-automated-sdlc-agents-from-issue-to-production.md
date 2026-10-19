# C19 — The automated SDLC: agents from issue to production

> **Level:** 3 — Production systems (Advanced) · **Duration:** 14h (theory 25% / labs 75%) · **Prerequisites:** C4 (agent-ready repo), C11 (test-first agents, Stryker.NET, Playwright agents), C14 (eval gates), C15 (tracing, cost), C16 (security gates), C17 (IaC, canary), C18 (governance checks) · **Volatility:** High (coding-agent features, names and billing change monthly; Azure DevOps agent support lags GitHub)

## Why this matters

You have built the Factory piece by piece: memory files and skills (C4), eval tests agents can run (C5, C14), test-first loops with mutation gates (C11), security agents (C16), IaC and canaries (C17), governance checks (C18). In this module the pieces become one closed loop. A dispatcher's complaint becomes a work item, the work item becomes a spec, the spec becomes a pull request written by an agent, and the PR passes a stack of automated gates and a human review before reaching a canary. Production telemetry then watches the canary, and when something degrades an SRE agent opens the next issue.

Getting this wrong is easy and expensive. Teams switch on a cloud agent, see dozens of PRs a week and declare a productivity win, while review queues grow, rework rises, tests pass because they were weakened, and nobody can explain the code in the incident review. The evidence is sobering. DORA 2025 found AI acts as a "mirror and a multiplier" of existing practices. METR's 2025 trial measured experienced developers ~19% *slower* while they believed they were faster, and its February 2026 update concedes developers are probably faster now but calls its own data "very weak evidence" of the size. Thoughtworks puts "coding throughput as a productivity measure" on Caution.

Experts build a *governed delivery system*. Verification is designed before implementation. Spec ceremony is matched to task size. Agents run in sandboxes with least-privilege tokens and cannot weaken their own gates. Humans act as spec owners, orchestrators and reviewers who can defend every merged line. Outcomes are measured (DORA keys, first-pass acceptance, rework, escaped defects, cost per merged PR), not output. This module assembles that system for Fleet Ops Copilot and prepares you for **Gate G3**, which audits both the product and this factory.

## Learning outcomes

1. **Choose** the right level of spec ceremony (none / plan mode / spec-anchored / delta spec) for a given change, and **justify** it using Böckeler's spec-first / spec-anchored / spec-as-source distinction and its critiques.
2. **Configure** an issue-to-PR flow with the Copilot cloud agent (from GitHub Issues and Azure Boards, with custom `.agent.md` agents) and with Claude Code in GitHub Actions, and **compare** them on the same task.
3. **Build** an ordered gate stack (build, tests, mutation, evals, safety/ASR, CodeQL + agentic autofix, supply chain, architecture drift, governance, AI review, human approval, canary) where agents **cannot weaken** their own gates.
4. **Run** parallel agents in git worktrees on decomposable work, and **decide** when parallelism hurts (coupled changes, review bandwidth).
5. **Operate** maintenance agents: Copilot Upgrade agent for modernization, dependency agents, and a docs agent that keeps documentation and the Transparency Note current.
6. **Close** the ops loop with Azure SRE Agent in Reader mode feeding issues back to coding agents, and **specify** when Privileged mode is acceptable.
7. **Measure** the factory with DORA capabilities and agent-specific metrics, **interpret** them against the METR/DORA evidence, and **write** a governance policy for agents in the repo.

## Concepts

### 1. The reference loop

```
Azure Boards / GitHub issue ──► spec (right-sized) ──► coding agent (cloud or local, sandboxed)
        ▲                                                     │ draft PR on agent branch
        │                                                     ▼
 SRE Agent (Reader) ◄── canary + online evals ◄── human approval ◄── gate stack (+ AI review, autofix)
```

Each arrow has an owner. **Humans own:** the intent (issue), the acceptance tests (spec anchor), approval and the decision to promote. **Agents own:** implementation, first-pass review, mechanical fixes (autofix), diagnosis drafts and documentation drafts. **Automation owns:** the gates and the canary controller (C17). The architecture decision for .NET shops: **Azure Boards can send a work item to the Copilot cloud agent, but the PR lands in a GitHub repository.** No evidence was found that this flow targets Azure Repos, and Copilot Autofix for GitHub Advanced Security for Azure DevOps is only in limited preview (since 11 Jun 2026). Teams on Azure Repos get a less mature agent loop. That is a real trade-off for Trakia, whose legacy pipelines live in Azure DevOps; document it in ADR-0019.

### 2. Spec-driven development: useful, contested, right-sized

Birgitta Böckeler (martinfowler.com) distinguishes three levels:
- **Spec-first:** write a spec, use it to generate code, then the spec drifts.
- **Spec-anchored:** the spec is kept and maintained alongside the code for future changes.
- **Spec-as-source:** humans edit only the spec; code is regenerated. Tessl's 1:1 spec-to-file mapping is the example, and regeneration gave non-deterministic output.

Tools:
- **GitHub Spec Kit:** Constitution → Specify → Plan → Tasks, branch per spec, in practice spec-first.
- **Kiro:** Requirements as user stories with GIVEN/WHEN/THEN criteria → Design → Tasks traced to requirements, with steering files `product.md`, `structure.md`, `tech.md`; its GA added property-based testing for spec correctness.
- **OpenSpec:** propose/apply/archive with *delta* specs, suited to brownfield.

Thoughtworks Radar Vol. 34 rates Spec Kit and OpenSpec **Assess** and puts *agent instruction bloat*, *coding agent swarms* and *MCP by default* on **Caution**.

Böckeler's critiques are the reason for skepticism. Kiro turned a small bug into 4 user stories with 16 acceptance criteria. Reviewing verbose Markdown is more tedious than reviewing code. Agents still ignored specs, for example by duplicating existing classes. The approach echoes model-driven development's failure, now with non-determinism added. There is no rigorous comparative evidence that SDD beats plan-mode workflows.

**Course position: spec-anchored, with the anchor executable.** The durable artefact is the human-written acceptance test (xUnit + eval cases), not the prose. The ceremony ladder:

| Change | Ceremony |
|---|---|
| One-line fix, typo, config | Issue text only; agent must add a failing test first |
| Multi-file change in one bounded context | Plan mode; plan posted as PR description before code |
| Feature | Interview → `specs/<id>/SPEC.md` (≤1 page) + human-written acceptance tests + eval cases → fresh agent session implements |
| Brownfield change across modules | Delta spec (OpenSpec style) listing *what changes* against existing behaviour + characterization tests first |

### 3. From issue to PR: the agents

**GitHub Copilot cloud agent** (docs now say "cloud agent" rather than "coding agent"; the URLs moved, but no official rename confirmation was found, so **verify**). You assign an issue to Copilot or prompt it from VS Code, the CLI or Azure Boards. It runs in an **ephemeral GitHub Actions-powered environment with a firewall-controlled internet connection**, runs tests and linters, runs **Copilot code review on its own changes**, and opens a **draft PR on a `copilot/` branch**. It can push only to `copilot/*` branches, and **Actions workflows on its PRs require human approval** to run. **Custom agents** are `.agent.md` profiles (usually `.github/agents/`; org-wide in `.github-private`), each with its own instructions, tools, MCP servers and model; they appear in the Azure Boards agent picker. From Boards, "Create a pull request with Copilot" sends the work item's fields and **last 50 comments**. It requires a paid Copilot plan, the cloud agent enabled on the repo and the Azure Boards GitHub app. Environment preparation (restoring .NET 10 SDK, NuGet from the internal feed, starting SQL for integration tests) goes in the agent's setup workflow *(`copilot-setup-steps.yml` per background knowledge; verify file name and schema)*.

```markdown
---
# .github/agents/fleet-feature.agent.md  (frontmatter keys: verify against current docs)
name: fleet-feature
description: Implements one approved Fleet Ops spec, test-first, within one bounded context.
tools: ["read", "edit", "search", "terminal", "trakia-mcp/schema.*", "trakia-mcp/tickets.read"]
---
You implement exactly one spec in specs/<id>/. Rules:
1. Read SPEC.md and the acceptance tests in tests/Acceptance/<id>/. Never edit those tests or evals/ or .github/.
2. Run `dotnet test tests/Acceptance --filter Spec=<id>` first and confirm it fails for the right reason.
3. Implement; run `dotnet build -warnaserror`, unit tests, then `dotnet test tests/FleetOps.Evals --filter Category=Smoke`.
4. If a tool, prompt or MCP schema changes, update security/tool-manifest.yaml and explain why in the PR.
5. Stop and ask (comment on the issue) if the spec is ambiguous. Do not guess business rules.
```

**Claude Code** gives you a GitHub Actions integration, managed Code Review on PRs, **Routines** (cloud runs triggered by schedule, API or GitHub events) and **headless `claude -p`** with `--output-format json|stream-json`, `--allowedTools` and `--permission-mode dontAsk` for CI. Interactive sessions default to *auto mode* (a classifier reviews actions; since v2.1.283). CI runs should use explicit allow-lists, not auto mode. It reads `AGENTS.md`, so one memory file can serve both ecosystems.

**OpenAI Codex** (comparison): as of DevDay (29 Sep 2026) it has persistent configurable cloud environments, a CLI `/agents` view with worktree support, automatic initial PR reviews and Codex Security Cloud scanning. Thoughtworks rates Codex Trial versus Claude Code and Cursor Adopt.

Teach the **transferable primitives**: memory file, skills, subagents, hooks, MCP, headless mode, cloud agent → PR, AI reviewer. Then map them onto each vendor. Product walkthroughs date within months.

### 4. The gate stack: cheap and deterministic first

| # | Gate | Tooling | Blocking? | Notes |
|---|---|---|---|---|
| 1 | Restore locked, format, analyzers, build | `dotnet restore --locked-mode`, `dotnet format --verify-no-changes`, `-warnaserror` | Yes | Slopsquatting defense from C16 |
| 2 | Unit + property tests | xUnit, FsCheck/CsCheck | Yes | |
| 3 | Acceptance tests for the spec | Human-owned `tests/Acceptance` | Yes | CODEOWNERS-protected |
| 4 | Mutation on changed code | Stryker.NET (`--since`) | Yes, ≥ threshold | Catches hollow tests |
| 5 | Eval suite (cached) | MEAI.Evaluation + `dotnet aieval` report | Yes, per-failure-mode thresholds | Uncached nightly run detects drift (C14) |
| 6 | Safety / ASR | Lab 2 harness (C16), PyRIT nightly **[Python]** | Yes for consequential ASR | |
| 7 | Code scanning & secrets | CodeQL, secret scanning push protection, dependency review, package allow-list | Yes for high/critical | Agentic autofix proposes fixes |
| 8 | Architecture drift | NetArchTest / ArchUnitNET rules from ADRs | Yes | Agents ignore architecture without this |
| 9 | Governance | C18 `governance-check`, tool-manifest test | Yes | |
| 10 | AI code review | Copilot code review / Claude Code review | **Advisory** (blocking only for high-precision categories) | Track comment acceptance rate |
| 11 | Human approval | CODEOWNERS, rulesets, required reviewers | Yes | Agent identities can't approve |
| 12 | Deploy → canary → promote | `azd deploy`, C17 canary controller | Automatic rollback | Environment protection rules |

**Rule zero: agents cannot weaken their own gates.** Put `.github/`, `tests/Acceptance/`, `evals/`, `security/`, `release/canary-criteria.yaml` and `infra/` under CODEOWNERS with required code-owner review in a repository ruleset. Agent-authored commits that touch them need a human owner's approval and a PR label explaining why. Agent tokens are least-privilege (contents/PR write on agent branches only), secrets are not exposed to agent-triggered workflows until a human approves the run, and production deployment uses an environment with required reviewers and OIDC federation (no stored cloud secrets).

**AI code review** catches inconsistencies, missing tests, obvious bugs and security smells cheaply. It misses intent, cross-system effects and business rules. Anthropic notes that reviewers asked to find gaps *will always find some*, which pushes toward over-engineering. Make AI review advisory, give it a narrow checklist (the C16 threat register, tool-manifest rules, logging of personal data), and measure its precision (accepted comments / total).

### 5. Security autofix in the loop

**Agentic autofix for code scanning alerts went GA on 15 Oct 2026.** Copilot explores the relevant files, proposes a fix, **re-runs CodeQL to confirm the alert closes**, iterates, then opens a **draft PR with up to 25 alerts** and the validation steps. Alerts can be assigned via REST (`assignees: ["copilot-swe-agent[bot]"]`). It requires GitHub Code Security or Advanced Security on Enterprise Cloud, with an enterprise policy plus an org/repo setting. Billing is Code Security AI credits plus Actions minutes, and it replaces the free "Generate Fix" button. For **Azure DevOps**, Copilot Autofix for GHAzDO is in **limited preview** (since 11 Jun 2026): CodeQL alerts on the default branch, including C#, at 1 AI credit = $0.01 billed to Azure. Autofix PRs go through the *same* gate stack; a fix that closes the alert but drops a mutation-killing test is still rejected.

### 6. Parallel agents and worktrees

Claude Code supports git worktrees and `/batch`, which fans one change out to 5–30 subagents, each in its own worktree. Codex CLI added worktrees, and Cursor runs up to 8 background agents. Parallelism pays for **independent, mechanical, well-tested** work: migrate 14 MCP tools to the C# SDK 2.0 attribute style, add `gen_ai.*` attributes to every tool span, translate 40 UI strings into Bulgarian. It hurts for **coupled writes**, where agents with partial context make conflicting implicit decisions (Cognition's argument from C12), and it hits a hard limit at **review bandwidth**. If the team can review 6 PRs a day, launching 20 agents only grows the queue and the merge-conflict surface. Thoughtworks cautions against "coding agent swarms" and assesses small, role-specific "teams of coding agents". Pattern: one orchestrator session decomposes the work, N workers run in worktrees with the same gate stack locally (hooks), a reviewer subagent pre-reviews, and a human merges in dependency order.

### 7. Maintenance agents: upgrades, dependencies, docs

- **Copilot Upgrade agent (GitHub Copilot app modernization for .NET):** assess → plan → execute, writing **assessment, plan and tasks files into the repo** for review before execution. It runs in VS, VS Code, Copilot CLI and the cloud agent (which delivers PRs), and accepts custom skills for internal migration patterns. It covers ASP.NET Core, Blazor, Functions, WPF and libraries to .NET 10, and .NET Framework → modern .NET (Windows only). Review the *plan* like an ADR: it is where wrong decisions are cheap to fix.
- **Dependency agents:** Dependabot PRs plus an agent that reads release notes, fixes breaking changes and runs the gate stack. Pin and allow-list as in C16.
- **Docs agents:** keep `docs/` consistent with code (API reference, ADR index, runbooks) and regenerate the metrics section of the Transparency Note (C18) from the latest eval artefacts. Constraints: docs agents cite the source file and line or artefact for every claim, never invent behaviour, and humans approve wording. DORA's AI capabilities model lists *accessible internal knowledge* as a precondition for AI benefit, and docs are context for the next agent run.

### 8. Operations: Azure SRE Agent

Azure SRE Agent investigates incidents and automates remediation. It queries Azure Monitor, Application Insights and Log Analytics, supports custom subagents and MCP connections, and integrates with GitHub and Azure DevOps. **Modes: Reader (read-only) and Privileged (remediation).** Network modes: Unrestricted, Limited or VNet. Regions: Sweden Central, East US 2, Australia East. Billing is in Azure Agent Units, and GA was reported in March 2026 by a secondary source *(verify GA date and pricing from Microsoft)*.

Policy for Trakia: **Reader by default.** It diagnoses, correlates with recent deployments and agent versions, and opens a GitHub issue containing the KQL, trace IDs and suspected change. Privileged actions (restart a revision, roll back traffic, scale) are allowed only when they map to a pre-approved runbook, the action is reversible, and it is logged with the agent's identity (C16). The canary controller (C17) remains the primary rollback mechanism. SRE Agent adds diagnosis, not a second uncontrolled actuator.

### 9. Measuring the factory

**DORA 2025:** ~90% AI adoption (median ~2h/day). AI use is now linked to higher throughput, but ensuring software works before delivery remains a challenge, and AI is "a mirror and a multiplier". Its **AI Capabilities Model** lists seven practices: clear AI policy, healthy data ecosystem, accessible internal knowledge, strong version control and code review, user-centric focus, platform engineering, small batches. Larger changesets raise instability risk, which matters because agents happily produce large diffs. **METR:** the RCT slowdown and the 2026 update both show how hard measurement is, and that perceived speed is not measured speed. **Thoughtworks:** coding throughput on Caution, DORA metrics on Adopt; "lines of code generated is misleading; rework rate exposes blind spots"; codebase cognitive debt on Caution.

Factory scorecard (weekly, from GitHub/ADO APIs + App Insights):

| Metric | Definition | Why |
|---|---|---|
| Deployment frequency, lead time for changes, change failure rate, failed-deployment recovery time | DORA keys | Outcome |
| Rework rate (DORA) | Share of deployments that are unplanned fixes for production issues (verify current DORA definition) | Instability hidden by throughput |
| Code churn | Lines changed again within 21 days of merge, by author type | Hidden cost of fast agent merges |
| First-pass acceptance | Agent PRs merged with ≤1 human revision request | Spec and context quality |
| Iterations per PR | Agent push cycles before green gates | Feedback sensor quality |
| Escaped defects | Prod incidents/bugs traced to PRs, by author type | Quality |
| Mutation score (changed code) | Stryker | Test strength |
| Agent cost per merged PR | Premium requests / tokens / Actions minutes ÷ merged PRs | Economics |
| Review latency & load | Time to first human review; open PRs per reviewer | Bottleneck |
| AI review precision | Accepted AI comments ÷ total | Reviewer trust calibration |

Beware Goodhart's law. Never reward PR counts. Pair every speed metric with a quality metric, and compare agent-authored with human-authored PRs on the same task classes.

### 10. Governance of agents in the repo, and the human role

`docs/governance/agent-policy.md` is a short, enforced document. It covers:
- which agents may run where (local, cloud, CI) and with which tools and MCP servers;
- token scopes;
- sandbox and egress allow-lists;
- data classes agents may see (no production personal data in agent sandboxes; synthetic `TrakiaOps` only);
- approved models and BYOK endpoints (Foundry, EU data zone);
- protected paths;
- attribution (an `Agent-Id` trailer in commits; Agent Trace, an open attribution spec, is on Thoughtworks Assess);
- audit-log retention;
- a kill switch (disable the agent app/identity) and an incident process for agent misbehaviour.

Every rule that matters is backed by a ruleset, hook or test. A policy that is not enforced is decoration.

The human role shifts to **spec owner, orchestrator and reviewer**. Expert habits: design the verification first; manage context deliberately (memory file vs skill vs subagent vs hook vs MCP); pick the ceremony; run unattended agents safely; measure outcomes; **explain every merged line**. To counter cognitive debt, the labs include "explain-the-diff" checks and occasional unaided implementations.

## Tools & versions (as of Oct 2026)

| Tool | Purpose | Status | Notes |
|---|---|---|---|
| GitHub Copilot cloud agent + custom agents (`.agent.md`) | Issue → PR | GA (rename from "coding agent": verify) | Pushes only to `copilot/*`; workflow runs need approval |
| Azure Boards ↔ Copilot integration | Work item → GitHub PR | Available | GitHub repos only; paid plan |
| Copilot code review | AI PR review | GA | Premium requests billing (verify current plans) |
| Agentic autofix for code scanning | CodeQL alert → validated fix PR | **GA 15 Oct 2026** | GHEC + Code Security/GHAS |
| Copilot Autofix for GHAzDO | Same for Azure DevOps | **Limited preview** | $0.01 per AI credit |
| Copilot Upgrade agent (app modernization for .NET) | Assess → plan → execute upgrades | Available | Framework → .NET 10 Windows-only |
| Copilot SDK (`GitHub.Copilot.SDK`) | Build custom factory agents | GA 2 Jun 2026 | Deep dive in D6 |
| Claude Code (CLI, GitHub Actions, Routines, headless) | Local/CI agent, review, triage | GA; agent teams experimental | `claude -p`, `--allowedTools`, `dontAsk` |
| OpenAI Codex | Comparison agent | GA; Thoughtworks Trial | DevDay 29 Sep 2026 features |
| GitHub Spec Kit / OpenSpec / Kiro | Spec-driven workflows | Thoughtworks **Assess** | Teach critically |
| Stryker.NET, FsCheck/CsCheck, NetArchTest/ArchUnitNET | Mutation, property, architecture gates | OSS | Pin versions |
| MEAI.Evaluation + `dotnet aieval` | Eval gate | Verify package versions | From C14 |
| Azure SRE Agent | Incident diagnosis/remediation | GA reported Mar 2026 (verify) | Reader/Privileged; 3 regions |
| Playwright test agents | E2E planner/generator/healer | Available | From C11; review healer diffs |

## Labs

### Lab 1 — One feature, two agents, right-sized spec (≈3h)

- **Goal:** Deliver "Driving-time compliance check" (Fleet Assistant warns a dispatcher when a proposed maintenance trip would breach EU driving-time limits for the assigned driver) via the full loop, implemented once by the Copilot cloud agent and once by Claude Code in Actions.
- **Start state:** tag `c19/lab1-start` (C18 increment plus `specs/` and `tests/Acceptance/` folders, CODEOWNERS).
- **Steps:**
  1. Create the work item in Azure Boards (or a GitHub issue form for GitHub-only cohorts). Choose the ceremony level and justify it in the issue: this is a *feature* → `SPEC.md` ≤1 page.
  2. Run an interview session with your local agent to draft `specs/0042-driving-time/SPEC.md`. Then **write the acceptance tests yourself**: 8 xUnit cases over the rules summary in the corpus (daily limit, weekly limit, breaks), plus 6 eval cases (one per failure mode from C14 that applies, incl. a Bulgarian question).
  3. Add `.github/agents/fleet-feature.agent.md` (Concepts §3) and the setup workflow (restore from internal feed, start SQL container).
  4. From Boards, "Create a pull request with Copilot" with the `fleet-feature` agent. In parallel, trigger the Claude Code workflow on a twin issue:
  ```yaml
  # .github/workflows/claude-implement.yml (action inputs: verify against the pinned major version)
  on:
    issues: { types: [labeled] }
  jobs:
    implement:
      if: github.event.label.name == 'agent:claude'
      runs-on: ubuntu-latest
      permissions: { contents: write, pull-requests: write, issues: write, id-token: write }
      steps:
        - uses: actions/checkout@<pinned-sha>
        - uses: actions/setup-dotnet@<pinned-sha>
          with: { dotnet-version: '10.0.x' }
        - uses: anthropics/claude-code-action@<pinned-sha>
          with:
            prompt: "Implement the spec referenced in issue #${{ github.event.issue.number }} following AGENTS.md. Never modify tests/Acceptance, evals, .github or security."
            claude_args: >-
              --allowedTools "Read,Edit,Grep,Glob,Bash(dotnet build:*),Bash(dotnet test:*)"
              --permission-mode dontAsk --max-turns 60
          # model access via Foundry/Bedrock/Vertex or API key secret per org policy (verify supported auth inputs)
  ```
  5. Compare both PRs: gate results, iterations, cost, diff size, and whether either touched protected paths.
- **Break it:** Write an ambiguous acceptance criterion ("long trips need a break") and observe which agent asks and which guesses. Then fix the spec, not the code.
- **Acceptance criteria:** Both PRs exist and are linked to the work item; acceptance tests and eval smoke pass on at least one; a comparison table (`docs/factory/agent-comparison-0042.md`) with measured numbers; you can explain every line of the PR you merge (instructor spot-check of 3 random hunks).
- **Stretch:** Re-run the same feature through Spec Kit (Constitution → Specify → Plan → Tasks) and record review time and spec length versus your one-page spec.

### Lab 2 — The gate stack, unweakenable (≈3h)

- **Goal:** A single `pr-gates` workflow and repository ruleset implementing Concepts §4.
- **Start state:** `c19/lab2-start` (separate workflows from earlier modules).
- **Steps:**
  1. Consolidate into `pr-gates.yml` with jobs ordered cheap → expensive and `needs:` dependencies:
  ```yaml
  name: pr-gates
  on: { pull_request: { branches: [main] } }
  permissions: { contents: read, pull-requests: write, security-events: write, id-token: write }
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@<pinned-sha>
        - uses: actions/setup-dotnet@<pinned-sha>
          with: { dotnet-version: '10.0.x' }
        - run: dotnet restore --locked-mode
        - run: dotnet format --verify-no-changes
        - run: dotnet build -warnaserror --no-restore
        - run: dotnet test tests/FleetOps.Tests tests/Acceptance --no-build
        - run: dotnet test tests/Architecture tests/Governance tests/Security.ThreatModel --no-build
    mutation:
      needs: build
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@<pinned-sha>
          with: { fetch-depth: 0 }
        - uses: actions/setup-dotnet@<pinned-sha>
          with: { dotnet-version: '10.0.x' }
        - run: dotnet tool restore && dotnet stryker --since:main --break-at 70   # verify flag names for pinned Stryker.NET
    evals:
      needs: build
      runs-on: ubuntu-latest
      environment: evals            # OIDC federated credential to the eval Foundry project; no stored keys
      steps:
        - uses: actions/checkout@<pinned-sha>
        - uses: actions/setup-dotnet@<pinned-sha>
          with: { dotnet-version: '10.0.x' }
        - uses: azure/login@<pinned-sha>
          with: { client-id: '${{ vars.EVAL_CLIENT_ID }}', tenant-id: '${{ vars.TENANT_ID }}', subscription-id: '${{ vars.SUB_ID }}' }
        - run: dotnet test tests/FleetOps.Evals --filter "Category=Gate"   # cached responses; thresholds in evals/thresholds.json
        - run: dotnet aieval report --path ./eval-results --output ./eval-report   # verify CLI arguments
        - uses: actions/upload-artifact@<pinned-sha>
          with: { name: eval-report, path: ./eval-report }
    asr:
      needs: build
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@<pinned-sha>
        - uses: actions/setup-dotnet@<pinned-sha>
          with: { dotnet-version: '10.0.x' }
        - run: dotnet run --project tools/AsrHarness -- --suite indirect --cached --fail-on-consequential
  ```
  2. Enable CodeQL (C#) with default setup, secret scanning push protection, dependency review, and **agentic autofix** (enterprise policy + repo setting). Assign two seeded alerts to Copilot via REST.
  3. Add NetArchTest rules derived from ADRs (e.g., `FleetOps.Agents` must not reference `Microsoft.Data.SqlClient` directly; data access only via the MCP server or repository layer).
  4. Configure the repository ruleset: required status checks (all jobs), required code-owner review for protected paths, no bypass for bot actors, linear history.
  5. Enable advisory AI review (Copilot code review or Claude Code review) with a checklist prompt referencing `security/threat-register.csv` and `docs/governance/agent-policy.md`.
- **Break it (three attacks):** (a) ask the cloud agent to "make the failing eval pass" for an intentionally hard case and watch whether it edits `evals/thresholds.json`; (b) a PR that deletes an assertion, so mutation score drops; (c) an autofix PR that closes a CodeQL SQL-injection alert by removing the feature's validation test. All three must be blocked by gates or rulesets, not by luck.
- **Acceptance criteria:** Ruleset export committed (`.github/rulesets/main.json`); the three attack PRs are blocked with the expected gate names; a clean PR goes green in under 20 minutes; autofix produced at least one validated draft PR that passed the full stack.
- **Stretch:** Measure AI review precision on 15 PRs and tune its checklist.

### Lab 3 — Parallel agents and maintenance agents (≈2h)

- **Goal:** Use parallelism where it fits and run upgrade/docs agents under the same gates.
- **Start state:** `c19/lab3-start`, including `legacy/DepotKiosk` (a .NET Framework 4.8 WinForms depot check-in app) and 14 MCP tools still using an older SDK attribute style.
- **Steps:**
  1. (≈45 min) Decompose the MCP tool migration into independent units, then migrate **4 of the 14 tools** in parallel with Claude Code worktrees/`/batch` (or 4 parallel cloud-agent issues), with a reviewer subagent pre-reviewing each PR. Merge in dependency order. The remaining 10 tools are stretch/homework.
  2. (≈30 min, timeboxed) Deliberately try parallelism on a *coupled* change: two agents each adding a field to `IncidentReport` and its serializer and eval cases (UI out of scope). Record the conflicts and the inconsistent decisions; do not resolve them beyond the write-up.
  3. (≈25 min) Run the Copilot Upgrade agent on `legacy/DepotKiosk` (Windows runner or VS 2026) through **assessment and plan only**. Review its assessment, plan and tasks files; reject or amend at least one plan step with a reason. Execution is stretch.
  4. (≈20 min) Run the **provided** docs agent workflow (`.github/workflows/docs-agent.yml`, scheduled Action) once: it regenerates `docs/api/`, the ADR index and the Transparency Note metrics section from artefacts, with citations, as a PR. Review the PR; adding a Routine variant is stretch.
- **Break it:** Give the docs agent a stale eval artefact. The staleness check from C18 must flag it rather than publishing old numbers.
- **Acceptance criteria:** 4 migration PRs merged green, with human review time per PR logged; the coupled-change experiment write-up (≤300 words) with the conflict count; Upgrade agent plan review comments committed; docs PR with per-claim citations passes `tests/Docs` link/citation checks, and the stale-artefact run is flagged.
- **Stretch:** Migrate the remaining 10 tools and compute review-queue time versus number of parallel agents to find your team's saturation point; execute the reviewed Upgrade plan on `DepotKiosk`; author the docs agent as a weekly Routine.

### Lab 4 — Ops loop: SRE Agent → issue → fix → canary (≈1.5h)

- **Goal:** Close the loop from production signal to agent-made fix.
- **Start state:** `c19/lab4-start`, deployed `prod-sim` (C17) with SRE Agent connected in **Reader** mode (Sweden Central).
- **Steps:**
  1. The instructor ships a canary with a regression: a new SQL index hint in Fleet Analyst raises p95 latency 4× for Varna queries, and tool error rate rises.
  2. SRE Agent investigates App Insights/Log Analytics and opens a GitHub issue with KQL, trace IDs, the suspected deployment and the agent version.
  3. Triage as human: confirm, add an acceptance test reproducing the slow query plan (or an eval latency budget), and label it for the cloud agent.
  4. The cloud agent fixes it; the full gate stack runs; the C17 canary controller promotes.
- **Break it:** Temporarily switch SRE Agent to **Privileged** in a sandbox subscription and ask it to "fix it". Record exactly what it would change and argue whether that action fits the runbook policy.
- **Acceptance criteria:** Issue created by the SRE Agent contains reproducible evidence; MTTR (detection → promoted fix) recorded; the fix PR includes a regression test; the agent-policy decision on Privileged mode is documented.
- **Stretch:** Connect SRE Agent to the Trakia MCP server (read-only tools) and evaluate whether diagnosis improves.

### Lab 5 — Measure and govern the factory (≈1h)

- **Goal:** A factory scorecard and an enforced agent policy, ready for Gate G3.
- **Start state:** `c19/lab5-start` with a script skeleton querying the GitHub/ADO APIs.
- **Steps:**
  1. Compute the scorecard (Concepts §9) for the last 4 weeks of your repo, split by agent- versus human-authored PRs.
  2. Write `docs/governance/agent-policy.md` and link every rule to its enforcement (ruleset, hook, test, Azure Policy).
  3. Present a one-slide interpretation: which metric would you act on, and which looks good but is misleading?
- **Break it:** The instructor adds 30 trivial agent PRs (README edits). Show how PR count and throughput jump while first-pass acceptance and rework reveal nothing improved.
- **Acceptance criteria:** Scorecard JSON + workbook committed; every policy rule has an enforcement link (checked by `tests/Governance/PolicyEnforcementTests`); the interpretation explicitly references DORA's amplifier finding or METR's measurement caveat.
- **Stretch:** Add cost per merged PR from Copilot premium-request and Actions usage exports.

## Kata

**"Ceremony and gate call" (20 min, repeat 5×).** Draw a change card (e.g., "rename a config key", "add a new MCP tool that sends SMS to drivers", "upgrade MEAI to the next minor", "change the incident triage prompt", "bump the frontier model version"). Decide: (1) ceremony level; (2) which agent (local, cloud, batch) or none; (3) which gates from the stack must run and which new ones are needed (e.g., the SMS tool needs a tool-manifest entry, HITL and an ASR scenario); (4) promotion path (direct, canary, shadow). Compare with a peer; disagreements must be resolved by citing a concept from C11–C18.

## Product increment — Fleet Ops Copilot

Fleet Ops Copilot is now delivered by an end-to-end automated, governed SDLC:
- the driving-time compliance feature, shipped through spec → agent PR → gates → human approval → canary;
- the MCP tools migrated by parallel agents;
- the legacy DepotKiosk on a reviewed upgrade path;
- docs and the Transparency Note regenerated by a docs agent;
- an SRE Agent (Reader) watching production and feeding issues back into the loop.

## Factory increment — your agentic SDLC

The Factory is complete for the core:
- Boards/Issues → Copilot custom agents and Claude Code Actions;
- a consolidated `pr-gates` workflow (build, tests, acceptance, mutation, evals, ASR, CodeQL + agentic autofix, supply chain, architecture, governance, advisory AI review);
- rulesets and CODEOWNERS that agents cannot bypass;
- an OIDC-only deployment with environment approvals and the eval-gated canary;
- parallel-agent and maintenance-agent playbooks;
- an SRE Agent ops loop;
- a factory scorecard and an enforced `agent-policy.md`.

D6 extends this with your own agent tooling; A7 governs it at team and programme level.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Spec & orchestration | Prompts agents ad hoc | Uses specs | Right-sized ceremony; human-owned executable anchors | Diagnoses spec ambiguity from agent behaviour; minimal specs, high first-pass acceptance |
| Gate design | Build + tests | Most gates present | Ordered stack, protected paths, OIDC, autofix in loop | All three attack PRs blocked; gates fast (<20 min); measured AI-review precision |
| Parallel & maintenance agents | Sequential only | Runs parallel agents | Decomposes well, avoids coupled parallelism, reviews upgrade plans | Finds review saturation point; agents' outputs cited and verifiable |
| Ops loop | Manual incident handling | SRE Agent reads | Reader-mode loop to fix PR with regression test | Privileged-mode policy argued with runbooks and reversibility |
| Measurement & governance | PR counts | DORA keys | DORA + agent metrics split by author type | Interprets against METR/DORA evidence; every policy rule enforced |

**Auto-checked:** `pr-gates` status on clean and attack PRs, ruleset export, policy-enforcement tests, docs citation tests, scorecard schema. **Gate G3** (see gates.md) lets you bring this factory into the operated environment (Blocks A–C) and draws Block D challenge questions from your evidence pack, including the governance artefacts. Learners must be able to demonstrate the full loop live.

## Common pitfalls

- Measuring success by agent PR volume.
- Specs longer than the code they produce; prose specs without executable anchors.
- Letting agents edit tests, eval thresholds or workflows "to get green".
- Running CI agents in auto/permissive modes with broad tokens and secrets available before human approval.
- Making AI review blocking for everything, which trains humans to ignore it, or for nothing, which wastes it.
- Launching more parallel agents than the team can review.
- Accepting upgrade-agent output without reviewing its plan files.
- Giving SRE Agent Privileged mode "to save time" without runbooks.
- Assuming Azure Repos has feature parity with GitHub for agent flows.
- Merging code no human can explain, which builds cognitive debt that surfaces at the next incident.


## References

- Böckeler, Understanding spec-driven development: Kiro, spec-kit and Tessl: https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- Thoughtworks Technology Radar Vol. 34 digest: https://agentic-ai.readthedocs.io/en/latest/AgenticTechStack/thoughtworks-radar-vol34/
- Azure Boards → Copilot cloud agent: https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/use-copilot-agents/cloud-agent/integrate-cloud-agent-with-azure-boards ; custom agent support: https://devblogs.microsoft.com/devops/azure-boards-integration-with-github-copilot-includes-custom-agent-support/
- Copilot coding/cloud agent overview (secondary, Mar 2026): https://www.morphllm.com/copilot-coding-agent
- Agentic autofix for code scanning GA (15 Oct 2026): https://github.blog/changelog/2026-10-15-agentic-autofix-for-code-scanning-alerts-general-availability
- Copilot Autofix for GHAzDO (**limited preview**): https://devblogs.microsoft.com/devops/copilot-autofix-for-github-advanced-security-for-azure-devops/
- Modernize .NET anywhere with GitHub Copilot (Upgrade agent): https://devblogs.microsoft.com/dotnet/modernize-dotnet-anywhere-with-ghcp/
- GitHub Copilot testing for .NET (`@Test`): https://devblogs.microsoft.com/dotnet/github-copilot-testing-for-dotnet-available-in-visual-studio/
- Copilot SDK GA: https://github.blog/changelog/2026-06-02-copilot-sdk-is-now-generally-available/
- Claude Code overview: https://code.claude.com/docs/en/overview ; best practices: https://code.claude.com/docs/en/best-practices
- Codex at DevDay 2026 (TechCrunch): https://techcrunch.com/?p=3171268
- Azure SRE Agent FAQ: https://learn.microsoft.com/en-us/azure/sre-agent/faq ; GA/pricing (secondary): https://www.licensingschool.co.uk/licensing-blog/2026/03/25/azure-sre-agent/
- DORA 2025: https://blog.google/technology/developers/dora-report-2025/ ; AI Capabilities Model: https://infoq.com/news/2026/03/ai-dora-report/
- METR uplift update (Feb 2026): https://metr.org/blog/2026-02-24-uplift-update/
- Playwright test agents: https://playwright.dev/docs/test-agents
- CSA slopsquatting note: https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419/
- Cognition, Don't Build Multi-Agents: https://cognition.ai/blog/dont-build-multi-agents
