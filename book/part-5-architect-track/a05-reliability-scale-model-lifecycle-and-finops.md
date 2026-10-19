# A5 — Reliability, scale, model lifecycle & FinOps

> **Level:** Expert — AI Solution Architect track · **Duration:** 16h (theory 30% / labs 70%) · **Prerequisites:** A1 (cost model), A2 (landing zone), A4 (AI gateway); C14 (eval gates), C15 (OTel, cost per task) · **Volatility:** High (model lifecycle durations, deployment types, PTU terms, prices and router versions change; reliability principles do not)

## Why this matters

**What separates an expert architect from a proficient one here:** a proficient architect makes an AI system highly available *today*. An expert designs for the fact that **the system's most important dependency has an expiry date**. Every GA model is retired on a published schedule, and the replacement behaves differently. The expert turns that into a routine, eval-gated, budgeted process. They also define reliability in terms users feel (latency to first token, task success, grounded answers) and run the economics per task and per tenant, so the business knows whether every new customer makes or loses money.

Here is what happens to a team that hasn't built these skills. Fleet Ops Copilot runs well for nine months. Then:

- A retirement notice arrives with the minimum 60 days' warning for the primary model. The prompts, judges and the Bulgarian groundedness calibration were all tuned to that model.
- A Standard deployment set to auto-upgrade quietly moves to a new version, and the incident workflow's tool-call accuracy drops 6 points. Nobody notices for two weeks, because the CI evals use cached responses.
- A Sweden Central capacity event turns into a full outage. Foundry Agent Service has **no built-in DR**, and nobody ever rebuilt the agents from code.
- A large SaaS tenant onboards and doubles TPM at 08:00 on Mondays. The PTU reservation was sized on an average and saturates.
- The CFO asks what Danube Logistics costs to serve, and the answer is a shrug.

Experts handle each of these in advance:

- **Model churn:** they keep a model register with retirement dates and treat migration as a release with pairwise eval gates and a canary.
- **Silent drift:** they run an *uncached* nightly suite that catches provider-side drift.
- **Disasters:** they design DR by reconstruction and rehearse it.
- **Capacity:** they size capacity from load distributions, not averages.
- **Overload:** they build a degradation ladder so that overload degrades the experience instead of failing it.
- **Economics:** they publish unit economics (cost per task, per tenant, per truck) and hold cost to an SLO, just like latency.

## Learning outcomes

1. **Build and operate** a model lifecycle register: lifecycle states, retirement dates, upgrade policies and owner, refreshed automatically from the Models API.
2. **Execute** a model migration with pairwise eval gates, per-failure-mode pass rates, cost and latency deltas, an APIM weighted canary and a tested rollback.
3. **Design and rehearse** multi-region DR for an AI workload without native DR: agents-as-code reconstruction, index rebuild RTO, state RPO, gateway failover, all within EU residency constraints.
4. **Plan capacity** from measured TPM distributions: quotas, PTU vs PAYG vs Batch break-even, spillover sizing and reasoning-token effects. **Validate** with load tests.
5. **Implement** a graceful degradation ladder with circuit breakers, feature flags and tenant-tier load shedding.
6. **Define** SLOs for AI (availability, TTFT, task success, quality, safety, cost per task) with error budgets and burn-rate alerts.
7. **Implement** FinOps unit economics and per-tenant showback/chargeback. **Derive** a SaaS price floor and margin.
8. **Run** a GameDay and write a postmortem that drives architecture changes.

## Concepts

### 1. Model lifecycle: policy facts you design around

From Foundry's model retirement policy (updated Jul 2026):

- **Standard GA models:** minimum **18-month** lifetime. Deprecated at 12 months, retired at 18.
- **Anthropic, DeepSeek, Fireworks and Mistral GA models:** **12 months**. Some Grok models: 6 months. **Preview models:** about **90 days**.
- **Notice:** at least **60 days** before GA retirement. **Retirement dates cannot be extended.** Retired models return **`410 Gone`**.
- **Auto-upgrade:** controlled by `versionUpgradeOption`. **Provisioned (PTU) deployments are not auto-upgraded.** PTU is stable until you act, and then you face a hard date.
- **Lifecycle API:** state can be read from the Models API, but **terminology conflicts**: API "Deprecated" means *retired*. Map states explicitly in your tooling.

Related volatility:

- **Model router.** Version `2025-11-18` is "Active (latest)" and **auto-updates**. Versions `2025-08-07` and `2025-05-19` are frozen. The router's pool and behaviour can change under you unless you pin a frozen version. Its effective context window is that of the smallest model in the pool.
- **Content Safety API versions.** A new GA version deprecates the previous GA after 90 days (if compatible).
- **Embedding models.** A change means a full re-embed (A3 aliases).

**Architecture consequences:**

1. **Indirection.**
   - Code addresses *roles* (`fleet-reasoning`, `fleet-fast`, `fleet-embed`, `judge-bg`) through `IChatClient` and the gateway.
   - Deployment names map to roles in configuration.
   - A migration is a config change plus evals, never a code hunt.
2. **A register with dates.** Each role records model, version, deployment type, region, upgrade policy, lifecycle state, deprecation/retirement dates, owner and the eval suite that gates it.
3. **Calendar.** With 12–18-month lifetimes and several roles, expect a migration every quarter somewhere. Budget it (A1 ops family).
4. **Judges migrate too.** Your C14 judges are calibrated to a model. A judge model change requires re-measuring TPR/TNR on the labelled dev/test splits before the judge gates anything.
5. **Choose upgrade policy deliberately.**
   - *Auto-upgrade* trades surprise for less toil. Acceptable only with an uncached nightly suite and alerting on `gen_ai.response.model` changes.
   - *Pinned* trades toil for control.
   - PTU is effectively pinned.

### 2. Model migration as a release

The **migration pipeline**:

1. **Shadow.** Replay a frozen evaluation set plus a sample of recent production traces (content-captured only where the DPIA allows) against old and new models.
2. **Pairwise judging** (new vs old, position-randomised).
3. **Per-failure-mode pass rates.** Use the C14 taxonomy, not just the aggregate. A model can improve overall while regressing on "Bulgarian table questions".
4. **Trajectory evals for agents.** Tool-call accuracy, steps, pass^k.
5. **Safety.** Red-team ASR re-run.
6. **Cost and latency deltas.** Tokens per task change with the model; reasoning-token behaviour especially.
7. **Prompt re-tune loop** if needed, then re-run.
8. **Canary** via APIM **weighted** backend (5% → 25% → 100%), with online evaluation (Foundry continuous evaluation or MEAI scores published to telemetry) and the success metrics from A1.
9. **Rollback rule** defined before starting. It works only while the old deployment exists, which is why you migrate early, not at day 59.

**Gate criteria example:**
- no failure mode regresses > 2 points;
- pairwise win-or-tie ≥ 55%;
- ASR not worse;
- cost per task ≤ +15%;
- p95 TTFT ≤ +10%.

The nightly **uncached** suite (C14) catches provider-side drift between migrations. The PR suite stays cached for determinism and cost.

### 3. Multi-region, failover and DR without native DR

What the baseline reference architecture states:

- **Standard deployments are single-region.** Use **Data Zone provisioned with spillover** or global deployments for model availability.
- **Foundry has no native load balancing or circuit breaking**, so APIM fills that role.
- **Agent Service has no built-in DR.** Recover by **reconstruction**: agents-as-code, backups, delete locks.
- **Multi-region is out of scope.**

You design the rest. Classify the **state** first, because DR is about state:

| State | Where | Recoverability | Typical RPO / RTO target for Trakia |
|---|---|---|---|
| Agent definitions, prompts, tool schemas, guardrail config | Git + IaC | Rebuild by pipeline | RPO 0 / RTO ≤ 1h (measured) |
| Model deployments | IaC; needs **quota in DR region** | Rebuild; quota is the risk | Pre-provisioned in secondary |
| Knowledge indexes | AI Search | Rebuild from sources (hours at scale) **or** maintain warm secondary index | Rebuild time is often the RTO driver: measure it |
| Conversations / standard-setup state | Cosmos DB | Backup/geo-replication (verify current Cosmos backup modes) | RPO ≤ 15 min for active incidents; history may tolerate 24h |
| In-flight workflows and pending HITL approvals | MAF checkpoints / Durable Task Scheduler | Must survive; this is the most business-critical state | RPO ≈ 0 for approvals; replay design |
| Memory stores | Foundry memory (preview) / files | Verify export and backup capability | Often acceptable to lose; decide explicitly |
| Telemetry, evals, audit logs | Log Analytics / Storage | Audit logs need immutability and retention (A6) | Per policy |

**Topologies:**

- **Active-passive.** The secondary EU region has gateway, quota and a warm index. Failover is by APIM backend priority, or by front-door routing for the app tier. This is the default for Trakia internal.
- **Active-active per stamp.** Tenants are pinned to a home region, so failover moves whole stamps. This is the SaaS default, because it keeps tenant data placement explicit.
- **Residency constrains pairing.** For EU customers, the failover region must also be EU (e.g., Sweden Central ↔ another EU region). Verify that your models, Data Zone types, safety features and the red-team regions exist there.
- **APIM availability and multi-region capabilities depend on tier.** Verify current tier features before designing gateway DR.

**The runbook is the deliverable.** It covers detection, decision authority, steps, verification (smoke evals through the failed-over path) and failback. A DR plan that has not been rehearsed is a hypothesis.

### 4. Quotas, PTU and capacity planning

- **Quotas** are TPM/RPM per model, per deployment type, per region and subscription. Request quotas for DR regions *before* you need them.
- **Deployment types:**
  - **PAYG** (Global / Data Zone / Regional Standard): elastic, priced per token.
  - **PTU** (Provisioned): reserved throughput, predictable latency, not auto-upgraded.
  - **Batch**: about 50% cheaper with a ~24h target (verify current Azure terms).

  The reference architecture's rule is **PAYG for variable load, PTU for a stable baseline**, implemented as PTU-first priority pools with PAYG spillover (A4).
- **Sizing from distributions.** Export per-minute token usage by role from gateway metrics, then build business-hours histograms. A practical course heuristic (not a vendor rule): size PTU near the sustained p50–p70 of peak-hours load and let spillover take the bursts. The break-even point depends on the PTU price and throughput per PTU *for that model*. Use the current Foundry capacity calculator and pricing; numbers are not reproduced here.
- **Reasoning effort is a capacity knob.** Reasoning tokens are billed and consume the context budget and throughput. Raising effort from low to high can multiply TPM for the same traffic. Every model and effort change triggers a capacity recalculation.
- **Batch moves offline work off the hot path:**
  - contextual chunk generation (A3);
  - nightly uncached eval suites;
  - monthly SaaS analytics reports;
  - re-labelling assistance.
- **Load testing AI workloads:**
  - Use realistic conversation scripts with think time and a mix of task types: Q&A, analyst, incident workflow (≈15× tokens).
  - Measure TTFT and end-to-end time, 429 rate, spillover share, the token cost of the test itself, and quality under load (run a sampled eval during the test, because degraded modes change answers).

### 5. Graceful degradation

Design a **degradation ladder** per capability. Each step is triggered by circuit-breaker state, quota exhaustion, latency SLO burn or a manual switch (feature flags in Azure App Configuration):

1. **Full experience.** Frontier reasoning model, agentic retrieval, tools.
2. **Cheaper or faster model role** for non-critical tasks. Planning effort lowered (`minimal` / extractive retrieval).
3. **Retrieval-only "search mode"**: cited passages without generation. It is still useful for mechanics.
4. **Cached or static answers** for FAQs, plus a "queue for later" for analyst queries (Batch).
5. **Human handoff.** The incident workflow falls back to the manual dispatcher procedure, with the event queue preserved.

**Load shedding by tenant tier.** Premium tenants keep step 1 longest. Internal non-critical agents shed first.

**Always disclose degraded mode to users.** It is a trust issue, and in the EU a transparency expectation.

**Never degrade safety.** Guardrails, permission trimming and HITL are not on the ladder.

### 6. SLOs for AI systems

| SLI | Source | Example SLO (Fleet Assistant, business hours) |
|---|---|---|
| Availability (successful responses / valid requests) | Gateway + app | 99.5% monthly |
| TTFT p95 | OTel `gen_ai.client.operation.time_to_first_chunk` (semconv "Development"; pin version) | ≤ 2.5 s |
| Task success (agents) | Workflow outcome events / state checks | Incident triage completed without human rework ≥ 85% |
| Quality | Sampled online evaluation: BG-calibrated groundedness judge pass rate | ≥ 92% rolling 7 days |
| Safety | Weekly red-team ASR; guardrail block anomalies | ASR ≤ 2% |
| Cost | Cost per task P50/P95 from token metrics × price table | P50 ≤ €0.04 per Q&A |

**Error budgets:**
- Availability budget at 99.5% ≈ 3.6 h/month.
- Quality budget (8% failing samples) is spent by model drift, index staleness or prompt changes.

**Burn-rate alerts** (fast and slow windows) on availability and quality. When the quality budget is exhausted, feature work pauses for error analysis, just as reliability work does.

**Quality SLIs come from sampling, so state the sample size and confidence.** 200 samples/week gives roughly ±4 points at 90% pass rate (95% CI). Small tenants may need longer windows.

### 7. FinOps for AI

- **Unit economics.**
  - Cost per **task** (not per token): every model call, tool backend, retrieval, judge sampling and allocated fixed cost.
  - Aggregated per **tenant** and per **truck** (the SaaS pricing unit).
  - **Gross margin** = price per truck − variable cost per truck − allocated platform cost.
- **Showback/chargeback.**
  - Token metrics from `llm-emit-token-metric` with tenant/agent/product dimensions (A4).
  - Resource tags (`tenant`, `stamp`, `ai-system-id`) for fixed costs.
  - An allocation rule for shared costs (e.g., by token share, or by trucks).
  - Monthly showback per internal department; chargeback or margin reports per SaaS tenant.
- **Controls:**
  - per-tenant monthly quotas (`llm-token-limit`);
  - budgets and anomaly alerts;
  - a **cost regression gate** in CI (A1 factory increment);
  - prompt layout for cache hits (static first);
  - model right-sizing per role;
  - Batch for offline work;
  - cap the tools agents can call. The baseline notes that agents call tools unnecessarily.
- **Know where the money goes.** For Trakia internal, the fixed platform (Cosmos DB, AI Search, DDoS Protection per the baseline) plus people dominate. For SaaS at scale, the Fleet Analyst and incident workflows' tokens can dominate variable cost. Your showback must make both visible.

**Misconception to unlearn: "cheaper model = cheaper task".** Per-task cost depends on tokens used, retries and escalations. Measure cost per *successful* task.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| Foundry model retirements policy + Models API lifecycle status | Lifecycle register | GA policy (updated 2026-07-24) | API "Deprecated" = retired; map explicitly |
| Model router `2025-11-18` (auto-updating), `2025-08-07`/`2025-05-19` (frozen) | Routing; lifecycle risk | Active / frozen | Pin frozen version for stability-critical paths |
| APIM backend pools (weighted, priority), circuit breaker, `llm-emit-token-metric`, `llm-token-limit` | Canary, failover, showback, quotas | GA | From A4 |
| Azure App Configuration feature flags | Degradation ladder switches | GA | |
| Azure Load Testing (+ k6/NBomber scripts) | Capacity validation | GA | Budget the token cost of tests |
| `Microsoft.Extensions.AI.Evaluation` (+ `.Reporting`, `dotnet aieval`) | Pairwise and per-failure-mode gates | GA (verify versions) | Cached for PR, uncached nightly |
| Foundry continuous evaluation | Online quality SLI | Evaluations/monitoring GA Mar 2026 per practitioner source; some evaluators preview | Requires App Insights |
| OTel GenAI semantic conventions | SLIs (TTFT, tokens) | **Development** (moved to `semantic-conventions-genai` at v1.42.0) | Pin; Collector-side mapping |
| Azure Monitor / Log Analytics workbooks, KQL | SLO dashboards, showback | GA | |
| Azure Cost Management + budgets, exports | FinOps | GA | Tag discipline required |
| Durable Task Scheduler / MAF checkpoints | In-flight state recovery | DTS GA (verify); MAF Durable extension prerelease | |
| Azure Chaos Studio | Fault injection for GameDay | GA (verify fault coverage for AI services) | Fallback: gateway policy fault injection |

## Labs

### Lab 1 — Lifecycle register and an eval-gated model migration (≈4h)

- **Goal:** Migrate the Fleet Assistant's `fleet-reasoning` role to a newer model with evidence, a canary and a tested rollback.
- **Start state:** branch `a5/start`. Contains the A4 gateway, the C14 frozen suite (incl. Bulgarian strata and adversarial cases), `model-register.yaml` (empty), and **your C15 Lab 3 artefacts**: the lifecycle-watcher Actions job, `docs/runbooks/model-migration.md` and the C17 Lab 5 `release/canary-criteria.yaml`.
- **This lab extends, not re-teaches, the C15 model-retirement drill.** C15 rehearsed one role (A/B, 90/10 weighted backend, runbook, `410` failover). Here you turn that rehearsal into a fleet-wide, register-driven, multi-stage process. Do not rebuild what already passes; re-run the C15 runbook first (≤ 15 min) and record what it is missing for a SaaS estate.
- **Steps:**
  1. Promote the C15 lifecycle-watcher job into `lifecycle-watch`, a .NET worker. Keep its < 120-day rule and add what C15 lacked: every deployed model (not just pinned roles), explicit state mapping (API "Deprecated" → retired), `model-register.yaml` filled with deprecation and retirement dates, and an issue on any state change.
  2. Deploy the candidate model under a new deployment and register it as `fleet-reasoning-next`.
  3. Extend the C15 runbook's A/B into the full migration pipeline (new steps beyond C15 are shadow replay, pass^4, ASR and A1 cost deltas):
     - shadow replay of the frozen set plus 300 sampled traces (synthetic or consented);
     - pairwise judge;
     - per-failure-mode pass rates;
     - trajectory evals on the incident workflow (pass^4);
     - ASR re-run;
     - cost and latency deltas from the A1 model.
     ```csharp
     // Pairwise gate sketch: verify evaluator APIs against current MEAI.Evaluation docs.
     var report = await MigrationGate.RunAsync(
         baseline: roles["fleet-reasoning"], candidate: roles["fleet-reasoning-next"],
         suite: FrozenSuite.Load("evals/frozen-v7"),
         gates: new() { MaxFailureModeRegression = 0.02, MinPairwiseWinOrTie = 0.55,
                        MaxCostPerTaskIncrease = 0.15, MaxP95TtftIncrease = 0.10 });
     report.ThrowIfFailed();
     ```
  4. If needed, re-tune the prompt in a branch and re-run. Re-validate the Bulgarian groundedness judge (TPR/TNR) if the judge model changes.
  5. Canary via the C15/C17 APIM weighted pool, extended from a single 90/10 stage to 5% → 25% → 100%, reusing `release/canary-criteria.yaml` and adding online eval sampling and A1 success metrics compared per arm. Update `docs/runbooks/model-migration.md` with the diff from the C15 version.
  6. Write `runbooks/model-migration.md` and the migration ADR.
- **Break it:** The instructor switches a Standard deployment's version underneath you (simulating auto-upgrade). The PR suite (cached) stays green. Your **nightly uncached suite** and a `gen_ai.response.model` change alert must catch it within one cycle.
- **Acceptance criteria:**
  - `lifecycle-watch` tests pass, including the state-mapping test.
  - The migration report is committed and all gates are evaluated.
  - The canary is recorded with per-arm metrics.
  - Rollback is executed and timed (< 10 min).
  - The silent upgrade is detected by the nightly job.
- **Stretch:** Plan the *embedding* model migration as well (A3 aliases) and the judge-model migration. Produce a 12-month migration calendar for all roles with effort estimates fed back into A1.

### Lab 2 — Multi-region DR by reconstruction and GameDay (≈4h)

- **Goal:** Prove you can lose the primary region and restore service within targets, inside the EU.
- **Start state:** `a5/lab2-start`. Contains the A2 landing-zone parameters for a secondary EU region and agents-as-code from C17/A4.
- **Steps:**
  1. Classify the state using the Concepts §3 table, set RPO/RTO per state, and get sign-off from the "business" (the instructor).
  2. Provision the secondary region:
     - gateway backends;
     - model deployments with **quota confirmed**;
     - a warm AI Search index fed by the same pipeline (or a measured rebuild path);
     - Cosmos DB replication/backup per your RPO (verify current modes);
     - Durable Task Scheduler/checkpoint store strategy for in-flight approvals.
  3. Script **reconstruction**: a pipeline that recreates Foundry projects, connections, agents and guardrails from code in the secondary region, and runs the smoke evals.
  4. Configure APIM failover (priority pools across regions) and the front-end routing.
  5. **GameDay.** The instructor "fails" the primary by blocking its private endpoints or disabling backends. Execute the runbook, measure the actual RTO/RPO, run smoke evals through the failed-over path, then fail back.
- **Break it:** During the GameDay an incident workflow is waiting on a human approval. After failover the approval must still be pending (not lost, not duplicated), and approving it must complete the booking exactly once.
- **Acceptance criteria:**
  - Measured RTO ≤ target for the Fleet Assistant (e.g., 1h) and the incident workflow.
  - The pending approval survives failover.
  - Smoke evals pass in the secondary region.
  - The runbook is updated with real timings.
  - The postmortem (blameless, with ≥ 3 architecture actions) is committed.
- **Stretch:** Measure a *cold* index rebuild at SaaS year-1 scale. Decide per tenant tier whether warm secondary indexes are worth their cost, using the A1 model.

### Lab 3 — Capacity plan, PTU break-even and load validation (≈3h)

- **Goal:** Size capacity from data and prove it under load.
- **Start state:** `a5/lab3-start`. Contains 4 weeks of gateway token metrics (synthetic SaaS growth included) and the Azure Load Testing scripts skeleton.
- **Steps:**
  1. KQL: per-minute TPM by role and tenant. Build business-hours percentiles (p50/p70/p95/max) and the Monday-08:00 peak.
     ```kusto
     customMetrics
     | where name == "Total Tokens" and customDimensions.namespace == "trakia-ai"
     | summarize tpm = sum(value) by bin(timestamp, 1m), role = tostring(customDimensions.role)
     | where hourofday(timestamp) between (6 .. 19)
     | summarize p50=percentile(tpm,50), p70=percentile(tpm,70), p95=percentile(tpm,95), peak=max(tpm) by role
     ```
  2. Model three options per role in `Trakia.CostModel`:
     - (a) PAYG only;
     - (b) PTU sized at p50/p70 + PAYG spillover;
     - (c) (b) plus Batch for offline workloads.

     Use current prices and PTU throughput for your model from the official calculator (record the source and date).
  3. Run the load test at projected year-1 SaaS peak with a realistic task mix. Measure 429s, spillover share, TTFT p95, cost per task and quality on a sampled eval during load.
  4. Write **ADR-A5-002 "Capacity strategy per model role"**.
- **Break it:** Raise reasoning effort on the incident workflow from low to high. Re-measure TPM and cost per task, and show the capacity plan breaking. Decide whether the quality gain (from the eval) is worth it, or whether effort should be `auto`/selective.
- **Acceptance criteria:**
  - The capacity model is reproducible from code with sourced prices.
  - The load test meets TTFT and error SLOs at the projected peak under the chosen option.
  - The ADR includes break-even analysis and triggers to revisit (e.g., sustained utilisation > 85%).
- **Stretch:** Add the model router in Cost mode for the Q&A role as a fourth option. Account for its auto-update risk and smallest-context-window constraint.

### Lab 4 — Degradation ladder and AI SLOs (≈2.5h)

