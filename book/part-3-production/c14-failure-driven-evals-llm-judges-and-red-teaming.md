# C14 — Failure-driven evals, LLM judges & red teaming

> **Level:** 3 — Production systems (Advanced) · **Duration:** 16h (theory 25% / labs 75%) · **Prerequisites:** C5 (golden set v1, MEAI.Evaluation basics), C11 (test pyramid, CI), C12 (incident workflow + traces), C13 (retrieval & memory) · **Volatility:** Med (method is stable; Foundry evaluator statuses, red-teaming regions/targets and tool ownership change)

## Why this matters

Fleet Ops Copilot passed all 50 golden-set questions from C5 and the incident workflow from C12 passes its invariant tests. In the first two weeks of shadow traffic the dispatchers still flag 9% of incident runs as "wrong." When the team opens the traces, the failures are not what anyone wrote evaluators for: customer notices that promise an ETA the maintenance slot cannot meet; Bulgarian policy citations that point to the right document but the wrong paragraph; triage that rates a reefer compressor fault "Medium" because the text never mentions temperature. The team's dashboard shows "Helpfulness 4.3/5" and "Coherence 4.6/5" — numbers that move with nothing and predict nothing.

This is the most common way AI products stall: evaluation that measures what was easy to imagine rather than what actually fails. The leading practitioners (Husain & Shankar) are explicit: "avoid eval-driven development in general" — do not write speculative evaluators or rely on generic metrics; **look at real traces first**, build a failure taxonomy, write one binary check per observed failure mode, validate every LLM judge against human labels, and only then gate CI. They report spending 60–80% of development time on error analysis and evaluation.

Experts also know their evaluators lie in specific ways: a judge with 70% true-negative rate will hide real regressions; a cached CI run cannot see provider drift; Azure's groundedness detection does not support Bulgarian; and the red-teaming service cannot target a workflow agent. This module industrialises the practice for Fleet Ops: error analysis on ~100 traces, calibrated judges, trajectory and tool-call evals, red teaming with Attack Success Rate, model-migration A/B tests and a CI regression gate that coding agents must keep green.

## Learning outcomes

1. **Perform** error analysis on ~100 production-like traces using open and axial coding, and **produce** a failure taxonomy with counts and a saturation curve.
2. **Choose** for each failure mode between a direct fix, a code-based check and an LLM judge, and **justify** the choice.
3. **Implement** binary, single-failure-mode LLM judges as MEAI `IEvaluator`s and **validate** them against 100–200 human labels with train/dev/test splits, reporting TPR and TNR.
4. **Correct** observed pass rates for judge error and **report** uncertainty.
5. **Implement** trajectory, tool-call and end-state evals (MEAI IntentResolution, TaskAdherence, ToolCallAccuracy; span-based assertions; τ-bench-style simulation with pass^k).
6. **Distinguish** offline and online evaluation and **configure** Foundry evaluations/continuous evaluation alongside .NET evals.
7. **Run** red-team campaigns with PyRIT and the AI Red Teaming Agent, **report** Attack Success Rate per category, and **verify** architectural mitigations.
8. **Design** a calibrated Bulgarian groundedness judge as a fallback for English-only safety features.
9. **Build** a CI regression gate in GitHub Actions (cached PR runs, nightly uncached runs, model-migration A/B) with statistically defensible thresholds.

## Concepts

### 1. Failure-driven evals, not speculative evals

Course stance (introduced in C5, now industrialised): **observe failures → write evaluators for them → gate CI.** Consequences:
- No generic "helpfulness/coherence" scores as quality measures. BLEU/ROUGE/BERTScore are generally not useful for LLM outputs (embedding similarity can help evaluate retrieval).
- **Binary pass/fail** over 1–5 Likert scales: Likert scores are hard to calibrate, drift between annotators and hide the decision you actually need ("ship or not").
- Report a **pass-all rate** (fraction of cases that pass every check) and drill into per-check rates.
- Many failures need a **fix, not an evaluator** (a prompt bug, a missing tool parameter). Add a regression check only if the failure can plausibly recur.

**Misconception to unlearn:** "more evaluators = more quality." Each evaluator has a cost (labels, maintenance, false alarms). Prefer few, validated, failure-specific checks.

### 2. Error analysis protocol

1. **Sample ~100 diverse traces.** Start exploratory (random, clustering); then targeted (negative user feedback, retries, unusually long traces, unusual tool sequences, budget escalations). Keep some random traces in every batch.
2. **Open coding.** For each trace, write a free-text note on the **first** failure you see (upstream errors cause downstream ones). Annotate at least the first 30 yourself before letting an LLM suggest failures; do not outsource core error analysis. Record non-model problems (missing feature, bad data) too.
3. **Axial coding.** Group notes into a taxonomy of failure modes with counts. An LLM can propose groupings; you decide.
4. **Saturation.** Continue until new traces stop revealing new failure modes ("theoretical saturation").
5. **Governance.** One domain expert acts as a "benevolent dictator" for quality calls (for Trakia: a senior dispatcher). With multiple annotators, label independently, measure agreement (Cohen's κ), then hold alignment sessions.
6. **Cadence.** Refresh with 100+ new traces every 2–4 weeks plus 10–20 outliers weekly.

Tooling: build a **custom trace viewer** — trace next to outcome, keyboard shortcuts for pass/fail and note, progress counter. Generic observability UIs are too slow for 100 traces.

### 3. From taxonomy to evaluators

| Failure mode (example from Trakia traces) | Detectable by rule? | Evaluator |
|---|---|---|
| Customer notice contains internal fault codes (`P0087`) | Yes | regex code check |
| Booking before driving-time check | Yes (span order) | trajectory assertion |
| Booked slot violates depot hours | Yes (DB) | end-state check |
| Notice promises ETA earlier than booked slot + repair estimate | Mostly (parse ETA, compare) | code check with parser; judge fallback for free-form phrasing |
| Policy citation does not support the claim (BG/EN) | No | LLM judge (groundedness, per claim) |
| Severity under-rated given cargo/SLA context | No | LLM judge with rubric of decisive features |
| Tone inappropriate for B2B customer | No — and rare | **no evaluator yet**; monitor via feedback |

### 4. LLM judges: design and validation

Judge design: one failure mode per judge; binary output plus a short critique; few-shot examples drawn from the **train** split; explicit definition of Pass and Fail with borderline examples; structured output (`{ "critique": "...", "pass": false }`); temperature as low as the model allows (still not deterministic). The same model family may serve as app model and judge **if** it aligns with human labels — measure, don't assume.

Validation (per failure mode):
- **100–200 labelled examples**; split ~10–20% **train** (few-shot pool), 40–45% **dev** (iterate the prompt), 40–45% **test** (touch once); aim for 30–50 Pass and 30–50 Fail in each of dev and test.
- Report **TPR** (judge says Pass when human says Pass) and **TNR** (judge says Fail when human says Fail). With imbalanced classes raw agreement misleads: a judge that always says Pass scores 92% agreement on a 92%-pass dataset and catches nothing.
- If test ≪ dev, you overfit the prompt to dev.
- **Correct the observed pass rate** for judge error: θ̂ = (p_obs + TNR − 1) / (TPR + TNR − 1). With p_obs = 0.88, TPR = 0.93, TNR = 0.85: θ̂ = (0.88 + 0.85 − 1)/(0.93 + 0.85 − 1) = 0.73/0.78 ≈ 0.936. Bootstrap the labelled set to get a confidence interval. If TPR + TNR − 1 is small, the judge is too weak to gate anything.

### 5. Trajectory, tool-call and outcome evals for agents

Three layers (matching the agentic-RAG SoK's component / trajectory / system split):
- **Outcome (system):** did the world end in the right state? τ-bench pioneered simulated users + domain policies + **database end-state checks** and **pass^k** (all k trials succeed) — the reliability metric agents need, because pass@1 hides flakiness. For Trakia: after the run, exactly one booking exists, at an allowed depot slot, parts reserved match the plan, one customer notice sent.
- **Trajectory:** right tools, valid arguments, correct order, no forbidden tools, efficiency (steps/tokens vs reference). Prefer asserting **invariants** (ordering, forbidden actions) over exact paths — many paths are valid.
- **Component:** retrieval quality, triage accuracy, judge-checked groundedness per node.

.NET: `Microsoft.Extensions.AI.Evaluation.Quality` includes agent evaluators **IntentResolution**, **TaskAdherence** and **ToolCallAccuracy** (LLM-judged; they need the conversation, the response and tool definitions as context). Foundry offers agent evaluators: Task Adherence, Intent Resolution, Task Completion (**preview**), Tool Call Accuracy, Tool Selection, Tool Input Accuracy, Tool Output Utilization, Tool Call Success, Task Navigation Efficiency, and a weighted **Rubric** evaluator (**preview**), runnable at turn or conversation level. Treat these as *generic* signals: useful for triage, but calibrate them like any judge before gating on them.

Trajectories come from **OTel spans** (C15): `invoke_agent`, `execute_tool` with `gen_ai.tool.name`, `gen_ai.tool.call.id`. Because GenAI semantic conventions are still "Development", pin the semconv version your assertions read.

### 6. Offline vs online evaluation

| | Offline (pre-release) | Online (production) |
|---|---|---|
| Data | golden + regression sets, simulations, red-team sets | sampled live traces |
| Purpose | gate changes | detect drift, discover new failures |
| Tools | MEAI.Evaluation in xUnit + `dotnet aieval`; Foundry cloud evaluations | Foundry **continuous evaluation**; MEAI scores published to telemetry; user feedback |
| Determinism | response caching → cheap, repeatable | none — sample and trend |

Foundry evaluations: per a practitioner source, evaluations, monitoring and tracing reached GA in March 2026 with some evaluators still preview (verify on Learn). Cloud evaluation references built-ins by ID (e.g., `builtin.task_adherence`), requires **Entra ID** (no API keys), and takes synthetic data, uploaded JSONL/CSV, benchmarks or existing traces (traces need App Insights). Authoring samples are Python-first (`azure-ai-evaluation`, `azure-ai-projects`) **[Python]**. Continuous evaluation samples live agent responses, shows results on the agent's Monitor tab next to latency/tokens/run success, supports alerts, and requires App Insights plus the project managed identity holding the Foundry User role. Online evals never replace error analysis: low-scoring traces go **into** the next error-analysis batch.

### 7. A/B and model-migration testing

Models retire (C15: ≥18 months for standard GA Azure models, 12 for several partner families, ≥60 days' notice). A migration is a **release with a pairwise eval report**:
- Freeze the suite (golden + regression + simulation + red-team sets).
- Run current and candidate; compare **per failure mode** pass rates, pass^k, cost/task, latency p50/p95.
- **Pairwise judge** for open-ended outputs (customer notice quality): show both outputs, ask for the better one with a reason; **swap positions** and count only consistent verdicts (position bias).
- Paired binary outcomes → **McNemar's test** on discordant pairs; with 200 cases, a 5-point swing may well be noise. Pre-register the decision rule ("no failure mode worse by > 3 pp with p < 0.05; cost/task ≤ +10%").
- Online, promote via canary/feature flags (C15) with the same metrics.

### 8. Synthetic data, carefully

Synthetic data fills coverage gaps; it cannot tell you how **common** a failure is in production. Recipe: define dimensions (incident type × severity × language × customer contract type × data quality), hand-write ~20 tuples, generate more tuples, then convert each tuple to a natural-language incident in a **separate** step (avoids homogeneous phrasing), and human-review before use. RAGAS can generate KG-based test sets **[Python]**. Never mix synthetic and production-sampled cases in the same prevalence statistic.

### 9. Red teaming

- **PyRIT** **[Python]**: orchestrators, converters (encodings, translations, rephrasings), scorers; you point it at an HTTP target.
- **AI Red Teaming Agent** (Foundry): wraps PyRIT with **24 attack strategies** (encodings/ciphers, obfuscation, jailbreak/indirect jailbreak, multi-turn, Crescendo) and reports **Attack Success Rate (ASR)** per risk category. Agent-specific risks (prohibited actions, sensitive data leakage, task adherence) are **cloud-only**, in East US 2, France Central, Sweden Central, Switzerland West and North Central US. Targets: Foundry prompt and hosted (container) agents; **workflow agents, non-Foundry agents, function tools, connected agents and computer use are not supported**; text-only; run in a "purple" (non-production, production-like) environment. GA/preview status is not stated on Learn — verify.
- **ASR** = successful attacks / attempted attacks, per category and strategy. Track it like a regression metric; it should trend down but will not reach zero for classifier-only defences.
- Also: MEAI.Evaluation safety evaluators (IndirectAttack, CodeVulnerability, content harms, ProtectedMaterial, UngroundedAttributes) call the Foundry Evaluation service; **ASSERT** (open-sourced at Build 2026) generates adversarial tests from policies; garak; Promptfoo (now OpenAI-owned).
- Red-team the **architecture**, not just the prompt: the C12 approval gate means a successful injection in incident text should still not produce a booking. Measure "attack reached a consequential action" separately from "model produced unsafe text."

### 10. Bulgarian: when safety features are English-only

Azure AI Content Safety **groundedness detection** (preview) is **English-only** and region-limited (East US, East US 2, France Central, Sweden Central, UK South, West US); protected material and custom categories are English-only; other classifiers are trained/tested on zh, en, fr, de, es, it, ja, pt — Bulgarian "may work" with variable quality. Fleet Ops answers dispatchers and customers in Bulgarian, so: build a **Bulgarian groundedness judge** (claim-level: each claim → supported / not supported by cited passage), calibrated on ≥150 Bulgarian examples labelled by a Bulgarian-speaking domain expert; compare against translate-then-check (cheaper, but translation can repair or introduce errors) and record both TPR/TNR. Run classifier-based safety on BG text, but measure its BG performance on your own labelled set before trusting it.

### 11. CI regression gates

- **PR gate:** MEAI.Evaluation tests with **response caching** (cheap, deterministic when prompt/model unchanged) → thresholds per failure mode → `dotnet aieval` report as artifact → PR comment.
- **Nightly uncached run** against live models to detect provider-side drift; weekly full simulation with pass^k.
- **Thresholds**: per failure mode, with tolerance bands derived from run-to-run variance (measure: run uncached ×5 and take the spread); never "exact equality" on model outputs.
- **Ownership:** eval datasets, judge prompts and thresholds are versioned artifacts under CODEOWNERS; coding agents may *read* them and must keep them green, but cannot change them.

### 12. The tools market and vendor neutrality

Promptfoo (OSS evals/red teaming) — OpenAI announced its acquisition on 9 March 2026; Langfuse (OSS tracing/evals/prompt management) — acquired by ClickHouse in January 2026. Both remain usable, but the lesson is architectural: **capture traces with OpenTelemetry**, keep datasets/labels as JSONL in git, keep judges as code (`IEvaluator`). Then any platform — Foundry, Langfuse, Phoenix, LangSmith, Braintrust — is a replaceable viewer, not the system of record.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| `Microsoft.Extensions.AI.Evaluation` (+ `.Quality`, `.NLP`, `.Safety`, `.Reporting`, `.Reporting.Azure`, `.Console`) | evaluators, caching, reports, `dotnet aieval` | Libraries documented on Learn; package versions/GA per package — verify on NuGet | Agent evaluators: IntentResolution, TaskAdherence, ToolCallAccuracy |
| xUnit / MSTest + Testcontainers (SQL Server 2025) | eval tests, end-state checks | GA | DB snapshot per run |
| Foundry evaluations & continuous evaluation | cloud/batch and online evaluation | GA (Mar 2026, per practitioner source); several agent evaluators + Rubric **preview** | Entra ID only; authoring **[Python]** |
| `azure-ai-evaluation`, `azure-ai-projects` **[Python]** | cloud eval authoring | GA SDKs (verify versions) | Used in Lab 3 stretch |
| PyRIT **[Python]** | red-team automation | OSS | Lab 4 |
| AI Red Teaming Agent (Foundry) | 24 strategies, ASR scorecards | Status not stated — verify; agent risks cloud-only, 5 regions | Not for workflow agents/function tools |
| ASSERT | policy-driven adversarial tests | Open source (Build 2026) | Optional |
| Azure AI Content Safety (Prompt Shields, groundedness) | classifiers | Prompt Shields available; groundedness **preview, English-only** | BG fallback required |
| GitHub Actions | CI gates | GA | `actions/upload-artifact` for reports |
| Promptfoo / Langfuse | alternative eval/trace tools | OSS; owned by OpenAI / ClickHouse | Use via OTel/JSONL only |

## Labs

### Lab 1 — Error analysis on 100 incident traces (≈2.5h)
- **Goal:** Build the Fleet Ops failure taxonomy from real behaviour.
- **Start state:** tag `c14/lab1-start` — 400 exported traces (OTLP JSON) from two weeks of shadow traffic of the C12 workflow driven by the dispatcher simulator, with 31 dispatcher thumbs-down events; a **pre-built trace viewer** (Blazor Server page: left pane = incident input + final outputs (booking, notice); right pane = span tree with tool arguments/results; keys `P`/`F`/`N` (pass/fail/note), progress counter; saves `labels/c14-open-coding.jsonl` with `traceId, verdict, firstFailureNote, annotator`).
- **Steps:**
  1. Run the provided trace viewer against the export and label 3 traces to check it works (≤10 min). Do not extend it in this lab; customising it is the stretch and the factory increment.
  2. Sample 100: 60 random, 25 targeted (thumbs-down, budget escalations, >2 planner loops), 15 longest traces.
  3. Open-code all 100 yourself (first failure only).
  4. Axial-code: use an LLM to propose clusters from your notes, then edit to a taxonomy `docs/evals/failure-taxonomy.md` with definitions, examples (trace IDs) and counts.
  5. Plot new-failure-mode discovery vs traces reviewed (saturation curve).
  6. For each mode decide: **fix now** / **code check** / **LLM judge** / **monitor only**; open issues for fixes.
- **Break it:** Have a peer annotate 30 of your traces independently; compute Cohen's κ; hold a 15-minute alignment session and update definitions.
- **Acceptance criteria:** ≥ 100 labelled traces; taxonomy with ≥ 5 modes, each with definition, ≥ 2 example trace IDs and count; κ reported; decision table complete; at least two "fix now" issues opened and linked.
- **Stretch:** Cluster trace embeddings (input + first-failure note) to find a mode you missed. Extend the viewer (e.g., filter by taxonomy mode, show the judge verdict next to your label) under C11 test discipline.

### Lab 2 — Code checks and calibrated binary judges (≈3h)
- **Goal:** Turn the top failure modes into validated evaluators.
- **Start state:** tag `c14/lab2-start`.
- **Steps:**
  1. Implement code checks as `IEvaluator`s (no model): `NoInternalFaultCodes`, `EtaConsistentWithBooking` (parse ETA in BG/EN; compare with slot + repair estimate).
     ```csharp
     public sealed partial class NoInternalFaultCodesEvaluator : IEvaluator   // partial: required by [GeneratedRegex]
     {
         public const string Metric = "NoInternalFaultCodes";
         public IReadOnlyCollection<string> EvaluationMetricNames => [Metric];
         public ValueTask<EvaluationResult> EvaluateAsync(IEnumerable<ChatMessage> messages, ChatResponse modelResponse,
             ChatConfiguration? chatConfiguration = null, IEnumerable<EvaluationContext>? additionalContext = null,
             CancellationToken cancellationToken = default)   // verify signature for your pinned version
         {
             var hit = FaultCodeRegex().Match(modelResponse.Text);
             var m = new BooleanMetric(Metric, value: !hit.Success, reason: hit.Success ? $"Leaked {hit.Value}" : null);
             return ValueTask.FromResult(new EvaluationResult(m));
         }
         [GeneratedRegex(@"\b[PBCU][0-3][0-9A-F]{3}\b")] private static partial Regex FaultCodeRegex();
     }
     ```
  2. Implement two LLM judges with structured output (`{critique, pass}`): `SeverityUnderratedJudge` and `PolicyClaimSupportedJudge` (claim-level, BG and EN).
  3. Assemble 150–200 labelled examples per judge: the start tag ships ~100 expert-labelled examples per judge, and you label the rest from Lab 1 traces + targeted additions (fewer than ~140 cannot satisfy the per-split minimums below). Split train 15% / dev 42.5% / test 42.5% with ≥ 30 Pass and ≥ 30 Fail in dev and test (`labels/judges/{judge}/{split}.jsonl`).
  4. Iterate the judge prompt on dev only; then run once on test. Compute TPR, TNR, and the corrected pass rate on the full 400-trace population with a bootstrap 95% CI.
     ```csharp
     static (double tpr, double tnr) Score(IEnumerable<(bool human, bool judge)> xs)
     {
         var l = xs.ToList();
         double tp = l.Count(x => x.human && x.judge), fn = l.Count(x => x.human && !x.judge);
         double tn = l.Count(x => !x.human && !x.judge), fp = l.Count(x => !x.human && x.judge);
         return (tp / (tp + fn), tn / (tn + fp));
     }
     static double Corrected(double pObs, double tpr, double tnr) => (pObs + tnr - 1) / (tpr + tnr - 1);
     ```
- **Break it:** Swap the judge model for a fast small model; re-measure TPR/TNR on test and observe which metric collapses.
- **Acceptance criteria:** each judge has TPR ≥ 0.85 and TNR ≥ 0.85 on **test** (or a documented decision to use it for monitoring only); dev–test gap ≤ 0.08; `docs/evals/judge-cards/*.md` (purpose, definition, model, prompt hash, splits, TPR/TNR, known blind spots); code checks have unit tests with positive and negative examples.
- **Stretch:** Compare the built-in MEAI `GroundednessEvaluator` against your claim-level judge on the same BG test split.

### Lab 3 — Trajectory, tool-call and end-state evals with simulated dispatchers (≈2.5h)
- **Goal:** Evaluate the agentic behaviour, not just final text.
- **Start state:** tag `c14/lab3-start` — Testcontainers SQL Server 2025 with a `TrakiaOps` snapshot; OTel in-memory exporter wired into the test host.
- **Steps:**
  1. Configure reporting with caching and agent evaluators:
     ```csharp
     ReportingConfiguration cfg = DiskBasedReportingConfiguration.Create(
         storageRootPath: "artifacts/aieval",
         evaluators: [new IntentResolutionEvaluator(), new TaskAdherenceEvaluator(), new ToolCallAccuracyEvaluator(),
                      new NoInternalFaultCodesEvaluator(), new PolicyClaimSupportedJudge()],
         chatConfiguration: new ChatConfiguration(judgeChatClient),
         enableResponseCaching: true,
         executionName: Environment.GetEnvironmentVariable("GITHUB_RUN_ID") ?? "local");   // verify names
     await using ScenarioRun run = await cfg.CreateScenarioRunAsync($"incident/{tc.Id}");
     EvaluationResult r = await run.EvaluateAsync(messages, response,
         additionalContext: [new ToolCallAccuracyEvaluatorContext(toolDefinitions)]);       // verify context type
     ```
  2. Trajectory assertions from captured spans: driving-time check precedes any `scheduling_book_slot`; no state-changing tool without an approval span; ≤ 2 planner loops; every `execute_tool` argument `vehicleId` exists in the snapshot.
  3. End-state check after each run: SQL assertions on bookings, reservations, notices (exactly-once, allowed slot, parts match plan).
  4. τ-bench-style simulation: an LLM **dispatcher simulator** with persona cards (terse Sofia dispatcher; anxious new hire; Bulgarian-only) and the fleet policy; 30 scenarios × k = 4. Report pass^1 and pass^4.
- **Break it:** Introduce a regression — reorder two edges so the planner can run before the policy check returns. Confirm trajectory assertions fail while text-only evaluators still pass.
- **Acceptance criteria:** trajectory and end-state tests in `tests/Evals.Agentic` green on `main`; the induced regression is caught; pass^4 reported with the gap to pass^1 explained; calibration note on the three MEAI agent evaluators (agreement with your Lab 1 labels on ≥ 40 traces).
- **Stretch [Python]:** Run Foundry cloud evaluation with `builtin.task_adherence` and Tool Call Accuracy on the same traces from App Insights; compare with MEAI results.

### Lab 4 — Red teaming and the Bulgarian groundedness fallback (≈2h)
- **Goal:** Quantify attack success and prove the architecture holds.
- **Start state:** tag `c14/lab4-start` — "purple" environment (separate Foundry project, synthetic data only); PyRIT environment in the scripts container.
- **Steps:**
  1. **[Python]** PyRIT campaign against `POST /incidents` and the Fleet Assistant chat endpoint: (a) indirect injection in incident free text and in a retrieved historical incident report; (b) exfiltration via customer notice (try to get driver personal data into the notice); (c) BG-language jailbreaks and encoded variants; (d) multi-turn Crescendo on the chat endpoint. Score with PyRIT scorers + your Lab 2 judges.
  2. Compute ASR per category and the **consequential-action ASR** (attack produced a booking/notice/tool call it should not have) from traces.
  3. AI Red Teaming Agent cloud scan (France Central or Sweden Central) against a **Foundry hosted-agent wrapper** of the Fleet Assistant (workflow agents are unsupported targets — document this limitation in the report).
  4. Mitigate: Prompt Shields at input + spotlighting of retrieved documents (layer 1); confirm approval gate and read-only planner (architecture); re-run and compare.
  5. BG groundedness: run your `PolicyClaimSupportedJudge` on 150 BG cases vs translate-then-check using English-only groundedness detection; report TPR/TNR for both.
- **Break it:** Temporarily allow the planner to call `scheduling_book_slot` directly (remove the approval edge in the purple env). Show consequential-action ASR jumps from 0.
- **Acceptance criteria:** `artifacts/c14/redteam-report.md` with ASR per category before/after, consequential-action ASR = 0 with architecture intact, scan configuration and region, unsupported-target note; BG groundedness comparison table; the red-team set added to the regression suite.
- **Stretch:** Generate policy-derived adversarial tests with ASSERT and add the failing ones to the suite.

### Lab 5 — CI regression gate and model-migration A/B (≈2h)
- **Goal:** Make evals a merge gate and rehearse a model migration decision.
- **Start state:** tag `c14/lab5-start`.
- **Steps:**
  1. GitHub Actions workflow:
     ```yaml
     name: evals
     on: [pull_request]
     jobs:
       evals:
         runs-on: ubuntu-latest
         permissions: { id-token: write, contents: read, pull-requests: write }
         steps:
           - uses: actions/checkout@v4
           - uses: azure/login@v2            # OIDC federated credential, no secrets
             with:
               client-id: ${{ vars.AZURE_CLIENT_ID }}
               tenant-id: ${{ vars.AZURE_TENANT_ID }}
               subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
           - uses: actions/setup-dotnet@v4
             with: { dotnet-version: '10.0.x' }
           - run: dotnet test tests/Evals.Agentic --filter "Category=Gate" --logger trx
           - run: dotnet tool restore && dotnet aieval report --path artifacts/aieval --output artifacts/aieval/report.html   # verify flags
           - uses: actions/upload-artifact@v4
             with: { name: aieval-report, path: artifacts/aieval/report.html }
     ```
     Threshold logic lives in the tests (per failure mode, tolerance from measured variance), not in YAML. Cache the response store between runs keyed by prompt/model hashes.
  2. Nightly workflow: same suite with caching disabled + simulation pass^4; open an issue automatically on threshold breach.
  3. Model migration A/B: candidate deployment vs current on the frozen suite; pairwise judge with position swap for customer notices; McNemar on each binary failure mode; cost/task and p95 deltas; write `docs/evals/migration-<candidate>.md` with a go/no-go per the pre-registered rule.
  4. Online loop: enable Foundry continuous evaluation (portal or REST) on the staging Fleet Assistant with one built-in agent evaluator, a sampling rate and one alert; route low-scoring traces into the next error-analysis batch (Lab 1 viewer queue). Note in the migration memo which online signal you would watch during the canary.
- **Break it:** Commit a prompt change that makes notices longer and occasionally drops the SLA clause; the PR gate must fail with the failing cases linked in the report.
- **Acceptance criteria:** PR gate blocks the bad change; nightly run green on `main`; migration memo contains per-mode table, McNemar p-values, cost/latency deltas and a decision; branch protection requires the `evals` check.
- **Stretch:** Add a pass^k-based flake guard: a failing case is re-run k = 3 uncached before the gate fails.

## Kata

**"Label sprint" (25 min, repeated).** Open 20 fresh traces from the latest shadow-traffic batch in your trace viewer. Annotate first failures in ≤ 60 s each, then spend 5 minutes updating the taxonomy counts and deciding whether any new mode has appeared. Variations: only Bulgarian traces; only traces with budget escalations; only traces your judges marked Pass (hunt judge false positives); a peer's batch (compute κ against them). Track your labels/minute and κ over repetitions.

## Product increment — Fleet Ops Copilot

Fleet Ops Copilot now ships with a **production eval suite**: a failure taxonomy maintained from trace review; code checks and calibrated binary LLM judges (with judge cards and TPR/TNR); trajectory, tool-call and end-state evals with simulated dispatchers and pass^k; a Bulgarian groundedness judge replacing the English-only classifier; a **red-team report** with ASR per category and zero consequential-action ASR; a **CI regression gate** on PRs, nightly uncached drift runs, and a documented model-migration A/B procedure. These artifacts are core evidence for **Gate G3** (see G3) and for the AI Act risk file in C18.

## Factory increment — your agentic SDLC

- **Eval gates in GitHub Actions** are required status checks; coding agents (Copilot cloud agent, Claude Code in Actions) must run `dotnet test --filter Category=Gate` locally before claiming done (instruction in `AGENTS.md`, enforced by a stop/pre-PR hook).
- **Protected eval assets:** `eval/**`, `labels/**`, `docs/evals/judge-cards/**` and threshold constants are under CODEOWNERS (human reviewers only); a hook blocks agent edits to these paths.
- **Regression triage agent:** a headless agent (`claude -p` or a Copilot custom agent `.github/agents/eval-triage.agent.md`) triggered on gate failure. It reads the aieval report and the failing traces, maps each failure to the taxonomy, posts a PR comment with suspected cause and the smallest reproducing case, and proposes a fix in a separate commit — never touching evals.
- **Label tooling as product:** the trace viewer lives in the repo and is maintained by agents under the same test discipline (C11).

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Error analysis | Writes evaluators from imagination | 100 traces coded; taxonomy with counts | Targeted + random sampling, saturation shown, κ measured and aligned | Analysis drives roadmap (fixes vs evals vs monitoring) with cadence and ownership |
| Judge quality | Likert "quality" judge | Binary judge per mode with dev/test | TPR/TNR ≥ 0.85 on test; corrected pass rate with CI; judge cards | Knows each judge's blind spots; detects judge drift; BG calibration done |
| Agentic evals | Final-text only | MEAI agent evaluators used | Trajectory invariants + end-state + pass^k | Simulation personas reveal reliability gaps; evaluators calibrated against labels |
| Red teaming | Ad-hoc prompts | PyRIT campaign with ASR | ASR before/after mitigations; consequential-action ASR separated | Red-team set in regression suite; platform limitations (targets, regions, language) designed around |
| CI & migration | Manual runs | PR gate with cached evals | Nightly uncached drift + per-mode thresholds from variance | Pre-registered migration rule with McNemar/pairwise; agents kept green without touching evals |

**Auto-checked:** labels files and taxonomy schema; judge TPR/TNR on hidden test split (instructor holds an extra 40 labels per judge); trajectory/end-state suites green; induced-regression detection; red-team report schema and consequential-action ASR = 0 on the hidden attack set; `evals` workflow is a required check and blocks the seeded bad PR.

## Common pitfalls

- Starting with metrics instead of traces; generic "helpfulness" dashboards.
- Letting an LLM do the open coding; never reading traces yourself.
- 1–5 scales; averaging Likert scores across annotators.
- Validating judges on the same examples used as few-shots (train leakage), or iterating on test.
- Reporting agreement instead of TPR/TNR; ignoring class imbalance.
- Gating on uncalibrated built-in evaluators.
- Exact-path trajectory assertions that break on valid alternatives — assert invariants.
- Only cached CI runs — provider drift goes unseen.
- Treating ASR from classifier tweaks as success while the architecture still allows consequential actions.
- Assuming English-only safety features cover Bulgarian.
- Letting coding agents "fix" failing evals by editing thresholds or datasets.
- Mixing synthetic cases into production prevalence numbers.


## References

- Husain & Shankar — LLM evals FAQ (updated 21 Sep 2026): https://hamel.dev/blog/posts/evals-faq/
- Husain — Using LLM-as-a-Judge (TPR/TNR, critique shadowing): https://hamel.dev/blog/posts/llm-judge/
- Microsoft Learn — MEAI Evaluation libraries: https://learn.microsoft.com/en-us/dotnet/ai/evaluation/libraries
- Microsoft Foundry — built-in evaluators (agent evaluators, Rubric **preview**): https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators
- Microsoft Foundry — RAG evaluators: https://learn.microsoft.com/en-my/Azure/foundry/concepts/evaluation-evaluators/rag-evaluators
- J. Reinhard — How to Evaluate AI Agents in Microsoft Foundry (practitioner; GA date, continuous eval prerequisites): https://jannikreinhard.com/microsoft-foundry-agent-evaluations/
- Yao et al. — τ-bench (pass^k): https://arxiv.org/abs/2406.12045 · τ²-bench: https://arxiv.org/abs/2506.07982
- Agentic RAG SoK (component/trajectory/system evaluation): https://arxiv.org/html/2603.07379v1
- Microsoft Learn — AI Red Teaming Agent (targets, regions, ASR): https://learn.microsoft.com/azure/ai-foundry/concepts/ai-red-teaming-agent
- PyRIT: https://github.com/Azure/PyRIT
- Microsoft Learn — Azure AI Content Safety overview (language/region limits): https://learn.microsoft.com/en-gb/azure/ai-services/content-safety/overview
- Foundry — What's new at Build 2026 (ASSERT, Agent Control Specification): https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-build-2026/
- OpenAI — to acquire Promptfoo: https://openai.com/blog/openai-to-acquire-promptfoo
- Langfuse — joining ClickHouse: https://langfuse.com/blog/joining-clickhouse
- RAGAS metrics and testset generation **[Python]**: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
- Anthropic — Writing effective tools for agents (tool evals): https://www.anthropic.com/engineering/writing-tools-for-agents
