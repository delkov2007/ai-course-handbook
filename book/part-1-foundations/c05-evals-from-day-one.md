# C5 — Evals from day one

> **Level:** 1 — Foundations (Beginner) · **Duration:** 10h (theory 20% / labs 80%) · **Prerequisites:** C1 (nondeterminism, sampling harness), C2 (pipeline, traces in Aspire), C3 (extraction, tool), C4 (factory, hooks, protected paths) · **Volatility:** Low for method; Med for `Microsoft.Extensions.AI.Evaluation` APIs and CI tooling

## Why this matters

Trakia's dispatch lead tried Fleet Ops Copilot for a week and reported "it's mostly fine, but sometimes it makes up policies." The team responded the way most teams do: they tweaked the system prompt, eyeballed three answers, and shipped. The next week a model-version upgrade silently increased Bulgarian extraction errors, and a prompt change that fixed policy fabrication broke vehicle-status tool routing. Nobody noticed for nine days, because nothing measured it.

The opposite failure is just as common: a team installs an eval framework, wires up twelve generic metrics ("helpfulness 4.1/5, coherence 4.3/5"), builds dashboards, and still can't say whether the product got better — because none of those numbers correspond to a failure a user actually experienced. Hamel Husain and Shreya Shankar, whose evals method is the most influential practitioner guidance in 2026, put it bluntly: "avoid eval-driven development in general" — don't write speculative evaluators, and don't trust generic metrics. They report spending 60–80% of development time on error analysis and evaluation.

This course therefore teaches **failure-driven evals**: look at real outputs and traces first; name the failures you actually see (open coding → axial coding); write the cheapest check that catches each one (code first, a binary LLM judge only where judgment is needed); put those checks in your test suite with statistics that respect nondeterminism; and gate CI on them. From this module on, every product feature ships with evals, your coding agents must keep them green, and the hidden suite behind Gate G1 uses exactly this machinery.

## Learning outcomes

By the end of C5 you can:

1. **Perform** error analysis on ~100 Fleet Ops traces: open-code the first failure per trace and axial-code the notes into a failure taxonomy with counts.
2. **Build** golden dataset v1 (50 stratified, versioned, human-labeled cases across features and languages) with dev/held-out splits.
3. **Choose** between code-based checks and an LLM-as-judge for each failure mode, and **justify** the choice.
4. **Implement** custom `IEvaluator`s and run them with `Microsoft.Extensions.AI.Evaluation` inside xUnit/MSTest, with response caching and `dotnet aieval` reports.
5. **Write** one binary pass/fail LLM judge for one failure mode and **validate** it against human labels (TPR/TNR).
6. **Apply** statistics for nondeterministic tests: N runs, per-case pass rates, confidence intervals, pass@k vs pass^k, and gating rules that distinguish regressions from noise.
7. **Configure** CI (GitHub Actions with OIDC) to run cached evals on PRs and uncached N-run evals nightly / on prompt or model change, publishing reports as artifacts.
8. **Instruct** coding agents to run evals before claiming done, and **prevent** them from editing golden labels.

## Concepts

### Error analysis first

The Husain/Shankar method (evals FAQ, updated 21 Sep 2026):