- **Goal:** Overload and dependency failures degrade the experience predictably, and SLOs make quality visible.
- **Start state:** `a5/lab4-start`.
- **Steps:**
  1. Implement the ladder for the Fleet Assistant and the incident workflow: App Configuration flags plus automatic triggers (APIM breaker open, quota near exhaustion, TTFT burn). Implement the "search mode" response (citations only) and "queued for later" for analyst queries.
  2. Show the degraded-mode banner in the UI and Teams card. Log the mode on every span (`trakia.degradation.level`).
  3. Define SLOs (Concepts §6) in `slo.yaml`. Build the workbook and burn-rate alerts (1h/6h windows) for availability, TTFT and quality (sampled online eval).
  4. Inject faults: gateway policy returning 429/503 for 20% of calls, +3s latency on the knowledge MCP server, an AI Search outage (Chaos Studio where supported; otherwise gateway or app fault injection).
- **Break it:** During the latency fault, a well-meaning flag disables the guardrail "to save latency". Your policy test must fail the configuration change, because safety is not on the ladder.
- **Acceptance criteria:**
  - Each fault produces the expected ladder step within 2 minutes.
  - User-visible error rate stays ≤ SLO.
  - Burn-rate alerts fire for the injected quality regression (instructor swaps in a weak prompt).
  - The guardrail-disable change is rejected by CI.
- **Stretch:** Make shedding tenant-tier aware. Show premium tenants retain step 1 while standard tenants are on step 2 during a capacity event.

### Lab 5 — FinOps: unit economics and per-tenant showback (≈2.5h)

- **Goal:** Answer "what does each tenant cost and earn?" from data, monthly, automatically.
- **Start state:** `a5/lab5-start`. Contains gateway metrics with tenant dimensions, cost exports and the tag policy from A6 (preview).
- **Steps:**
  1. Join token metrics × price table (variable cost), plus tagged resource costs (stamp and tenant), plus an allocation of shared platform cost (rule documented). Compute cost per task (successful tasks only in the denominator), per tenant, per truck.
  2. Build the showback workbook with internal departments, SaaS tenants, trend, anomalies (a cost-per-task z-score) and top cost drivers (agent, tool, model role).
  3. Compute gross margin per SaaS tenant at the A1 price hypothesis. Derive the **price floor** per truck per isolation tier (pooled/bridge/silo from A3).
  4. Add budgets and anomaly alerts per tenant. Connect the monthly quota (A4) to the plan.
- **Break it:** One tenant's integration loops A2A calls overnight. The anomaly alert must fire before the monthly quota is consumed, and the showback must attribute the cost correctly.
- **Acceptance criteria:**
  - Unit-economics numbers reconcile with Cost Management totals (± 5%).
  - Every resource carries the required tags (policy compliance).
  - The margin report is generated by pipeline.
  - The anomaly is detected within 1 hour of onset.
- **Stretch:** Present a one-slide "cost to serve" story to the ARB "CFO": where margin comes from, which tier loses money, and which architectural lever fixes it.

## Kata

**"Retirement notice in your inbox"** (30 min, repeat).

You receive a simulated notice: model X retires in 75 days. In 30 minutes, produce:

- the affected roles and agents (from the register);
- the migration plan with dates working backwards from retirement, including canary and buffer;
- the evals to run, including judges that use the model;
- the capacity and cost implications (PTU not auto-upgraded? new token profile?);
- the stakeholder message.

Variations:
- a partner model with a 12-month lifecycle;
- a PTU deployment;
- an embedding model (re-index);
- the judge model;
- the model router's auto-update changing the pool;
- a preview model your SaaS feature depends on (~90 days).

## Product increment — Fleet Ops Copilot

The product is now **operable at scale**:

- model lifecycle register with automated watch, and a rehearsed migration pipeline with pairwise gates and canary;
- active-passive EU DR by reconstruction, with measured RTO/RPO and approvals that survive failover;
- a capacity plan per model role validated by load tests;
- a degradation ladder;
- AI SLOs with error budgets (availability, TTFT, quality, safety, cost);
- per-tenant unit economics with a price floor per isolation tier.

## Factory increment — your agentic SDLC

- **`lifecycle-watch`** opens issues automatically. A **migration agent** (custom Copilot/Claude Code agent) prepares the candidate deployment PR, runs the migration gate and drafts the report and ADR for human review. It never promotes past canary on its own.
- **Nightly uncached eval suite** plus the `gen_ai.response.model` drift alert. A **cost regression gate** and a **capacity recalculation** job run on any model, effort or prompt change.
- **Policy tests** prevent configuration changes that put safety controls on the degradation ladder.
- **GameDay as code:** fault-injection scripts and a smoke-eval verification step, runnable quarterly from the pipeline.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Model lifecycle & migration | Hard-coded model names | Config-based models | Register with dates and automated watch; pairwise, per-failure-mode gates; canary and timed rollback | Plus judge/embedding migrations planned, migration calendar costed, silent-upgrade detection proven |
| DR & failover | "Azure is redundant" | Backup of some data | State classified with RPO/RTO; reconstruction pipeline; GameDay with measured results and postmortem | Plus residency-aware pairing, in-flight approval continuity, tier-based warm/cold decisions priced |
| Capacity & degradation | Average-based sizing | Quotas requested | Distribution-based PTU/PAYG/Batch plan validated by load test; degradation ladder with triggers | Plus reasoning-effort impact quantified, tenant-tier shedding, safety excluded from ladder by policy |
| SLOs | Uptime only | Latency + availability | Quality, safety and cost SLOs with error budgets and burn-rate alerts | Plus sample-size/CI reasoning, quality budget policy that pauses feature work |
| FinOps | Monthly bill | Token totals | Cost per successful task, per tenant, per truck; showback; anomaly alerts | Plus margin and price floor per isolation tier, levers tied to architecture decisions |

**Auto-checked:**
- `lifecycle-watch` tests;
- migration gate report;
- rollback timing;
- nightly drift detection;
- GameDay smoke evals and RTO measurement;
- approval-continuity test;
- capacity model reproducibility;
- load-test thresholds;
- degradation trigger tests;
- policy rejection;
- burn-rate alert firing;
- cost reconciliation (± 5%);
- tag compliance.

## Common pitfalls

- Hard-coded model or deployment names, so migration becomes a code search.
- Migrating at day 59 of 60, with no time left for a canary or rollback.
- Gating migrations on aggregate scores only, hiding per-failure-mode (e.g., Bulgarian) regressions. Forgetting that judges also need migration.
- Cached CI evals only, so provider drift goes unnoticed.
- Assuming Foundry gives DR. Forgetting quota in the DR region. Losing pending HITL approvals on failover.
- Choosing a non-EU failover region for EU personal data.
- Sizing PTU on averages. Ignoring reasoning tokens.
- Degrading safety controls to meet latency.
- Cost per token instead of cost per successful task. Shared costs left unallocated, so SaaS margins look fictional.


## References

- Foundry model retirements (lifecycle durations, 60-day notice, 410 Gone, PTU not auto-upgraded): https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
- Model router concepts (versions, modes, failover subset): https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-router
- Baseline Microsoft Foundry chat RA (reliability, no built-in DR, PAYG vs PTU, cost drivers): https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
- APIM AI gateway (priority pools, circuit breaker with Retry-After, token metrics): https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities
- Multitenant AI/ML (noisy neighbours, per-resource limits): https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/ai-machine-learning
- MEAI Evaluation libraries (caching, reporting, online evaluation): https://learn.microsoft.com/en-us/dotnet/ai/evaluation/libraries
- Foundry agent evaluations and continuous evaluation (practitioner source): https://jannikreinhard.com/microsoft-foundry-agent-evaluations/
- OTel GenAI semconv status: https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained ; https://dev.to/azena-ai/opentelemetrys-genai-semantic-conventions-are-not-stable-yet-heres-what-actually-shipped-in-2026-3mke
- MAF HITL and checkpoints: https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop ; Durable extension: https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions
- Content Safety API deprecation policy and regions: https://learn.microsoft.com/en-gb/azure/ai-services/content-safety/overview
- Per-task vs per-token cost (aggregator, indicative): https://www.digitalapplied.com/blog/ai-model-releases-september-2026-tracker
- τ-bench / pass^k: https://arxiv.org/abs/2406.12045
