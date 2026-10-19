# C11 — Agentic testing: AI-driven TDD, mutation & E2E test agents

> **Level:** 2 — Building blocks (Intermediate) · **Duration:** 14h (theory 30% / labs 70%) · **Prerequisites:** C4 (agent-ready repo, plan → implement → verify, permissions), C5 (evals in CI), C7–C10 (the product code you will now test); Node.js LTS installed (Playwright test agents) · **Volatility:** High

## Why this matters

By now coding agents write most of Fleet Ops Copilot's code. Ask one to "add tests" and it will happily produce 140 green tests and a coverage report showing 87%. Then run a mutation tester: flip `>` to `>=` in the EU driving-time validator, delete the line that adds the 45-minute break, return `null` from the slot planner — and two-thirds of those mutants survive. The tests execute the code; they don't check it. Worse, because the agent wrote the tests *after* the code, the tests faithfully encode the current behaviour, bugs included: the off-by-one in the weekly driving limit now has a test asserting it.

In an agentic SDLC, tests stop being only a quality artifact and become the **agent's oracle** — the executable definition of "done" that a coding agent iterates against. If the oracle is weak, every agent iteration converges on the wrong thing, faster. Thoughtworks Radar Vol. 34 puts two practices in Trial for exactly this reason: **mutation testing** ("catches hollow tests that high coverage can hide") and **feedback sensors for coding agents** (compilers, linters, tests run during the session). Anthropic's own guidance is to write a failing test first and to split test-writer and implementer into separate sessions.

Experts design verification first. Humans own the assertions for behaviour that matters; agents implement against them and generate the long tail of tests; mutation score — not line coverage — measures whether tests can catch bugs; property-based tests explore inputs nobody thought of; E2E test agents explore the UI but their "healing" is reviewed like product code; and LLM features are tested statistically in a separate lane, never with exact-string assertions. This module builds that test system for the product and makes it the backbone of your Factory.

## Learning outcomes

By the end of this module you can:

1. **Design** a test strategy for an LLM-based product that separates deterministic tests, contract tests, LLM-feature evals and E2E tests, with appropriate gates and cadences for each.
2. **Run** an AI-driven TDD loop: write acceptance tests as the spec, have a coding agent implement in a separate session with tests protected from modification, and verify.
3. **Generate** tests with the Visual Studio 2026 `@Test` agent and with CLI/cloud coding agents, and **audit** them with Stryker.NET mutation testing.
4. **Direct** an agent to kill surviving mutants, distinguishing real test gaps from equivalent mutants.
5. **Write** property-based tests with FsCheck or CsCheck for domain rules and for the retrieval/SQL components built in C6–C10.
6. **Set up** Playwright test agents (planner, generator, healer) for the Fleet Ops UI and **govern** healer changes so tests don't adapt to regressions.
7. **Implement** contract tests for the mock REST APIs and the MCP server, and synthetic test-data generation that is GDPR-safe and reproducible.
8. **Configure** CI gates (mutation threshold on changed code, eval gates, E2E smoke, flaky-test policy, protected test paths) and **report** agent-relevant quality metrics.

## Concepts

### Tests as the oracle for agents

A coding agent's loop is: read context → change code → run feedback sensors → iterate until the sensors are green or it gives up. The sensors are the build, analyzers, tests and evals. Three consequences:

1. **The agent optimizes for the sensors you give it.** If "green" is achievable by weakening an assertion, an agent under pressure will sometimes do exactly that. Protect the assertions that encode requirements.
2. **Test-after generation encodes current behaviour.** Tests generated from existing code are characterization tests: useful as a regression net for refactoring, useless as evidence of correctness.
3. **Fast, deterministic sensors make agents better.** A 40-second unit suite is run on every iteration; a 25-minute E2E suite is not. Structure the pyramid so the agent's inner loop is fast and meaningful.

### AI-driven TDD workflow

1. **Spec as examples.** For a behaviour that matters, a human writes acceptance tests (xUnit) from the requirement — often with the agent's help drafting cases, but the human decides the expected values. Choose the ceremony level (C4): a bug fix needs one failing reproduction test; a feature needs an acceptance test file plus a short SPEC.md.
2. **Protect the oracle.** Implementer sessions may not edit acceptance tests: enforce with agent permissions (deny edit/write on `tests/**/Acceptance/**`), a pre-tool hook, and in CI a CODEOWNERS rule requiring human review for changes there.
3. **Separate sessions.** Test writer and implementer are different sessions (or subagents) so the implementer can't "see" how the tests were reasoned and the tester can't bend tests toward an implementation.
4. **Implement until green** with the inner loop: build → unit tests → analyzers.
5. **Strengthen**: mutation testing on changed code; agent adds tests to kill surviving mutants (it may add tests, not change acceptance tests); property-based tests for invariants.
6. **Review**: the human explains and defends the diff (counter to "codebase cognitive debt", Thoughtworks Caution).

### Test generation with agents

- **VS 2026 `@Test` agent** (GitHub Copilot testing for .NET, GA in Visual Studio 2026 v18.3 on 11 Feb 2026): generates tests for a member, class, file, project, solution or the current git diff; creates the test project if needed; builds, runs, fixes and reruns until stable; reports coverage before/after, testability gaps and unstable tests; accepts targets like "80% coverage"; needs a paid Copilot plan; framework support beyond the xUnit example in the announcement is not documented — verify.
- **CLI / cloud agents** (Claude Code, Copilot CLI and cloud agent, Codex): same generation, scriptable in CI, can follow your test conventions from AGENTS.md and skills.
- Risks: coverage-chasing (tests that call code without meaningful assertions), tautologies (`Assert.Equal(sut.Compute(x), sut.Compute(x))`), over-mocking (testing the mock), snapshotting current bugs, flaky time/culture-dependent tests (Bulgarian culture `bg-BG` decimal comma breaks naïve string parsing — a real Trakia bug class).
- Policy: generated tests are welcome for coverage of the long tail and characterization before refactors; they are accepted only with a **mutation score** on the code they claim to cover.

### Mutation testing with Stryker.NET

A mutation tester makes small changes (mutants) to production code — arithmetic, equality and boundary operators, boolean logic, string and LINQ mutations, null-coalescing, removed statements — and runs the tests. A mutant is **killed** if some test fails, **survives** if all pass. **Mutation score** = killed / (killed + survived) (timeouts usually count as killed; no-coverage mutants count against you — verify Stryker's exact formula in your version). It measures the fault-detection power of tests, which coverage cannot.

Practicalities:

- `dotnet tool install dotnet-stryker` (local tool manifest), run `dotnet stryker` in the test project directory; HTML and JSON reports.
- Thresholds `high` / `low` / `break` in `stryker-config.json`; `break` fails the run below the score.
- Mutation testing is slow (it re-runs tests per mutant). Use **diff-based runs** on PRs (`since` the target branch) and a baseline for full runs nightly.
- **Equivalent mutants** (changes that don't alter observable behaviour) exist; mark them with Stryker's ignore comments plus a justification — reviewed, never bulk-ignored by an agent.
- Target domain logic and validators (driving-time rules, slot planner, SQL validator, citation validator, RRF), not generated DTOs or framework glue.

The agent loop "here are the surviving mutants, add tests that kill them, don't change production code" is one of the highest-value uses of a coding agent in testing.

### Property-based testing

Instead of examples, you state **properties** that must hold for all inputs and the framework generates hundreds of inputs, then **shrinks** a failing input to a minimal counterexample. .NET options: **FsCheck** (xUnit integration via `[Property]`) and **CsCheck** (C#-first generators, `Sample`, built-in shrinking). Kiro's GA added property-based testing to check spec correctness — the idea that properties are the most compact spec is spreading into agent tooling.

Good Trakia properties:

- Driving-time validator (EU rules as implemented in Trakia policy: e.g., 4.5 h driving → 45 min break; daily driving ≤ 9 h, extendable to 10 h twice per week; weekly ≤ 56 h; two-week ≤ 90 h — the lab spec is the source of truth): converting a driving segment into rest of the same duration, with all timestamps unchanged, never creates a weekly (56 h) or two-week (90 h) violation and never lengthens any continuous-driving run (invariant **INV-1** in `docs/specs/driving-time.md`); parsing the serialised activity log round-trips to identical violations; violations are invariant to time-zone representation. Beware the tempting "adding rest never adds violations": under the daily rules extra rest can create a new (reduced) daily rest, re-partition driving days and count against reduced-rest or extended-day allowances — a property must be derived from the spec, not from intuition.
- RRF (C7): result is a permutation of the union; a document ranked first in every list is ranked first overall; deterministic for equal inputs.
- SQL validator (C10): any statement containing DML/DDL anywhere is rejected (fuzz with generated statement compositions).
- Result-set comparer (C10): symmetric; invariant under row permutation; reflexive.
- Citation validator (C7): never accepts a source ID not in the retrieved set.

### Playwright test agents

Playwright ships three test agents:

- **Planner** explores the app from a seed test (and optional PRD) and writes Markdown test plans in `specs/`.
- **Generator** turns plans into Playwright tests, validating selectors live against the running app.
- **Healer** reruns failing tests, inspects the UI for equivalent elements, and patches the test — or skips it if the feature itself appears broken.

Setup: `npx playwright init-agents --loop=<vscode|claude|codex|opencode>`; **re-run after each Playwright update**; VS Code needs v1.105 or later. The agents run in Node; Fleet Ops' UI is Blazor/ASP.NET, which Playwright tests through the browser like any web app.

**The healer's core risk:** it can "fix" a test to match a regression — a renamed button is a locator change, but a booking form that no longer requires the approval checkbox is a bug, and a healer may happily update or skip the test. Governance: healer diffs go through PR review like product code; a guard script flags any change to assertions (`expect(...)` lines) or new `test.skip`/`fixme`; track **healer skip rate** and **assertion-change rate** as metrics.

**LLM UIs in E2E tests:** never assert generated text. Run E2E against a **deterministic fake `IChatClient`** (scripted responses keyed by scenario) for UI flows — streaming rendering, citation chips, approval cards, error states — and keep a handful of live-model smoke tests that assert structure (a citation chip exists, the approval card shows a slot ID), not wording.

### Contract tests

Agents change interfaces confidently. Contracts catch it:

- **OpenAPI contract tests** for the mock Ticketing, Scheduling and Parts APIs: a generated client + response schema validation against the spec; provider tests verifying the mock (and later the real API) honours the spec. Consumer-driven contracts with Pact (PactNet) are an option — not researched for this course; verify maturity before adopting.
- **MCP contract**: `tools.snapshot.json` from C8 (names, descriptions, input/output schemas) — snapshot test fails on unreviewed change; ties into definition pinning.
- **Prompt and tool-schema contracts**: structured-output schemas (C3) and agent tool sets (C9) are versioned and snapshot-tested.

### Testing LLM features vs deterministic code

| Aspect | Deterministic code | LLM feature |
|---|---|---|
| Assertion | Exact | Schema + code checks + calibrated judges |
| Unit of result | Pass/fail per test | Pass rate over a dataset; pass^k |
| Determinism | Yes | No — cache responses for PR runs (MEAI response caching), uncached nightly for drift |
| Speed / cost | Milliseconds, free | Seconds, tokens |
| Lane in CI | `unit`, `integration` | `evals` (C5, C7, C9, C10), separate job, separate thresholds |
| Orchestration logic around the model | Test with a **fake `IChatClient`** — deterministic | — |

Keep the agent's inner loop on deterministic lanes plus cached evals; never let a coding agent "fix" an eval regression by editing the golden set (protected path, like acceptance tests).

### Test data generation

- **Never copy production data** into tests (GDPR); Trakia data is synthetic by design.
- Deterministic generators with fixed seeds (e.g., Bogus — general knowledge, verify current version) for structured entities.
- LLM-generated realistic text (BG/EN incident reports, driver messages) using the dimension-tuple method: define dimensions (vehicle type, fault severity, language, writing style, presence of PII, injection attempt yes/no), hand-write ~20 tuples, generate more tuples, then convert each tuple to text in a **separate** step; human-review a sample. Synthetic data shows coverage, not production frequency.
- Snapshot databases with pinned clocks (C10) for reproducible integration and eval tests.

### CI gates and metrics

Pipeline (GitHub Actions; Azure Pipelines equivalent in the stretch):

1. Build + analyzers + `dotnet format --verify-no-changes`.
2. Unit + property tests (fast lane).
3. Integration tests with Testcontainers (SQL Server 2025, WireMock for APIs).
4. Contract tests (OpenAPI, MCP snapshot).
5. Stryker on changed projects (`since` target branch) — **break threshold on changed code**.
6. Cached eval lanes (RAG, agent, SQL).
7. E2E smoke (fake LLM) on PR; full Playwright + live-model smoke nightly.
8. Policy checks: protected paths (acceptance tests, golden sets, eval thresholds) changed only with CODEOWNERS approval; healer-diff guard; dependency allow-list (slopsquatting — 19.7% of 2.23M AI code samples referenced hallucinated packages in a USENIX 2025 study).

Metrics: mutation score (changed code and overall), escaped defects, flaky-test rate, healer skip/assertion-change rate, first-pass acceptance of agent PRs, rework rate. Coverage is reported, not gated.

### Misconceptions to unlearn

- "87% coverage means well tested." Coverage measures execution, not checking.
- "The agent wrote tests and they pass, so the feature works." The tests may encode the bug.
- "Self-healing tests reduce maintenance." They also reduce detection unless governed.
- "LLM features can't be tested." They can — statistically, in their own lane.
- "Mutation testing is too slow for CI." Diff-based runs on PRs, full runs nightly.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| Visual Studio 2026 v18.3+ `@Test` agent | Generate/run/fix .NET tests, coverage targets | GA (11 Feb 2026) | Paid Copilot plan |
| Claude Code / Copilot CLI & cloud agent / Codex | Test writing, implementation, mutant-killing loops | GA (feature sets churn) | Map primitives, not UIs |
| Stryker.NET (`dotnet-stryker`) | Mutation testing | OSS, mature | Verify config keys (`since`, thresholds) for your version |
| FsCheck (+ FsCheck.Xunit) / CsCheck | Property-based testing | OSS | Pick one per repo |
| xUnit / MSTest / NUnit | Test frameworks | GA | Lab repo uses xUnit |
| Testcontainers for .NET | SQL Server 2025, dependencies in tests | OSS | |
| WireMock.Net | HTTP API stubs | OSS | |
| Playwright Test + test agents | Planner / Generator / Healer | GA (agents: re-init after updates) | `npx playwright init-agents --loop=…`; VS Code ≥ 1.105; **Node.js** |
| `Microsoft.Extensions.AI.Evaluation` (+ caching, `dotnet aieval`) | LLM-feature lanes | GA | From C5 |
| Pact (PactNet) | Consumer-driven contracts | OSS | Not researched — verify before adopting |
| Bogus | Synthetic structured data | OSS | Verify version |

## Labs

### Lab 1 — Test-first with a protected oracle (≈2h)

- **Goal:** Run a full AI-driven TDD loop where the agent cannot move the goalposts.
- **Start state:** `c11/lab1-start` — `FleetOps.Domain` with an empty `DrivingTimeValidator` and `MaintenanceSlotPlanner`; `docs/specs/driving-time.md` (Trakia policy restating EU driving and rest rules with examples, including multi-day and week-boundary cases, plus numbered invariants such as INV-1 used by the Lab 3 properties).
- **Steps:**
  1. Write `tests/FleetOps.Tests/Acceptance/DrivingTimeValidatorTests.cs` yourself: 15–20 cases from the spec (normal day, 4.5 h without break, split break 15+30, two 10-hour days in a week then a third, 56 h weekly, 90 h fortnight, week boundary in Europe/Sofia with DST). Expected violations are yours.
  2. Protect the oracle:
     ```jsonc
     // .claude/settings.json (verify current permission rule syntax)
     { "permissions": { "deny": [ "Edit(tests/**/Acceptance/**)", "Write(tests/**/Acceptance/**)",
                                  "Edit(evals/golden/**)" ] } }
     ```
     plus a `PreToolUse` hook script that blocks the same paths (defence in depth), and `CODEOWNERS`: `/tests/**/Acceptance/ @trakia/domain-owners`.
  3. New session: "Implement `DrivingTimeValidator` until the acceptance tests pass. Do not modify tests. Run `dotnet test` after each change." Record iterations, tokens, time.
  4. Repeat for `MaintenanceSlotPlanner` with the roles swapped: the agent drafts acceptance cases from the spec in session A, you review and correct expected values, a fresh session B implements.
- **Break it:** Remove the deny rule and hook, and give an underspecified instruction ("make the build green quickly"). Inspect whether the agent edits a test. Restore protections; confirm the CI CODEOWNERS check would have caught it.
- **Acceptance criteria:** All acceptance tests green with zero diff under `tests/**/Acceptance/**` in the implementer's commits (CI check); hook test proves blocked edits; `docs/factory/agent-log.md` records iterations and any attempted test edits.
- **Stretch:** Run the implementer headless in CI (`claude -p` or Copilot CLI) on a branch and have it open a PR.

### Lab 2 — Generated tests under the mutation microscope (≈2.5h)

- **Goal:** Measure the real strength of AI-generated tests and fix it with an agent.
- **Start state:** `c11/lab2-start` — existing untested components from earlier modules: `CitationValidator` (C7), `RetrievalMetrics` (C6), `SqlValidator` and `ResultSetComparer` (C10), `BudgetMiddleware` (C9).
- **Steps:**
  1. Generate tests for these components with the VS 2026 `@Test` agent targeting 80% coverage (or a CLI agent with the same instruction if you lack VS). Record coverage.
  2. Configure Stryker.NET:
     ```json
     {
       "stryker-config": {
         "project": "FleetOps.Core.csproj",
         "thresholds": { "high": 85, "low": 75, "break": 70 },
         "mutation-level": "Standard",
         "reporters": [ "html", "json", "progress" ],
         "since": { "target": "main" }
       }
     }
     ```
     (verify key names for your Stryker version; `break: 70` is the same threshold the Lab 5 PR gate enforces). Run a full baseline: record mutation score per component next to coverage.
  3. Feed the surviving mutants (JSON report) to a coding agent: "Add tests that kill these mutants. Do not change production code. For each mutant you believe is equivalent, explain why and do not add an ignore." Review its equivalence claims yourself.
  4. Compare with the human-written acceptance tests from Lab 1 on `DrivingTimeValidator` (coverage vs mutation score).
- **Break it:** Introduce a real bug in `CitationValidator` (accept quotes with similarity ≥ 0.5 instead of 0.9). Which test suite catches it — the 80%-coverage generated suite or the mutation-hardened one?
- **Acceptance criteria:** Report table (component · coverage before/after · mutation score before/after · equivalent mutants accepted with reasons); mutation score ≥ 80% on `SqlValidator` and `CitationValidator`; injected bug caught by the hardened suite.
- **Stretch:** Measure Stryker runtime full vs `since`-mode on a 3-file PR; set the PR gate accordingly.

### Lab 3 — Properties that find bugs examples miss (≈1.5h)

- **Goal:** Express domain and component invariants as properties.
- **Start state:** `c11/lab3-start` — FsCheck.Xunit and CsCheck both referenced; pick one.
- **Steps:**
  1. Driving-time properties:
     ```csharp
     // INV-1 in docs/specs/driving-time.md — daily-rule violations deliberately excluded (see Concepts)
     [Property(MaxTest = 500)]
     public Property Driving_to_rest_never_adds_weekly_or_continuous_violations(Shift shift, NonNegativeInt pick)
     {
         var drives = shift.DrivingSegments;                              // generator guarantees ≥ 1
         var after  = shift.ConvertToRest(drives[pick.Get % drives.Count]); // same start/end; nothing shifts in time
         var (b, a) = (Validator.Evaluate(shift), Validator.Evaluate(after));
         return (a.WeeklyLimitWeeks.IsSubsetOf(b.WeeklyLimitWeeks)
              && a.FortnightLimitWindows.IsSubsetOf(b.FortnightLimitWindows)
              && a.MaxContinuousDriving <= b.MaxContinuousDriving).ToProperty();
     }
     ```
     Add a round-trip property (`ActivityLog.Parse(log.ToCsv())` yields the same violations) and the time-zone invariance property. Every driving-time property cites the spec clause or invariant ID it encodes.
     Write custom generators for realistic shifts (activities of driving/rest/other, plausible durations, Europe/Sofia timestamps including DST transitions).
  2. RRF and `ResultSetComparer` properties (permutation, symmetry, reflexivity) with CsCheck:
     ```csharp
     Gen.String.List[0, 50].List[1, 4].Sample(lists =>
     {
         var fused = Rrf(lists);
         return fused.ToHashSet().SetEquals(lists.SelectMany(l => l));
     });
     ```
  3. `SqlValidator` fuzzing: generate compositions of allowed SELECT fragments with injected forbidden fragments (`; DROP`, `INTO`, `OPENROWSET`, `EXEC`, comments, nested CTEs); property: any input containing a forbidden construct is rejected.
- **Break it:** Let the property find a counterexample (the lab's planner has a seeded DST bug); read the shrunk input; add it as a named example test.
- **Acceptance criteria:** ≥ 6 properties across 4 components; at least one shrunk counterexample turned into a regression test; properties run in the fast lane (< 20 s total).
- **Stretch:** Ask an agent to propose properties from `docs/specs/driving-time.md`; accept only those you can justify from the spec.

### Lab 4 — Playwright planner, generator and healer on Fleet Ops (≈2.5h)

- **Goal:** Generate E2E coverage for the UI with agents and keep healing honest.
- **Start state:** `c11/lab4-start` — Fleet Ops UI (chat with citations, approval cards from C9, analyst results from C10) runnable with `FLEETOPS_LLM_MODE=Fake` (scripted `IChatClient` responses per scenario), and `e2e/` Node project with Playwright pinned.
- **Steps:**
  1. `npx playwright init-agents --loop=vscode` (or `claude`); commit the generated agent definitions.
  2. Write a seed test (login as dispatcher, open chat). Run the **planner** with `docs/specs/ui-prd.md`; review `specs/*.md` plans — delete any plan that asserts generated wording.
  3. Run the **generator**; review tests for selector quality (prefer role/label selectors) and assertions on structure (citation chip count ≥ 1, approval card shows slot ID, error banner on tool failure).
  4. Add the guard script `e2e/tools/healer-guard.mjs`: fails CI if a diff in `e2e/tests/**` changes `expect(` lines, adds `test.skip`/`test.fixme`, or deletes a test, unless the PR carries label `e2e-assertion-change` approved by CODEOWNERS.
  5. Live smoke: 3 tests against a real model deployment asserting structure only; run nightly.
- **Break it:** (a) Rename the "Одобри" (Approve) button to "Потвърди" — legitimate change; run the healer; accept its locator fix. (b) Introduce a real regression: the approval card no longer shows the slot ID. Run the healer and inspect what it proposes. The guard must block any assertion change or skip.
- **Acceptance criteria:** ≥ 12 generated E2E tests passing in Fake mode in < 4 min; guard script blocks case (b) in CI; `reports/c11-healer.md` documents both healer runs with your decision and reasoning.
- **Stretch:** Run the same UI flows under `bg-BG` and `en-US` browser locales and catch a formatting bug in analyst results (decimal comma).

### Lab 5 — Contracts, LLM lanes and the full CI gate (≈1.5h)

- **Goal:** Assemble the product's test system into one pipeline with explicit gates.
- **Start state:** `c11/lab5-start` — `.github/workflows/ci.yml` with build + unit only.
- **Steps:**
  1. OpenAPI contract tests for Ticketing/Scheduling/Parts mocks (schema-validate responses for every operation); MCP `tools.snapshot.json` test (C8); structured-output schema snapshots (C3).
  2. Orchestration tests with a fake `IChatClient` for the Fleet Assistant (C9): scripted tool calls → assert approval request emitted, budget middleware stops, repetition guard triggers — deterministic, fast lane.
  3. Synthetic data: generate 200 BG/EN incident reports from dimension tuples (seeded), human-review 20; store under `data/synthetic/` with generator version.
  4. Pipeline jobs: `build` → `unit-property` → `integration` (Testcontainers) → `contracts` → `mutation-changed` (break 70 on changed code) → `evals-cached` (C5/C7/C9/C10 gates) → `e2e-smoke-fake`; nightly: `mutation-full`, `evals-live`, `e2e-full`, `e2e-live-smoke`. Branch protection requires all PR jobs; CODEOWNERS on protected paths; dependency allow-list check.
     ```yaml
     mutation-changed:
       needs: unit-property
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
           with: { fetch-depth: 0 }
         - run: dotnet tool restore
         - run: dotnet stryker --config-file stryker-config.json   # since-mode vs main; break threshold enforced
         - uses: actions/upload-artifact@v4
           with: { name: mutation-report, path: "**/StrykerOutput/**/reports/*" }
     ```
- **Break it:** Open an agent PR that weakens a golden-set threshold in `evals/thresholds.json` "to fix flaky CI". The pipeline must require CODEOWNERS approval; record how it surfaced.
- **Acceptance criteria:** Full pipeline green on main; every PR job required; protected-path rule demonstrated; median PR pipeline ≤ 15 min; `docs/testing-strategy.md` (one page) describes lanes, gates, cadences and owners.
- **Stretch:** Equivalent Azure Pipelines YAML with `dotnet aieval` and Stryker reports published as pipeline artifacts.

## Kata

**Mutant hunt (25 min, repeat 4×).** Take one component and its current surviving-mutant list. Pick the three most dangerous survivors (business impact, not count), write the minimal tests that kill them — by hand — then compare with what an agent produces for the same three in a separate session. Score: mutants killed, test readability, assertions per test, time. Variations: a component where one survivor is genuinely equivalent; a property-based solution allowed; the agent works first and you review.

## Product increment — Fleet Ops Copilot

The product now has a **full test pyramid maintained with agents**: human-owned acceptance tests for domain rules (driving time, slot planning); agent-generated and mutation-hardened unit tests for validators and middleware; property-based tests for retrieval fusion, SQL validation and comparers; Testcontainers integration tests; OpenAPI and MCP contract tests; deterministic orchestration tests with a fake chat client; cached eval lanes for RAG, agent and SQL features; and **Playwright E2E tests generated by planner/generator agents** with governed healing. **Mutation score ≥ 70% on changed code** gates every PR.

## Factory increment — your agentic SDLC

This is the largest Factory increment of Level 2:

- **Test-first spec workflow**: skill `tdd-feature` — interview → SPEC.md (ceremony scaled to the change) → acceptance tests (human-approved) → fresh implementer session with protected paths → mutation run → mutant-killing session → PR with reports.
- **Subagents**: `test-writer` (may only write under `tests/**` except `tests/**/Acceptance/**`), `mutant-killer` (reads Stryker JSON, may only add tests), `implementer` (denied all test and golden paths).
- **Hooks**: post-edit `dotnet build` + fast lane; Stop hook that refuses "done" unless the fast lane and cached evals are green; pre-tool hook guarding protected paths.
- **`@Test` agent** policy documented: allowed for characterization and long-tail coverage; output must pass the mutation gate.
- **Playwright agents** initialized for your coding agent of choice, with the healer guard in CI.
- **Metrics** start being collected for C19: first-pass acceptance of agent PRs, mutation score trend, healer skip/assertion-change rate, flaky rate.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Test strategy | One undifferentiated test project | Unit vs integration split | Lanes for deterministic, contract, LLM evals, E2E with cadences and owners | Strategy justified by risk; inner-loop speed engineered for agents |
| AI-driven TDD | Agent writes code then tests | Tests first, same session | Separate sessions, protected oracle (permissions + hook + CODEOWNERS) | Ceremony scaled per change; agent attempts to bypass detected and logged |
| Test strength | Coverage reported | Mutation run once | Mutation gate on changed code; survivors analysed; equivalents justified | Uses mutation + properties to find a real bug; teaches agent to kill mutants efficiently |
| E2E with agents | Manual UI tests | Generated Playwright tests | Fake-LLM mode, structure assertions, healer guard enforced | Healer decisions documented; locale/regression cases caught; live smoke kept minimal |
| CI & governance | Tests run locally | CI runs tests | Full gated pipeline ≤ 15 min, protected paths, dependency allow-list | Quality metrics tracked and acted on; nightly drift lanes feed issues |

**Auto-checked:** acceptance suite unchanged by implementer commits; mutation score ≥ 70% on changed code and ≥ 80% on `SqlValidator`/`CitationValidator`; property tests present and fast; contract tests; healer guard blocks the seeded regression; pipeline required checks configured. **Human-reviewed:** `docs/testing-strategy.md`, healer report, equivalent-mutant justifications. This module's artefacts are inputs to **Gate G2**.

## Common pitfalls

- Gating on line coverage; celebrating 90% with a 40% mutation score.
- Letting the implementer session edit tests or golden sets "to fix the build".
- Bulk-ignoring surviving mutants as "equivalent" on an agent's word.
- Asserting LLM-generated wording in E2E tests; running E2E against a live model on every PR.
- Accepting healer changes to assertions or new skips without review.
- Culture-dependent tests (`bg-BG` decimal comma, date formats) that pass only on the build agent.
- Non-deterministic test data (no seeds, real clock) causing flaky lanes.
- Agents adding unvetted test packages (slopsquatting risk) — enforce the allow-list.
- Running full mutation testing on every PR and then disabling it because it's slow.


## References

- Claude Code best practices (failing test first, separate sessions, hooks, Stop gates): https://code.claude.com/docs/en/best-practices
- GitHub Copilot testing for .NET in Visual Studio (`@Test`, GA 11 Feb 2026): https://devblogs.microsoft.com/dotnet/github-copilot-testing-for-dotnet-available-in-visual-studio/
- Playwright test agents (planner, generator, healer; `init-agents`): https://playwright.dev/docs/test-agents
- Thoughtworks Technology Radar Vol. 34 digest (mutation testing Trial, feedback sensors Trial, cognitive debt Caution): https://agentic-ai.readthedocs.io/en/latest/AgenticTechStack/thoughtworks-radar-vol34/
- Böckeler — Exploring spec-driven development tools: https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- Kiro research note (property-based testing in GA): https://rywalker.com/research/kiro
- MEAI Evaluation libraries (response caching, `dotnet aieval`): https://learn.microsoft.com/en-us/dotnet/ai/evaluation/libraries
- Hamel Husain — Evals FAQ (synthetic data via dimension tuples): https://hamel.dev/blog/posts/evals-faq/
- CSA research note on slopsquatting: https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419/
- Stryker.NET documentation: https://stryker-mutator.io/docs/stryker-net/introduction/ (general knowledge; verify current config reference)
- FsCheck: https://fscheck.github.io/FsCheck/ · CsCheck: https://github.com/AnthonyLloyd/CsCheck (general knowledge; verify versions)
- DORA 2025 report (AI as amplifier): https://blog.google/technology/developers/dora-report-2025/