1. **Collect diverse traces.** Review ~100; annotate at least the first 30 yourself before letting any LLM suggest failure categories. Keep going until new traces stop revealing new failure modes ("theoretical saturation").
2. **Open coding:** a free-text note on the *first* (most upstream) failure in each trace — "invented a 'Trakia night-driving policy' that doesn't exist", "Latin plate not normalized before tool call", "answered in English to a Bulgarian question". First failure only, because downstream errors are often consequences.
3. **Axial coding:** group notes into a taxonomy of failure modes with counts. An LLM may help cluster; you decide.
4. **Prioritize** by frequency × impact (a rare injury-severity misclassification can outrank a frequent formatting nit).
5. **Write evaluators only for observed failure modes.** Refresh with 100+ new traces every 2–4 weeks plus 10–20 outliers weekly; record non-model problems (missing features, bad data) too.
6. **One "benevolent dictator"** — a domain expert (here: Trakia's dispatch lead persona, played by your peer or instructor) — makes quality calls; with several annotators, label independently and measure agreement first.
7. **Build your own viewer.** A simple tool showing the trace next to the outcome, with keyboard shortcuts for labels, beats a generic UI. Don't outsource core error analysis.

### Golden dataset v1

- **Purpose:** a regression suite for *known* failure modes and core behaviors, not a benchmark of general intelligence.
- **Stratify** on the dimensions that matter for Trakia: feature (extraction / vehicle status / out-of-scope), language (BG Cyrillic, BG Latin-script, EN), expected behavior (answer, tool call, abstain, refuse/contain injection), difficulty (missing fields, two plates, relative dates).
- **Sources:** real traces from your dogfooding (C2–C4) first; synthetic cases to fill gaps using the dimensions → hand-written tuples → generated queries method (generate tuples, then turn each tuple into natural language in a separate step). Synthetic data cannot tell you how *common* a failure is in production.
- **Labels are human-owned** (protected path from C4). Generated labels are drafts until a human signs off.
- **Splits:** `dev` (you iterate on it) vs `heldout` (you look at it rarely). Iterating prompts until dev passes turns dev into training data (C1); Gate G1's hidden suite exists for the same reason.
- **Versioned** (`evals/golden/v1/*.jsonl` + `CHANGELOG.md`): adding a case is a reviewed PR with the trace that motivated it.

```json
{"id":"ext-017","feature":"extract","lang":"bg-latn","split":"dev","critical":false,
 "input":"Kamion PB4521KH, guma spuknala na AM Trakia km 142 dnes 06:40, nqma postradali",
 "expected":{"category":"Tyre","plate":"РВ 4521 КН","roadKm":142,"injuriesReported":false,"cargoDamaged":null},
 "checks":["schema","fields","nulls"],"failureMode":"latin-plate-not-normalized","source":"trace:2026-10-14/7f3c"}
```

### Code-based checks vs LLM-as-judge

| Prefer code-based checks when… | Use an LLM judge when… |
|---|---|
| Output is typed (schema valid, enum fields, normalized plate, ±1 km) | The failure is semantic: "fabricates a Trakia policy", "answer not in the user's language register", "summary omits the injury" |
| A tool must/mustn't be called with specific arguments (inspect `FunctionCallContent`) | Many phrasings are acceptable and rules can't enumerate them |
| Abstention can be detected structurally (typed `abstained: true`, or a refusal code) | Abstention is expressed in free text and must be recognized |
| Forbidden content is lexical (system-prompt fragments, PII patterns) | Judgment requires reading context and output together |

Rules for judges: **binary pass/fail** (not 1–5 Likert scales, which are hard to calibrate, drift and hide disagreement), **one judge per failure mode** (not one omnibus "quality" judge), a short rubric with pass and fail examples, a required one-sentence reason, and **validation against human labels** — report **TPR** and **TNR** separately because classes are imbalanced. Course convention (same as C14, used by all gates): **Pass is the positive class** — TPR = judge says Pass when humans say Pass; TNR = judge says Fail when humans say Fail. TNR is therefore the "catches failures" number; a judge that always says Pass has TPR 1.0 and TNR 0. Full calibration (100–200 labels per failure mode, train/dev/test splits for judge prompts) is C14; in C5 you do a first, smaller validation. The same model may serve as app and judge if it agrees with humans. Don't use BLEU/ROUGE/BERTScore for LLM answers; don't adopt generic "helpfulness/coherence" scores as quality measures.

### Microsoft.Extensions.AI.Evaluation in practice

Packages: `Microsoft.Extensions.AI.Evaluation` (core: `IEvaluator`, metrics), `.Quality` (LLM-judged: Relevance, Completeness, Groundedness, Equivalence, Coherence, Fluency, Retrieval, and agent evaluators IntentResolution, TaskAdherence, ToolCallAccuracy), `.NLP` (BLEU/GLEU/F1), `.Safety` (calls the Foundry Evaluation service: GroundednessPro, ProtectedMaterial, IndirectAttack, CodeVulnerability, content harms), `.Reporting` (response caching, result storage, reports), `.Reporting.Azure` (Azure Storage), `.Console` (the `dotnet aieval` tool). Works under MSTest, xUnit and NUnit; reports can be published in Azure DevOps or as GitHub artifacts.

The built-in quality evaluators are convenient but generic; in this course you use them only where they map to an observed failure mode (e.g., Groundedness in C7). Your C5 evaluators are custom.

```csharp
public sealed class IncidentFieldsEvaluator : IEvaluator
{
    public const string Metric = "incident.fields";
    public IReadOnlyCollection<string> EvaluationMetricNames => [Metric];

    public ValueTask<EvaluationResult> EvaluateAsync(
        IEnumerable<ChatMessage> messages, ChatResponse modelResponse,
        ChatConfiguration? chatConfiguration = null,
        IEnumerable<EvaluationContext>? additionalContext = null, CancellationToken ct = default)
    {
        var expected = additionalContext!.OfType<ExpectedIncidentContext>().Single().Expected;
        var (pass, reason) = IncidentChecks.Compare(modelResponse.Text, expected); // schema + fields + null-correctness
        var metric = new BooleanMetric(Metric, pass, reason);
        metric.Interpretation = new EvaluationMetricInterpretation(
            pass ? EvaluationRating.Good : EvaluationRating.Unacceptable, failed: !pass, reason: reason);
        return new(new EvaluationResult(metric));
    }
}
```

```csharp
// Shared fixture (xUnit). Verify factory/method names against your package version.
Reporting = DiskBasedReportingConfiguration.Create(
    storageRootPath: Paths.EvalResults,
    evaluators: [new IncidentFieldsEvaluator(), new ToolRoutingEvaluator(), new PolicyFabricationJudge()],
    chatConfiguration: new ChatConfiguration(judgeClient),
    enableResponseCaching: true,
    executionName: Env("GITHUB_RUN_ID") ?? $"local-{DateTime.UtcNow:yyyyMMdd-HHmm}");

[Theory, Trait("Category", "Eval")]
[MemberData(nameof(Golden.Extraction), MemberType = typeof(Golden))]
public async Task Extraction(GoldenCase c)
{
    await using ScenarioRun run = await _fx.Reporting.CreateScenarioRunAsync($"extract/{c.Id}", iterationName: _fx.Iteration);
    var messages = IncidentPrompt.Build(c.Input);                       // the product's real prompt template
    ChatResponse response = await _fx.AppClient(run).GetResponseAsync(messages, IncidentPrompt.Options);
    EvaluationResult result = await run.EvaluateAsync(messages, response,
        additionalContext: [new ExpectedIncidentContext(c.Expected)]);
    _fx.Record(c, result);                                              // aggregate for statistics & gating
}
```

**Response caching:** while the request (prompt, options, model) is unchanged, responses — app and judge calls routed through the reporting configuration's chat client — are replayed from disk, so repeated CI runs are cheap and deterministic. That is perfect for catching *code* regressions and useless for measuring *model* variance. Hence two run types (below). Reports: `dotnet aieval report --path <storageRoot> --output report.html` (verify flags for your tool version).

### Statistics for nondeterministic tests

- **One run is an anecdote.** Run each case N times (N = 3 for PR-adjacent uncached runs, 5–10 nightly for critical slices).
- **Per-case pass rate** p̂ᵢ = passes/N; classify cases as *stable pass*, *stable fail* or *flaky*. Flaky cases are information (ambiguous spec, borderline prompt), not noise to suppress.
- **Suite metrics:** *pass-all rate* (share of cases passing all their checks) plus per-check and per-failure-mode rates. Report per slice (BG vs EN!).
- **Confidence intervals:** with 50 cases and an observed 90% pass rate, the 95% Wilson interval is ≈ 79%–96%. A drop from 90% to 86% on 50 cases is *not* evidence of regression. Use paired comparisons (same cases, before vs after; McNemar's test or simply count cases that flipped pass→fail vs fail→pass) instead of comparing two percentages.
- **pass@k vs pass^k:** pass@k = at least one of k attempts succeeds (fine for "can it ever do this?"); **pass^k** = all k succeed (τ-bench's reliability measure, the right one for production behavior). Critical cases (injury → severity ≥ High; never fabricate policy) should be gated on pass^k.
- **Gating rules** that work at small n: (1) every `critical` case passes all N runs; (2) no stable-pass case flips to stable-fail; (3) suite pass-all rate's Wilson lower bound ≥ agreed floor; (4) cost per run within budget.

### CI design

| Trigger | Cache | Runs | Gate |
|---|---|---|---|
| PR touching `src/**` | On (replay) | 1 | All critical pass; pass-all ≥ floor; no stable flips (vs baseline results) |
| PR touching `prompts/**`, `models.json`, `evals/**` | Off for affected slices | N = 3 | Rules 1–4 above |
| Nightly | Off | N = 5 | Report + open issue on regression (detects provider-side drift) |

Use OIDC (`azure/login` with a federated credential) — no stored keys. Publish the `dotnet aieval` HTML report and a Markdown summary (per slice, per failure mode, flips) as artifacts and as a PR comment. Keep the golden set small and fast; G1's hidden suite is larger.

### What NOT to do

- Writing evaluators for imagined failures before reading traces.
- 1–5 Likert judges and "overall quality" scores.
- Generic metrics (helpfulness, coherence, BLEU/ROUGE) as release gates.
- Exact-string assertions on model output.
- Tuning prompts against the held-out split.
- Letting an LLM (or a coding agent) write the expected labels unsupervised.
- Treating a 2–4 point change on 50 cases as signal.
- Running N repetitions with response caching on and calling it a variance measurement.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| `Microsoft.Extensions.AI.Evaluation` (+ `.Quality`, `.NLP`, `.Safety`, `.Reporting`, `.Reporting.Azure`) | Evaluators, caching, reports | Package versions/status: verify on NuGet before teaching | `.Safety` calls the Foundry Evaluation service (Entra ID) |
| `Microsoft.Extensions.AI.Evaluation.Console` (`dotnet aieval`) | HTML reports from stored results | Verify | Install as local dotnet tool |
| xUnit / MSTest | Test host | GA | Trait/Category `Eval` separates eval tests |
| GitHub Actions (`azure/login` OIDC, `actions/cache`, `actions/upload-artifact`) | CI | GA | Azure DevOps equivalent shown in C19 |
| Foundry evaluations (cloud, continuous) | Later (C14/C15) | GA (evals/monitoring/tracing Mar 2026, per practitioner blog); some evaluators preview | Authoring samples largely **[Python]** (`azure-ai-evaluation`) |
| Course `tools/TraceViewer` (Blazor) + `tools/EvalGate` | Error analysis UI, gating logic | Course code | You extend both |

## Labs

### Lab 1 — Look at the data: error analysis on 100 traces (≈2.5h)

- **Goal:** A failure taxonomy for Fleet Ops grounded in real outputs.
- **Start state:** `c5/lab1-start` (`tools/TraceViewer`, `scripts/traffic.ps1` that replays 120 realistic BG/EN driver and dispatcher messages through Ask Fleet Ops and `/incidents/extract`, storing prompt id/version, messages, tool calls, outputs and cost per trace in `evals/traces/*.jsonl`).
- **Steps:**
  1. Run the traffic script against your C4 product (`chat-fast`). Add 20+ traces from your own dogfooding.
  2. In the TraceViewer, review traces in random order. For each: pass/fail and, if fail, a one-line open code for the **first** failure. Annotate the first 30 without any AI help.
  3. Continue to ~100 or until saturation. Export notes.
  4. Axial coding: group into 5–10 failure modes with counts and examples (you may ask an LLM to *propose* clusters; you decide). Expected candidates: policy fabrication; abstention phrased as fabrication-with-disclaimer; Latin-script plate handling; wrong reply language; relative date resolution; tool not called / called for general questions; injury inferred without evidence; injection followed.
  5. Prioritize by frequency × impact; pick the top 3 for Labs 2–3.
  6. Peer calibration: exchange 20 traces with a peer, label independently, compute raw agreement and discuss disagreements (Cohen's kappa optional).
- **Break it:** Ask an LLM to produce a failure taxonomy *without* you reading traces, then compare it with yours. Mark categories it invented that never occurred and real ones it missed.
- **Acceptance criteria:** `evals/error-analysis/2026-xx-taxonomy.md` with ≥ 100 coded traces, 5–10 failure modes with counts, examples (trace IDs), priority ranking and the LLM-taxonomy comparison; peer-agreement number recorded.
- **Stretch:** Add keyboard shortcuts and a "first failure" field to the TraceViewer; time your labeling speed before/after.

### Lab 2 — Golden dataset v1 and code-based evals in xUnit (≈2.5h)

- **Goal:** 50 stratified cases with code-based evaluators running under MEAI.Evaluation with caching and reports.
- **Start state:** `c5/lab2-start` (`tests/FleetOps.Evals` with fixture skeleton; `evals/golden/v1/` empty).
- **Steps:**
  1. Build 50 cases (≥ 50% Bulgarian, ≥ 6 Latin-script): 20 extraction (incl. 4 adversarial, 4 with missing fields), 15 vehicle status (10 requiring the tool, 5 invalid/nonexistent plates), 10 out-of-scope policy questions that must be abstained from (Fleet Ops has no documents until C7), 5 general/safety. Mark ≥ 8 as `critical`. Assign ~70% `dev`, ~30% `heldout`. Every case cites the trace or tuple it came from.
  2. Implement evaluators: `IncidentFieldsEvaluator` (schema, fields, null-correctness — reuse C3 checks), `ToolRoutingEvaluator` (inspects `FunctionCallContent` in the response messages: tool called iff expected, normalized plate argument), `AbstentionCheck` (structural: the product now returns a typed `answerKind: Answer|Abstain|Refuse` alongside text — add it if missing; this is a product improvement driven by evals).
  3. Wire the fixture with `DiskBasedReportingConfiguration`, response caching on, execution name from env.
  4. Run `dotnet test --filter Category=Eval`; generate `dotnet aieval report`; open the HTML report.
  5. Re-run: confirm the second run is fast and costs ~€0 (cache hits visible in your C2 cost ledger as zero-cost — or absent, depending on where caching sits; explain which).
- **Break it:** Change one word in the extraction prompt template and re-run: confirm cache misses only for affected scenarios. Then point `chat-fast` to Foundry Local via config and run — record per-slice deltas.
- **Acceptance criteria:** 50 cases validate against `evals/golden/schema.json` (CI check); stratification report auto-generated (`tools/EvalGate stats`) shows required quotas; eval tests run in < 5 min cached; HTML report artifact produced; `evals/golden/**` is a protected path in AGENTS.md and Claude settings (C4).
- **Stretch:** Add a `Category=EvalSmoke` subset (10 cases, < 60 s) for the agent's Stop hook.

### Lab 3 — One binary LLM judge, validated (≈1.75h)

- **Goal:** A judge for the top semantic failure mode — **policy fabrication** — that agrees with humans.
- **Start state:** `c5/lab3-start` (`evals/judges/policy-fabrication/labels.jsonl` — 60 traces labeled by the instructor-as-domain-expert; you add 20 of your own).
- **Steps:**
  1. Write the judge prompt as a versioned template (`prompts/judges/policy-fabrication.md`): definition of failure ("states or implies a specific Trakia policy, rule, number or procedure not provided in context"), 2 pass and 2 fail examples (BG and EN), output schema `{ "pass": bool, "reason": string }` via structured output.
  2. Implement `PolicyFabricationJudge : IEvaluator` using `chatConfiguration.ChatClient` and `GetResponseAsync<JudgeVerdict>`.
  3. Split labels: 20 for prompt iteration (dev), 60 held out. Measure TPR and TNR on dev, iterate the judge prompt (≤ 3 iterations), then measure once on held-out.
  4. Compare judge models: `chat-fast` vs `chat-reasoning` (cost per 100 judgments vs TPR/TNR).
- **Break it:** Replace the binary rubric with "rate fabrication risk 1–5" and threshold at ≥ 3. Measure agreement and stability across 3 runs. Explain why it's worse.
- **Acceptance criteria:** `evals/judges/policy-fabrication/validation.md` with dev and held-out TPR/TNR (target held-out TPR ≥ 0.85 and TNR ≥ 0.85; if not reached, document the disagreement analysis instead of tuning on held-out); judge wired into the golden suite for the 10 out-of-scope cases; judge prompt hash recorded in results.
- **Stretch:** Have a peer label 20 cases blind; compute human–human agreement and compare it with judge–human agreement.

### Lab 4 — CI gate with statistics, and agents that run evals (≈1.25h)

- **Goal:** Evals gate PRs and run nightly with N-run statistics; agents can't claim done without them.
- **Start state:** `c5/lab4-start` (`tools/EvalGate` computes pass-all, Wilson bounds, flips vs a baseline file).
- **Steps:**
  1. Create `.github/workflows/evals.yml`:
     ```yaml
     name: evals
     on:
       pull_request: { paths: ['src/**', 'prompts/**', 'evals/**', 'models.json'] }
       schedule: [{ cron: '17 2 * * *' }]
     permissions: { id-token: write, contents: read, pull-requests: write }
     jobs:
       eval:
         runs-on: ubuntu-latest
         env:
           EVAL_RUNS: ${{ github.event_name == 'schedule' && '5' || '1' }}
           EVAL_DISABLE_CACHE: ${{ github.event_name == 'schedule' && 'true' || 'false' }}
         steps:
           - uses: actions/checkout@v4
           - uses: actions/setup-dotnet@v4
             with: { global-json-file: global.json }
           - uses: azure/login@v2
             with: { client-id: ${{ vars.AZURE_CLIENT_ID }}, tenant-id: ${{ vars.AZURE_TENANT_ID }}, subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }} }
           - uses: actions/cache@v4
             if: github.event_name == 'pull_request'
             with: { path: eval-results/cache, key: evalcache-${{ hashFiles('prompts/**', 'models.json', 'evals/golden/**') }}, restore-keys: evalcache- }
           - run: dotnet test tests/FleetOps.Evals --filter Category=Eval
           - run: dotnet tool restore && dotnet aieval report --path eval-results --output eval-report.html
           - run: dotnet run --project tools/EvalGate -- --results eval-results --baseline evals/baseline.json --min-wilson-lower 0.80 --critical-pass-all
           - uses: actions/upload-artifact@v4
             if: always()
             with: { name: eval-report, path: eval-report.html }
     ```
     (Pin action versions per course release; for prompt/model-change PRs, a path filter job sets `EVAL_RUNS=3` and disables cache for affected slices.)
  2. Add a federated credential for the repo on a dedicated app registration with only the model-calling role on the Foundry resource.
  3. Make `EvalGate` post a PR comment: per-slice pass rates with Wilson intervals, critical failures, stable flips.
  4. Update AGENTS.md: "Before claiming done on any change under `src/`, `prompts/` or `models.json`, run `dotnet test --filter Category=EvalSmoke` and report the summary. Never edit `evals/golden/**` or `evals/baseline.json`." Extend the C4 Stop hook to run `EvalSmoke` when prompts changed.
  5. Have your coding agent implement a small prompt improvement for your #1 failure mode via the factory; the PR must pass the gate.
- **Break it:** Introduce a deliberate regression (remove the plate normalizer call). Confirm the PR gate fails with a clear message. Then run the suite uncached with N=1 three times on an unchanged commit and show that suite-level percentage moves within the Wilson interval — and that your gate did not flap.
- **Acceptance criteria:** `evals.yml` green on a clean PR, red on the regression PR with critical case named; nightly run produces a report artifact; `evals/baseline.json` committed; Stop hook runs `EvalSmoke` on prompt changes; agent-made PR merged through the gate.
- **Stretch:** Open an issue automatically from the nightly run when any stable-pass case becomes flaky, assigning it to triage.

## Kata

**"Trace → check"** (20–30 min, repeat weekly for the rest of the course). Pull 10 fresh traces (random + 2 lowest-rated). Open-code first failures. For any *new* failure mode: write one golden case from the trace, decide code-check vs judge in one sentence, implement the cheapest check, run it N=3. Variations: a Bulgarian-only batch; traces from a different model role; traces produced by your coding agent's recent change.

## Product increment — Fleet Ops Copilot

**Golden dataset v1** (50 stratified BG/EN cases with dev/held-out splits and critical flags), code-based evaluators for extraction, tool routing and abstention, one validated binary judge for policy fabrication, and eval tests in CI (cached on PRs, uncached N-run nightly) with HTML reports. Driven by error analysis, the product gained a typed `answerKind` (Answer/Abstain/Refuse) and at least one prompt fix for the top failure mode. Ready for **Gate G1**.

## Factory increment — your agentic SDLC

Eval tests are runnable by agents (`dotnet test --filter Category=EvalSmoke|Eval` + `dotnet aieval report`); AGENTS.md instructs agents to run them before claiming done; the Stop hook enforces `EvalSmoke` on prompt changes; golden labels and baselines are protected paths; `EvalGate` posts statistics to PRs; OIDC-only access from CI. The TraceViewer and the weekly trace kata are your standing error-analysis loop.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Error analysis | Skims a few outputs | Codes traces, ad-hoc categories | ≥ 100 traces, first-failure open coding, axial taxonomy with counts and priorities | Saturation argued; peer agreement measured; non-model problems captured; taxonomy drives roadmap |
| Dataset design | Random examples | Covers features | Stratified, BG-heavy, sourced, split, versioned, critical flags | Explicit coverage rationale; held-out discipline; change log tied to traces |
| Evaluator choice & quality | Generic metrics / Likert | Some custom checks | Code checks first; one binary judge per mode validated with TPR/TNR | Judge validated on held-out without leakage; cost/accuracy of judge models compared |
| Statistics & gating | Single run, exact thresholds | Repeated runs | Per-case rates, Wilson intervals, pass^k for critical cases, paired flips | Gate demonstrated not to flap on noise yet catch real regressions; cache vs variance trade-off explained |
| Factory integration | Manual runs | CI runs evals | PR + nightly + reports + agent instructions | Agents demonstrably blocked by gates; protected labels; regressions auto-ticketed |

**Auto-checked:** golden schema and stratification quotas; `evals.yml` status on the clean and regression PRs; presence and format of taxonomy and judge validation files; protected-path rules; EvalGate thresholds; G1's hidden suite runs against this harness.

## Common pitfalls

- Starting with the eval framework instead of the traces.
- Coding *all* failures in a trace instead of the first one.
- A single omnibus judge; numeric scores without calibration.
- Validating a judge on the same examples used to write its prompt.
- Golden sets that are 80% English for a 60% Bulgarian user base.
- Forgetting that response caching makes repeated runs identical.
- Gating on tiny percentage changes; or the opposite — no gate at all because "LLMs are nondeterministic".
- Letting the coding agent "fix" an eval failure by editing the expected output.
- Long-lived Azure keys in CI secrets instead of OIDC.


## References

- Hamel Husain & Shreya Shankar, LLM evals FAQ (updated 21 Sep 2026): https://hamel.dev/blog/posts/evals-faq/
- Hamel Husain, Using LLM-as-a-Judge: https://hamel.dev/blog/posts/llm-judge/
- Microsoft.Extensions.AI.Evaluation libraries (packages, evaluators, caching, `dotnet aieval`): https://learn.microsoft.com/en-us/dotnet/ai/evaluation/libraries
- How to evaluate AI agents in Microsoft Foundry (practitioner blog; GA status claims): https://jannikreinhard.com/microsoft-foundry-agent-evaluations/
- τ-bench (pass^k reliability): https://arxiv.org/abs/2406.12045
- Thinking Machines Lab, nondeterminism in LLM inference: https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
- OpenAI, Why language models hallucinate (rewarding abstention): https://openai.com/index/why-language-models-hallucinate/
- Chip Huyen, *AI Engineering* (two chapters on evaluation): https://github.com/chiphuyen/aie-book/blob/main/ToC.md
- Wilson score interval (background): https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Wilson_score_interval
- GitHub Actions OIDC with Azure (`azure/login`): https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect
