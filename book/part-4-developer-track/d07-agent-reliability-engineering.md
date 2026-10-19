# D7 — Agent reliability engineering

> **Level:** Expert (AI Solution Developer track) · **Duration:** 18h (theory 25% / labs 75%) · **Prerequisites:** Core C0–C19 and Gate G3; especially C5/C14 (evals, calibrated judges), C15 (tracing, versioning), C17 (APIM, deployment); D2 (durable agents) and D5 (CPST) recommended · **Volatility:** Medium (methods are stable; Foundry evaluator status, benchmark leaderboards and tooling change quarterly)

## Why this matters

A proficient practitioner has an eval suite, an LLM judge and a CI gate. An expert treats agent reliability **statistically and operationally**:
- measures whether the agent succeeds **every** time (pass^k), not whether it *can* succeed (pass@1);
- tells a real regression from noise with the right test and sample size;
- covers the long tail with simulated users and environments;
- injects faults into tools and models to prove graceful degradation;
- runs agent behaviour under SLOs with error budgets;
- writes postmortems whose output is new evals;
- reads every benchmark claim, including vendors' and Microsoft's own, with a critic's eye.

The τ-bench authors introduced **pass^k** precisely because agents that look strong at pass@1 collapse when asked to succeed consistently. If one trial succeeds with p = 0.9 and trials are independent, pass^4 ≈ 0.66 and pass^8 ≈ 0.43.

Trakia now runs the Fleet Assistant, the Fleet Analyst, the incident workflow, the durable planner, the voice assistant and two customer pilots. Last month three things happened:
- A provider-side model update shifted the Fleet Assistant's tool-calling behaviour, and maintenance bookings started missing the depot parameter. The cached CI evals stayed green.
- A dispatcher "flaky test" was quarantined for weeks. It turned out to be a real 12% failure mode on Bulgarian plates.
- A conference talk claimed a memory feature gave "+14% on τ-bench", and someone proposed adopting it immediately. Microsoft's own two posts disagree on the size of that gain (≈5% vs 7–14%).

Reliability engineering is the discipline that would have caught all three.

## Learning outcomes

1. **Build** a τ-bench-style simulation harness (LLM user simulator, policy document, tool backends over a database snapshot, end-state graders) for a Trakia agent, and **audit** simulator-induced false failures.
2. **Curate** a versioned scenario library with an explicit taxonomy and coverage matrix, fed by production failures and synthetic tuples.
3. **Quantify** reliability with pass@1, pass^k and per-scenario success rates with confidence intervals, and **distinguish** flaky scenarios from hard ones and regressions from noise (paired tests, sample-size planning).
4. **Design and run** chaos experiments for tools and models (errors, latency, malformed results, 429s, model swap, retirement `410 Gone`, injection) with steady-state hypotheses and expected behaviours.
5. **Define** agent SLIs/SLOs (task success, safety violations, escalations, latency, CPST) with error budgets and multi-window burn-rate alerts, including measurement error from judges.
6. **Operate** continuous evaluation in production (sampling, online judges, canary comparisons, drift detection), and **feed** it back into offline suites.
7. **Lead** a blameless postmortem for an AI failure that produces concrete new scenarios, checks and guardrails.
8. **Critique** public benchmark and vendor claims (SWE-bench, Terminal-Bench, GAIA, τ-bench, OSWorld): saturation, harness effects, contamination, variance, cost.

## Concepts

### 1. Reliability is not accuracy

| Metric | Definition | Answers |
|---|---|---|
| pass@1 | Success rate of a single attempt (averaged over scenarios) | "How good is it typically?" |
| pass@k | ≥ 1 success in k attempts | "Can it ever do this?" (useful with a verifier and retries) |
| **pass^k** | All k attempts succeed | "Will it do this *every time* a user asks?" |
| Per-scenario success distribution | Success rate per scenario across N trials | "Which scenarios are reliable, flaky or broken?" |

Users experience per-attempt behaviour, repeatedly. A dispatcher who asks 30 questions a day experiences pass^30 on a scenario family, not pass@1. Report pass^k alongside pass@1 for agentic tasks with side effects. Track the **share of scenarios with success ≥ 0.95** (the "reliable set"); it is more actionable than the mean.

Non-determinism is structural. Temperature 0 is not deterministic in production serving, because inference kernels are not batch-invariant. Your tests must therefore be statistical. Use MEAI.Evaluation response caching to make PR-time CI *repeatable* for unchanged prompts. Never mistake that for reliability, and always run an **uncached** suite nightly against live endpoints.

### 2. Simulation-based testing (τ-bench style)

τ-bench evaluates tool-agent-user interaction with four parts:
- an **LLM-simulated user** that has a goal and private information;
- a **domain policy** document;
- **tools** over a database;
- a check of the **database end state** against the goal.

**τ²-bench** adds dual-control environments in which the user also acts on the world. The design lesson: grade **outcomes and policy adherence**, not the exact turn-by-turn path. Stateful agents can reach the right end state many ways.

**TrakiaSim** generalises the C14 Lab 3 dispatcher simulator (one persona family, 30 scenarios, pass^4) into a reusable, statistically sound harness. Do not rebuild C14's simulator; extend it:
- **Environment:** a containerized SQL Server snapshot of `TrakiaOps` (reset per episode), the mock ticketing, scheduling and parts APIs, and the real Trakia MCP server.
- **Simulated users:**
  - a dispatcher (terse, Bulgarian/English code-switching);
  - a customer-service agent (relays a customer's angry email);
  - a driver (voice transcripts from D3);
  - an adversarial user (pressure to bypass approval).
  
  Each has a **goal**, **known facts**, **hidden facts** revealed only if asked, and a **termination rule**.
- **Policy:** excerpts of the fleet policy handbook, for example "maintenance bookings require depot capacity check; urgent DTCs override routing".
- **Graders:**
  - (a) end-state diff (expected rows created or updated, nothing else changed);
  - (b) policy-violation checks in code (booking without a capacity check, notification before approval);
  - (c) a calibrated judge for conversational requirements (asked for missing info, confirmed before acting, language matched).

**Simulator fidelity is a threat to validity:**
- simulated users are often too cooperative, too verbose, or leak hidden facts early;
- they also make mistakes that cause **false failures**.

Mitigations:
- calibrate personas against 30+ real transcripts;
- run the simulator at low temperature with a different model family from the agent's (reduces correlated blind spots);
- **audit every failure cluster** and label it "agent fault", "simulator fault" or "scenario bug";
- report the agent's pass rate only over valid episodes, and track the simulator fault rate as a metric.

### 3. Scenario libraries

A scenario is data: `{id, version, persona, goal, hidden_facts, initial_db_fixture, policy_refs, expected_end_state, checks[], tags[]}`.

- **Taxonomy dimensions:**
  - intent family;
  - complexity (number of tools and turns);
  - language (BG/EN/mixed);
  - data condition (missing, stale, conflicting);
  - permission context (role);
  - adversarial type (injection, social pressure);
  - modality (text/voice).
  
  Maintain a **coverage matrix** and target the cells that production traffic and risk say matter. Do not aim for uniform coverage.
- **Sources:**
  1. **production failures** from error analysis and postmortems (highest value);
  2. synthetic tuples: define the dimensions, hand-write about 20 tuples, generate more, then turn each tuple into a scenario in a separate step and review it by hand (Hamel & Shankar);
  3. policy-derived edge cases;
  4. red-team findings (C14/C16).
  
  Synthetic data cannot tell you how *frequent* a failure is. Use production sampling for that.
- **Sets:**
  - **smoke** (20, every PR, cached);
  - **regression** (150–300, every PR touching prompts, tools or models, multiple trials, nightly uncached);
  - **exploratory/long-tail** (weekly);
  - **holdout** (never used for tuning; quarterly, to detect overfitting to the suite).
- **Versioning:** scenarios evolve with policy. Pin each suite version in the eval report and keep the old versions for trend comparability.

### 4. Statistics for regression gates and flakiness

- **Confidence intervals.** 45/50 successes is 90%, with a Wilson 95% CI of ≈ 79–96%. A 50-scenario suite cannot distinguish 88% from 92%. Report intervals, always.
- **Sample size.** To detect a drop from 90% to 85% with an unpaired two-proportion test (α = 0.05 two-sided, power 0.8), you need ≈ 690 episodes per arm. **Paired** designs (the same scenarios under both versions) are far more efficient. Use **McNemar's test** on discordant pairs, and with multiple trials per scenario, a paired test on per-scenario success rates (or a permutation test).
- **Pre-register the primary metric.** Gate on 1–2 primary metrics (for example, task success on the regression set, and safety violations = 0 on the safety set). Monitor the others. With 20 metrics at α = 0.05, one "regression" per run is expected by chance. Correct with Holm if you must gate on many.
- **Flaky vs hard vs regressed.** Run each scenario N = 5–10 times:
  - success near 0 → **broken/hard**: fix the agent or the scenario;
  - near 1 → **reliable**;
  - in between → **flaky**: a real reliability defect *or* a scenario/simulator defect.
  
  **Never auto-quarantine flaky agent scenarios.** Quarantine is legitimate only after an audit attributes the variance to the simulator or the environment, and the scenario is fixed within an SLA.
- **Variance decomposition.** Separate between-scenario variance (difficulty) from within-scenario variance (stochasticity). A change that lowers within-scenario variance at equal mean is a reliability improvement worth shipping.
- **Cost.** Trials multiply cost (scenarios × trials × tokens). Use cached PR runs, a smaller smoke set, nightly full runs and budget caps (D5).

### 5. Chaos engineering for agents

Start from a **steady-state hypothesis** ("≥ 95% of booking scenarios succeed or escalate correctly"). Inject one fault class at a time, observe, and widen the blast radius gradually.

| Fault | Injection point | Expected agent behaviour |
|---|---|---|
| Tool 5xx / timeout | Tool wrapper, toxiproxy | Code retries with backoff (not the model); after N failures, an actionable error message to the model; graceful partial answer or escalation |
| Tool returns malformed or partial data | Tool wrapper | Schema validation catches it; the model is told *what* is wrong; no fabricated fill-in |
| Slow tool (P99 × 10) | Latency injection | Timeout budget respected; user informed (D4); no duplicate side effects on retry (D2 idempotency) |
| 429 with `Retry-After` | APIM fault policy / mock backend | Honour `Retry-After`; spill to the secondary pool (D5); no retry storm |
| **Model swap** (new version, router change, fallback model) | Config via `IChatClient` registration | Eval deltas within tolerance; tool-call argument accuracy unchanged; if not, the gate blocks the promotion |
| Model **retired → `410 Gone`** | Mock backend | Fail over to the configured successor; alert; no silent outage. GA models are deprecated at 12 months and retired at 18; partner models get 12 months (Grok sometimes 6); notice is ≥ 60 days; dates cannot be extended |
| Context pressure (huge tool result, long session) | Tool wrapper | Truncation/pagination or compaction kicks in; no lost instructions |
| Stale or conflicting data | DB fixture | The agent surfaces the conflict, prefers the authoritative source, cites the version |
| Injected instructions in tool results | Tool wrapper | No consequential action (C16 patterns); a violation counts as a safety SLI breach |

In .NET, faults are injected as **middleware**, so the same agent code is tested:

```csharp
public sealed class ChaosChatClient(IChatClient inner, ChaosPolicy policy) : DelegatingChatClient(inner)
{
    public override async Task<ChatResponse> GetResponseAsync(IEnumerable<ChatMessage> messages,
        ChatOptions? options = null, CancellationToken ct = default)
    {
        if (policy.ShouldFail("model.429")) throw new HttpRequestException("429", null, HttpStatusCode.TooManyRequests);
        if (policy.ShouldFail("model.410")) throw new HttpRequestException("410 Gone", null, HttpStatusCode.Gone);
        await policy.MaybeDelayAsync("model.latency", ct);
        return await base.GetResponseAsync(messages, options, ct);
    }
}
// Tools: wrap each AIFunction with ChaosToolDecorator (errors, latency, malformed JSON, injected text) — same ChaosPolicy, seeded per episode.
```

Run chaos in **TrakiaSim** (the simulator plus faults), not only in unit tests. Behaviour under faults is a property of the whole loop.

### 6. Benchmark literacy

| Benchmark | Measures | Read with care because |
|---|---|---|
| SWE-bench / **Verified** (500 human-validated tasks) | Resolving real GitHub issues, verified by tests | Saturating (Vals AI archived its coverage citing saturation); the harness/scaffold matters as much as the model; contamination risk |
| Terminal-Bench | Agent tasks in real terminals | Newer, differentiating in 2026; harness-dependent |
| GAIA | General assistant tasks (reasoning, browsing, tools); humans ≈ 92% at release | Web drift changes answers; tool set matters |
| τ-bench / τ²-bench | Tool-agent-user interaction with policies; pass^k | Simulator fidelity; domain is retail/airline/telecom, not yours |
| OSWorld | Real OS tasks for computer-use agents | Environment setup variance; pixel vs accessibility approaches |

A checklist for any claim, including vendor and Microsoft posts:
1. Who ran it (vendor-run or independent)?
2. Which harness/scaffold, which settings (effort, tools, retries, best-of-n)?
3. pass@1 or best-of-k? Is variance reported?
4. Is cost per task reported?
5. Is there a contamination analysis?
6. Is the gain relative or absolute, against which baseline?
7. Does the task distribution resemble ours?

Course examples:
- Anthropic's multi-agent system beat single-agent Opus by **90.2% on an internal eval**: not reproducible by you, but internally consistent with token-usage findings.
- Microsoft's procedural memory: "≈5% on STATE-Bench and τ-bench" in one post vs "+7–14% absolute on τ-bench" in another.
- Mem0's vendor-authored LOCOMO gains are publicly disputed by Letta.

The expert response: "promising; run it on TrakiaSim with pass^k before adopting".

### 7. SLOs for agents

| SLI | Measurement | Example SLO (Fleet Assistant) |
|---|---|---|
| Task success | Online sampled judges (calibrated, TPR/TNR known) + outcome signals (no human override, no rollback) | ≥ 92% over 28 days |
| Safety violations | Policy-check failures, guardrail-confirmed unsafe actions | 0 critical; ≤ 0.1% minor |
| Escalation rate | Agent → human handoffs | 5–15% (too low can mean overconfidence) |
| Latency | P95 E2E / TTFT per task type | P95 ≤ 6 s (analyst), ≤ 2.5 s (assistant) |
| Availability | Non-error responses / requests | ≥ 99.5% |
| Cost | CPST (D5) | ≤ €0.04 per successful assistant task |

- **Error budgets** and **multi-window burn-rate alerts** (for example, 1h and 6h windows at 14× and 6× burn) apply as in classic SRE, with one twist.
- **Judge-based SLIs carry measurement error.** A judge with TPR 0.92 and TNR 0.95 biases the observed success rate. Correct for it (Rogan–Gladen style: true ≈ (observed + TNR − 1)/(TPR + TNR − 1)) or report the bounds.
- **Sample enough traffic for the alert windows.** Low-traffic tenants need longer windows.
- Separate **behavioural SLOs** (success, safety) from **infrastructure SLOs** (availability, latency). A behavioural burn should page the AI owner, not the platform on-call.

### 8. Continuous evaluation in production

- **Sampling:** random (unbiased SLI estimation) plus **targeted** (thumbs-down, retries, long traces, unusual tool sequences, new intents). Keep the two pools separate, because targeted samples bias rates.
- **Online judges:** small, calibrated, cost-capped. **Foundry continuous evaluation** samples live agent responses, scores quality and risk dimensions, shows results on the agent's Monitor tab and supports alerts. It requires App Insights and the project managed identity with the Foundry User role. Some agent evaluators are still preview, and per a practitioner source, evaluations, monitoring and tracing reached GA in March 2026.
- **Canary and shadow:** route 5–10% through APIM weighted backends to the new model or prompt version, then compare SLIs with a paired-by-intent analysis before promotion. Shadow mode (run the new version without showing the result) for side-effect-free tasks.
- **Drift:**
  - input drift: intent mix, language mix, token lengths;
  - output drift: length, tool-usage patterns, refusal rate;
  - judge pass-rate drift;
  - the provider changing under you, detected by the nightly *uncached* golden run.
- **The loop:** online failures → error analysis queue → new scenarios in TrakiaSim → regression set. A failure seen twice in production without a scenario is a process defect.

### 9. Postmortems for AI failures

Use the classic blameless format plus AI-specific sections:
- **Versions at incident time:** model and deployment version, router version, prompt/agent definition hash, tool contract versions, index alias/corpus version, guardrail config, cache state.
- **Failure class:** provider drift, prompt change, retrieval/index, tool contract change, injection/abuse, runaway cost, unsafe action, regulated-value hallucination, simulator/eval blind spot.
- **"Why didn't our evals catch it?"** This section is mandatory. Typical answers: no scenario covered it, the judge was miscalibrated, the cached CI masked drift, flaky-quarantined, SLI not sampled.
- **Outputs:** ≥ 1 new scenario, ≥ 1 new check or judge, a guardrail or design change, SLO or alert tuning, and an owner and date for each.
- **Regulatory hooks:** personal-data leaks trigger GDPR breach assessment (72-hour notification duty). For high-risk systems, AI Act serious-incident duties apply once the Annex III obligations take effect (2 Dec 2027 after the Digital Omnibus). Know which applies to which Trakia component (C18).

**Misconceptions to unlearn:**
- "Green CI = reliable." Cached, single-trial, small-N suites prove little.
- "Flaky tests are noise." In agents, flakiness *is* the reliability defect.
- "A leaderboard win transfers to our domain."
- "The judge's score is the truth." It is a measurement instrument with error rates.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| `Microsoft.Extensions.AI.Evaluation` (+ `.Quality`, `.Safety`, `.Reporting`, `dotnet aieval`) | Evaluators, caching, reports in xUnit/MSTest | GA (verify package versions on NuGet) | Agent evaluators: IntentResolution, TaskAdherence, ToolCallAccuracy |
| MEAI `DelegatingChatClient` / MAF middleware | Chaos injection, budgets | GA | Same code path as production |
| Foundry evaluations & continuous evaluation | Cloud/agent evaluators, live sampling, alerts | GA (Mar 2026 per practitioner source); some evaluators preview | Cloud evaluation authoring is mostly **[Python]** (`azure-ai-evaluation`) |
| Foundry Rubric evaluator | Weighted custom criteria | Preview | |
| Azure Monitor / App Insights (KQL, alerts, workbooks) | SLIs, burn-rate alerts | GA | GenAI semconv "Development": pin and map |
| APIM weighted/priority backends, fault simulation via policies | Canary, 429/latency chaos at the gateway | GA | |
| toxiproxy / Chaos Studio | Network-level fault injection | OSS / GA | Chaos Studio for Azure-resource faults |
| SQL Server 2025 container | Resettable environment snapshots for simulation | GA | |
| Azure SRE Agent | Incident triage over App Insights/Monitor | GA per secondary source (Mar 2026); Reader/Privileged modes; 3 regions | Use Reader mode in labs |
| τ-bench / τ²-bench (reference implementations) | Methodology reference | Research code | **[Python]** reading only; TrakiaSim is .NET |

## Labs

Lab repo: `trakia-fleetops`, folder `reliability/` (`TrakiaSim` .NET project, `scenarios/` YAML library, `chaos/` policies, `slo/` Bicep for alerts and workbooks).

### Lab 1 — TrakiaSim: a τ-bench-style harness for the Fleet Assistant (≈5h)

- **Goal:** Measure the Fleet Assistant's reliability on realistic multi-turn tasks with end-state grading and pass^k.
- **Start state:** tag `d7/lab1-start` (your C14 Lab 3 dispatcher simulator and scenarios, plus the scenario schema, the SQL Server snapshot container with a reset script, and the mock APIs). New relative to C14: per-episode DB reset and end-state diff, four persona families incl. adversarial, simulator-fault attribution, CIs and the reliable-set share.
- **Steps:**
  1. Implement `UserSimulator`, a separate `IChatClient` (a different model family from the agent's) with a persona prompt containing the goal, known facts and hidden facts, the rule "reveal hidden facts only when asked", and a `###STOP###` termination token.
  2. Implement `Episode.RunAsync`: reset the DB, then loop between simulator and agent until stop, max turns or budget. Record the trace and compute the end-state diff:
     ```csharp
     var before = await Db.SnapshotAsync(scenario.Fixture);
     var transcript = await Episode.RunAsync(agent, simulator, scenario, budget, ct);
     var diff = await Db.DiffAsync(before);
     var verdict = Graders.EndState(diff, scenario.ExpectedEndState)
                 & Graders.Policy(transcript.ToolCalls, scenario.PolicyRefs)       // code checks
                 & await Judges.Conversation(transcript, scenario.ConversationChecks); // calibrated judges
     ```
  3. Author 40 scenarios across 4 personas and 8 intents, including Bulgarian and code-switched dispatcher scenarios and 6 adversarial "skip approval" scenarios.
  4. Run 4 trials per scenario. Report pass@1, pass^4, the reliable-set share (≥ 0.95 success) and the per-intent breakdown, all with Wilson CIs.
  5. Audit every failing episode and label it agent fault, simulator fault or scenario bug. Fix the simulator and scenario bugs, and report the simulator fault rate.
- **Break it:** Make the simulator "helpful", so it volunteers hidden facts in the first message. Observe the inflated pass rate on information-gathering scenarios, then restore it and add a simulator-fidelity check (hidden facts may not appear before the agent asks).
- **Acceptance criteria:**
  - `TrakiaSim` runs in CI on the 40-scenario suite (nightly, uncached, budget-capped).
  - The report contains pass@1, pass^4, CIs and failure attribution.
  - The simulator fault rate is ≤ 5% after fixes.
  - The 6 adversarial scenarios have 0 approval bypasses.
- **Stretch:** Add a τ²-style dual-control scenario in which the driver must perform a step (confirm the odometer reading) that the agent cannot do itself.

### Lab 2 — Scenario library, flakiness and a statistically sound regression gate (≈3h)

- **Goal:** Turn the suite into a library with coverage, and a gate that catches real regressions without crying wolf.
- **Start state:** tag `d7/lab2-start`.
- **Steps:**
  1. Define the taxonomy (intent, complexity, language, data condition, role, adversarial, modality) and generate a coverage matrix report. Add 30 scenarios from last month's production failure clusters (C14 error-analysis exports) and 20 from synthetic tuples, reviewed by hand.
  2. Run 8 trials per scenario on the current version. Classify each scenario as reliable, flaky or broken, and investigate the top 5 flaky ones.
  3. Make a prompt change (the Fleet Assistant v3.2, "more concise confirmations"). Compare it with v3.1 on the same scenarios and trials: a paired per-scenario analysis plus McNemar on first-trial outcomes, with primary metrics pre-registered in `gate.yaml`.
  4. Implement the gate:
     - fail if the paired lower 95% bound of the success delta is < −2 points on the primary set;
     - fail on any safety-set violation;
     - **warn** (not fail) on secondary metrics, with a Holm correction.
  5. Write a sample-size note: how many scenarios × trials are needed to detect a 3-point drop on this suite.
- **Break it:** Gate on a single cached trial of 50 scenarios, re-run the identical version 10 times uncached, and count the false alarms. Compare with your gate.
- **Acceptance criteria:**
  - `gate.yaml` and the gate implementation are committed.
  - The false-alarm rate is ≤ 1 in 10 identical-version runs.
  - The seeded real regression (the instructor provides a v3.2b that drops the depot parameter in 10% of bookings) is caught.
  - The flaky-scenario investigation finds at least one real agent defect, or documents why none exists.
- **Stretch:** Add sequential testing, stopping early when the evidence is conclusive, to cut trial costs. Report the savings.

### Lab 3 — Chaos for tools and models (≈3h)

- **Goal:** Prove graceful degradation under realistic faults, including a model swap and a retirement.
- **Start state:** tag `d7/lab3-start` (`ChaosChatClient`, `ChaosToolDecorator` and the APIM fault policy fragments, all disabled).
- **Steps:**
  1. Write steady-state hypotheses for 3 intents (booking, analyst query, incident triage).
  2. Run the experiments in TrakiaSim, one fault class at a time, at 5%, 20% and 50% intensity:
     - tool 5xx;
     - tool latency ×10;
     - malformed JSON;
     - 429 with `Retry-After` at the gateway;
     - injected instructions in tool output;
     - a stale fixture.
  3. **Model-swap drill:** point `Models:Assistant` at a different version or model through config, run the regression set (paired), and decide go/no-go with the Lab 2 gate.
  4. **Retirement drill:** the mock backend returns `410 Gone` for the primary deployment. Verify failover to the configured successor and the alert, and write the runbook step.
  5. Fix at least two weaknesses found. Typical ones: the model was retrying tools itself (move the retries into code); fabricated values after a malformed result (strengthen validation and the error message).
- **Break it:** Remove idempotency keys from the booking tool (D2) and rerun the latency fault. Count the duplicate bookings, then restore the keys.
- **Acceptance criteria:**
  - `ChaosSuite` passes: each steady-state hypothesis holds at 20% intensity.
  - There are 0 duplicate side effects.
  - There are 0 consequential actions from injected tool text.
  - The 410 drill fails over within the configured time and raises the alert.
  - The model-swap decision is documented with paired evidence.
- **Stretch:** Run a gateway-level chaos experiment in a staging environment with Azure Chaos Studio (network latency to the Foundry endpoint) while the load test from D5 runs.

### Lab 4 — SLOs, continuous evaluation and an AI incident postmortem (≈3h)

- **Goal:** Operate the agents against behavioural SLOs, detect a live incident, and learn from it.
- **Start state:** tag `d7/lab4-start` (staging environment with synthetic traffic generators).
- **Steps:**
  1. Define the SLIs and SLOs in `slo/slo.yaml` for the Fleet Assistant and the Fleet Analyst. Implement them as KQL over traces and judge events, and deploy multi-window burn-rate alerts via Bicep.
  2. Enable online evaluation. Either use **Foundry continuous evaluation** on the hosted agent, or a .NET sampler that scores a 5% random sample plus all targeted samples with calibrated judges. Apply the judge-error correction to the reported success SLI.
  3. Run a canary: 10% of traffic to the assistant prompt v3.2 via APIM weighted backends, and compare SLIs per intent.
  4. **Incident:** the instructor flips a hidden change (the provider deployment or the index alias switches to a version that drops a policy chapter). Detect it from the burn-rate alert, triage it with traces (optionally with Azure SRE Agent in Reader mode), and mitigate it (roll back the alias or route).
  5. Write the postmortem with the AI-specific sections (versions, failure class, "why evals didn't catch it"). Add the new scenarios and checks to TrakiaSim and prove they fail on the broken version and pass on the fixed one.
- **Break it:** Silence the uncached nightly run and repeat the incident. How long until detection? Quantify the value of the nightly run in hours of exposure.
- **Acceptance criteria:**
  - SLO alerts are deployed as code.
  - The incident is detected within the target window (≤ 1h at the staging traffic level).
  - The postmortem is merged with ≥ 2 new scenarios and ≥ 1 new check, all red on the broken version and green on the fixed one.
  - The canary analysis report is attached.
- **Stretch:** An error-budget policy. Write the rule for freezing prompt and model changes when the budget is exhausted, and automate it as a CI check reading the SLO status.

## Kata

**"Signal or noise?" (25 min, repeat 4×).** You get two eval reports (version A vs B) with per-scenario, per-trial outcomes:
- Variant 1: 50 scenarios × 1 trial, −4 points.
- Variant 2: 200 × 5, −1.5 points, concentrated in Bulgarian scenarios.
- Variant 3: +3 points on pass@1 but lower pass^4.
- Variant 4: a vendor blog claiming +12% on τ-bench.

For each, decide ship/hold/investigate and justify it with the right statistic: a CI, a paired test, a pass^k comparison, or the benchmark checklist. The instructor reveals the ground truth (simulated with known effects).

## Product increment — Fleet Ops Copilot

Fleet Ops Copilot is now operated as a reliable service:
- **TrakiaSim** covers the core agents with pass^k reporting.
- A versioned **scenario library** has a coverage matrix fed by production failures.
- A **statistical regression gate** with pre-registered primary metrics.
- A **chaos suite** covers tool, gateway and model faults, with retirement and model-swap drills.
- **Behavioural SLOs** with burn-rate alerts.
- **Continuous evaluation** with judge-error correction, and a canary process.
- A postmortem template whose outputs land as tests.

## Factory increment — your agentic SDLC

- Coding agents must run the smoke set (cached) and attach the `TrakiaSim` delta for any PR touching prompts, tools or agent definitions. A `Stop` hook or Copilot custom-agent rule enforces it.
- A **regression triage agent** (headless, D6 tooling) runs on every nightly failure. It clusters failing episodes, labels likely simulator faults vs agent faults for human confirmation, and opens issues with traces attached. It may *not* quarantine scenarios.
- Postmortem action items are created as issues tagged `eval-gap`. The cloud agent drafts the scenario YAML and the check, and humans review the expected end states.
- The error-budget policy is enforced in CI: prompt and model changes are blocked while the budget is exhausted, unless the PR is labelled as a reliability fix.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Simulation & scenarios | Single-turn Q&A evals | Multi-turn scripted tests | Simulator + end-state grading + library | Calibrated simulator with fault attribution; coverage matrix driven by risk and production failures; holdout set |
| Statistics | Point estimates | Averages over trials | CIs and pass^k | Paired tests, pre-registered gates, sample-size planning, judge-error correction, measured false-alarm rate |
| Chaos | None | Unit tests for tool errors | Fault injection in the loop | Hypothesis-driven experiments incl. model swap and retirement; fixes verified; no duplicate side effects |
| Operations | Dashboards | SLIs defined | SLOs + alerts + online evals | Error budgets with policy, canary analysis, drift detection, incident detected and mitigated within target |
| Learning from failure | Fixes the bug | Writes an incident note | Blameless postmortem | "Why evals missed it" answered; new scenarios/checks proven red→green; benchmark claims critiqued with the checklist |

**Auto-checked:** the nightly TrakiaSim run, the simulator fault-rate threshold, the gate false-alarm test (10 identical runs), detection of the seeded regression, `ChaosSuite`, the 410 drill, SLO alert deployment, postmortem scenarios red→green on the broken and fixed versions, and the error-budget CI check.

## Common pitfalls

- Gating on cached, single-trial, small-N suites and calling it reliability.
- Reporting only pass@1 for agents with side effects.
- Auto-quarantining flaky scenarios, which hides the real reliability defect.
- Trusting simulators without auditing simulator-caused failures.
- Grading exact tool-call sequences instead of end state plus policy checks, and so failing valid alternative paths.
- Retrying tools via the model instead of in code. Retrying side effects without idempotency.
- Treating judge scores as ground truth in SLIs.
- Paging platform on-call for behavioural SLO burns, or not paging anyone at all.
- Adopting features on vendor benchmark deltas without running them on your own simulator.
- Postmortems without new tests.


## References

- Yao et al., τ-bench (pass^k, simulated users, policy + DB end state): https://arxiv.org/abs/2406.12045 ; τ²-bench: https://arxiv.org/abs/2506.07982
- Jimenez et al., SWE-bench: https://arxiv.org/abs/2310.06770 ; SWE-bench Verified: https://openai.com/index/introducing-swe-bench-verified/
- Mialon et al., GAIA: https://arxiv.org/abs/2311.12983 · Terminal-Bench: https://www.tbench.ai · OSWorld: https://arxiv.org/abs/2404.07972
- FutureAGI, Best LLMs Sept 2026 (benchmark saturation, vendor-run scores; aggregator): https://futureagi.com/blog/best-llms-september-2026/
- Hamel Husain & Shreya Shankar, Evals FAQ (error analysis, judges, synthetic tuples, sampling): https://hamel.dev/blog/posts/evals-faq/
- Microsoft Learn — MEAI Evaluation libraries: https://learn.microsoft.com/en-us/dotnet/ai/evaluation/libraries
- Microsoft Learn — Foundry built-in evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators ; Reinhard, Foundry agent evaluations & continuous evaluation (practitioner): https://jannikreinhard.com/microsoft-foundry-agent-evaluations/
- Thinking Machines Lab — Defeating nondeterminism in LLM inference: https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
- Microsoft Learn — Foundry model retirements (`410 Gone`, notice periods): https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
- Microsoft Learn — APIM AI gateway (backend pools, circuit breaker): https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities
- Microsoft Learn — Azure SRE Agent FAQ: https://learn.microsoft.com/en-us/azure/sre-agent/faq
- Foundry blog — Memory at Build 2026 (≈5% claim) vs Agent Service at Build 2026 (7–14% claim): https://devblogs.microsoft.com/foundry/memory-build2026/ ; https://devblogs.microsoft.com/foundry/agent-service-build2026/
- Mem0 paper: https://arxiv.org/abs/2504.19413 ; Letta on memory benchmarking: https://www.letta.com/blog/benchmarking-ai-agent-memory
- Anthropic — Multi-agent research system (internal eval, rubric judging): https://www.anthropic.com/engineering/multi-agent-research-system
- EU AI Act Digital Omnibus timing: https://www.addleshawgoddard.com/en/insights/insights-briefings/2026/technology/eu-ai-act-ai-omnibus-formally-adopted/
