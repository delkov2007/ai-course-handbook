# C15 — Observability, GenAIOps & cost

> **Level:** 3 — Production systems (Advanced) · **Duration:** 14h (theory 30% / labs 70%) · **Prerequisites:** C9 (agent), C12 (incident workflow), C13 (context/caching), C14 (eval suite, CI gate) · **Volatility:** High (OTel GenAI conventions are "Development"; prices, model lifecycles, APIM/Foundry preview features change quarterly)

## Why this matters

Three weeks after Fleet Ops Copilot goes live at the Varna depot, finance asks why the Azure bill for "AI" doubled while incident volume rose 8%. Operations asks why the incident workflow sometimes takes four minutes. A dispatcher reports that "since Tuesday the customer notices sound different." Nobody can answer any of the three from data: the logs contain HTTP status codes and nothing about which agent, prompt version or model produced what; token usage exists only as a monthly invoice line; and Tuesday was the day the model router silently started favouring a different model in its pool.

LLM systems fail along dimensions classic APM does not see: *which* tokens were spent and why, which prompt and model version produced an answer, where in a multi-agent trajectory the time went, which tool is failing, what users thought, and what each outcome cost. Without that, every quality conversation is anecdotal and every cost conversation is a surprise. Worse, models are *retired on a schedule you do not control* — standard GA models on Foundry get about 18 months, several partner families 12 — so the system must be ready to change models as a routine operation, not a fire drill.

Experts instrument the whole trajectory with OpenTelemetry GenAI conventions (pinned, because the spec is still moving), keep message content out of production telemetry by default, turn traces into unit-economics dashboards (cost per incident, per depot, per shift), close the loop from user feedback into error analysis, version every prompt and agent like code with canaries and rollbacks, and treat model migrations and cost optimisation as measured, eval-gated releases. This module builds that operating layer for Fleet Ops Copilot.

## Learning outcomes

1. **Instrument** a MAF multi-agent workflow, MEAI clients and the C# MCP server with OpenTelemetry so one incident yields one connected trace (`invoke_workflow` → `invoke_agent` → `chat` → `execute_tool` → MCP server → SQL).
2. **Apply** the OTel GenAI semantic conventions with a pinned version, and **handle** attribute renames (e.g., `gen_ai.system` → `gen_ai.provider.name`) with Collector-side mapping.
3. **Configure** privacy-safe telemetry: content capture off in production, redaction, retention, DPIA notes.
4. **Build** dashboards and alerts for TTFT, latency, tokens (input/output/cached/reasoning), cost per task, tool error rate, budget escalations and HITL metrics in Application Insights/Azure Monitor and the Aspire dashboard.
5. **Implement** a user-feedback loop joined to traces that feeds the C14 error-analysis queue.
6. **Operate** a GenAIOps lifecycle: versioned prompts/agents/models, offline gates, feature-flag and gateway canaries, rollback.
7. **Plan and rehearse** a model migration under Foundry's deprecation policy (≥ 60 days' notice, PTU not auto-upgraded).
8. **Reduce** cost per task with evidence using caching, routing (Foundry model router or cascades), batch, gateway quotas and PTU-vs-PAYG analysis — without regressing evals.
9. **Produce** FinOps chargeback/showback dashboards with unit economics.

## Concepts

### 1. What LLM observability must answer

| Question | Signal |
|---|---|
| Why did this incident get this outcome? | distributed trace with agent/tool spans, prompt & model versions |
| Where does time go? | span durations, TTFT, HITL wait time |
| What does it cost, per what? | token usage by type × versioned price table → cost per task/tenant/feature |
| Is quality drifting? | online eval scores, feedback rate, approval/edit rates |
| Is anything failing silently? | tool error rate, retrieval-empty rate, budget escalations, judge Fail spikes |
| Who did what (audit)? | approver identity, agent identity, version attributes |

Misconception to unlearn: "logging the prompt and response is observability." It is the least useful and most dangerous part (PII, cost); structure, versions and token accounting matter more.

### 2. OpenTelemetry GenAI semantic conventions — status and shape

- **Status:** all `gen_ai.*` spans, metrics, attributes and events are at **"Development"** stability; only generic attributes such as `error.type`, `server.address`, `server.port` are stable. Names can change without a deprecation window. In **v1.42.0 (12 June 2026)** the GenAI conventions (including MCP) moved from the main repo to **`open-telemetry/semantic-conventions-genai`** (schema `gen-ai/1.42.0`; that repo had no tagged release as of mid-July 2026). Transition to stability is expected to use dual emission via `OTEL_SEMCONV_STABILITY_OPT_IN`; no date announced.
- **Operations / span names:** `create_agent`, `invoke_agent` (`{operation} {agent.name}`; split into client and internal spans in v1.41.0), `invoke_workflow {workflow.name}`, `execute_tool {tool.name}`, `plan`, `retrieval`, memory operations (`create_memory`, `search_memory`, `upsert_memory`); model calls `{operation} {request.model}`, e.g. `chat <model>`. Typical tree: `invoke_agent` → `chat` → `execute_tool`.
- **Attributes:** required `gen_ai.operation.name`, `gen_ai.provider.name`; recommended/conditional `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.response.finish_reasons`, `gen_ai.conversation.id`, `error.type`; agent/tool `gen_ai.agent.name|id|version`, `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.type`, `gen_ai.workflow.name`; usage `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.usage.cache_read.input_tokens`, `gen_ai.usage.reasoning.output_tokens`.
- **Renames/removals to expect:** `gen_ai.system` → `gen_ai.provider.name`; `prompt_tokens`/`completion_tokens` → `input_tokens`/`output_tokens`; `gen_ai.prompt`/`gen_ai.completion` **removed** (not renamed).
- **Content** is opt-in: `gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages`, carried on the `gen_ai.client.inference.operation.details` event; switches vary by library (e.g., `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`; MEAI's `EnableSensitiveData`).
- **Metrics:** `gen_ai.client.token.usage` (histogram by `gen_ai.token.type`), `gen_ai.client.operation.duration`; streaming (Apr 2026) `gen_ai.client.operation.time_to_first_chunk`, `time_per_output_chunk`; server-side `gen_ai.server.request.duration`, `gen_ai.server.time_to_first_token`, `gen_ai.server.time_per_output_token`.
- **MCP:** 2026-07-28 propagates W3C trace context in `_meta` (`traceparent`, `tracestate`, `baggage`) and recommends OpenTelemetry instead of protocol Logging; MCP tool calls emit the same `execute_tool` shape.

**Operating rule:** pin the semconv version your dashboards, alerts and C14 trajectory assertions read; normalise attributes in an OpenTelemetry Collector `transform` processor (e.g., copy `gen_ai.system` to `gen_ai.provider.name` for older emitters); review on every instrumentation upgrade.

### 3. Instrumenting the .NET stack

- **MEAI:** `ChatClientBuilder(...).UseOpenTelemetry(...)` emits GenAI spans and metrics for every `IChatClient`; `UseLogging` for structured logs.
- **MAF:** OpenTelemetry-based observability for agents and workflows (spans, metrics, events); verify ActivitySource/Meter names in your pinned version.
- **Aspire 13.x:** `ServiceDefaults` wires OTLP; the dashboard shows GenAI calls with a "sparkles" marker — your local trace viewer.
- **Azure Monitor / Application Insights:** Azure Monitor OpenTelemetry Distro (`UseAzureMonitor()`); span attributes land in `customDimensions` (classic) / `Properties` (workspace tables) — verify mapping for your workspace.
- **Foundry tracing:** model calls, tool invocations, sub-agent hops and handoffs flow through one OpenTelemetry pipeline in the **Foundry Control Plane**, with evaluations linked to traces; "tracing and evaluations for any agent framework" was public preview at Build 2026. Per a practitioner source, Foundry tracing/monitoring/evaluations reached GA in March 2026 — verify per feature. Foundry continuous evaluation and agent monitoring require App Insights.

```csharp
builder.AddServiceDefaults();                                    // Aspire: OTLP exporter, resource attrs
builder.Services.AddOpenTelemetry()
    .WithTracing(t => t.AddSource("Trakia.FleetOps.*")
                       .AddSource("Microsoft.Extensions.AI*")   // verify source names
                       .AddSource("Microsoft.Agents.AI*"))      // verify source names
    .WithMetrics(m => m.AddMeter("Trakia.FleetOps")
                       .AddMeter("Microsoft.Extensions.AI*"))   // verify meter names
    .UseAzureMonitor();                                          // Azure.Monitor.OpenTelemetry.AspNetCore

IChatClient chat = new ChatClientBuilder(foundryClient)
    .UseOpenTelemetry(sourceName: "Trakia.FleetOps.Llm",
                      configure: o => o.EnableSensitiveData = env.IsDevelopment())  // content OFF in prod
    .UseFunctionInvocation()
    .Build();

// Business correlation: what finance and dispatch care about
Activity.Current?.SetTag("trakia.incident.id", ticket.IncidentId);
Activity.Current?.SetTag("trakia.depot", ticket.Depot);            // chargeback dimension
Activity.Current?.SetTag("trakia.prompt.id", "notifier@v7#3f9c2a"); // name@version#hash
```

**Sampling:** agent traces are long and valuable; head-based 1% sampling destroys exactly the rare failures you need. Use tail sampling at the Collector: keep 100% of traces with errors, budget escalations, negative feedback or Fail judgements, plus a random share (e.g., 10%) of the rest; keep metrics unsampled.

**Privacy (EU/GDPR):** content capture off by default in production; if needed for a debugging window, enable with redaction (driver names, phone numbers, plates mapped to pseudonyms) in a Collector processor, separate retention for content (e.g., 14 days vs 90 for spans), access restricted, and documented in the DPIA (C18).

### 4. Metrics that matter for Fleet Ops

| Metric | Definition | Initial SLO / budget |
|---|---|---|
| TTFT (chat) | `time_to_first_chunk` p95 | ≤ 2.5 s |
| Incident workflow latency | `invoke_workflow` duration excl. HITL wait, p95 | ≤ 90 s |
| HITL wait | time from `RequestInfoEvent` to decision, p50/p95 | p95 ≤ 2 h (Severity ≥ High) |
| Tokens per incident | input / cached input / output / reasoning | trend; regression alert +15% |
| Cost per incident | Σ tokens × price-table version | ≤ €0.25 (example target) |
| Tool error rate | `execute_tool` spans with `error.type` / total, per tool | ≤ 1% |
| Budget escalations | runs ending in `EscalationRequired` | ≤ 2% |
| Approval rate & edit rate | approvals without change; notices edited before send | watch > 97% (automation bias, C18) |
| Retrieval empty rate | retrieval spans with 0 results above threshold | ≤ 3% |
| Online judge Fail rate | C14 judges on sampled traffic, corrected for TPR/TNR | per failure mode |
| Feedback | thumbs-down rate, reason codes | trend |

**Per-token price is not per-task cost** — a model with a lower token price can cost more per task if it uses more tokens (reasoning, retries, longer answers). Always report cost per *task*.

### 5. User feedback loops

Explicit feedback (thumbs + reason code: wrong facts / wrong vehicle / policy wrong / tone / too slow) and implicit signals (customer notice edited before sending, approval rejected, question re-asked within 2 minutes, escalation) are recorded as events carrying `gen_ai.conversation.id`, trace ID, incident ID, prompt/agent versions. Pipeline: feedback → join with trace → **error-analysis queue** (C14 viewer, prioritised) → taxonomy update → evaluator or fix → CI gate. Feedback rates are biased (angry users click more); never use them as prevalence estimates — use them to *find* traces.

### 6. GenAIOps lifecycle

Versioned artifacts (all in git): prompts and instruction files, tool schemas, agent definitions (MAF declarative YAML or code), workflow topology, judge prompts, eval datasets and labels, model deployment config, price table. The Baseline Foundry chat reference architecture adds three requirements: **agents-as-code via CI/CD**, **immutable agent versions**, and **regression suites** because behaviour is nondeterministic.

Promotion path:
1. PR → offline gate (C14, cached) → merge.
2. Deploy new version **dark** (shadow traffic or 0% flag).
3. **Canary**: Azure App Configuration feature flags (percentage/targeting, variant flags for prompt versions — verify variant API in your `Microsoft.FeatureManagement` version) or **APIM weighted backend pools** for model versions; 5–10% of a depot.
4. Compare online metrics per version (`gen_ai.agent.version`, `trakia.prompt.id`): judge Fail rates, feedback, cost/task, latency.
5. Promote or roll back by **config only** (no redeploy).
6. Nightly uncached eval run detects provider-side drift.

### 7. Model lifecycle and deprecation policy

Foundry model retirements (from the Learn page; re-verify each quarter):
- **Standard GA models: at least 18 months** — deprecated at 12, retired at 18.
- **Anthropic, DeepSeek, Fireworks and Mistral models: 12 months**; some Grok models: 6.
- **Preview models: about 90 days.**
- **Retirement notice ≥ 60 days**; retirement dates cannot be extended.
- **Retired models return `410 Gone`.**
- **PTU deployments are not auto-upgraded** — you must migrate them yourself.

**Model router** (`2025-11-18`, "Active (latest)", auto-updated; `2025-08-07` and `2025-05-19` frozen) routes per prompt across a pool in **Balanced (default) / Quality / Cost** modes; a **custom model subset** also serves as the failover set; effective context window = the **smallest** model in the pool; Global Standard and Data Zone Standard. An auto-updating router is convenient for cost but changes behaviour without your release — for regulated or customer-facing paths, either pin a frozen version or treat router updates as model migrations with online monitoring per routed model (`gen_ai.response.model`).

Migration as a routine: lifecycle watcher (scheduled job reading model lifecycle status; verify API) → issue at ≥ 120 days before retirement (same window as the instructor watch, D1 and A5) → C14 migration A/B → canary → promote → decommission old deployment. Keep model *roles* in config (C0), never model names in code.

### 8. Cost engineering basics

Order of levers (biggest first, measured per task):
1. **Don't call a model** — deterministic code for rules (C12).
2. **Shrink context** — budgets, compaction, rerank to top-k (C13).
3. **Cache** — provider prompt caching (static-first layout; Opus 5.5 cache reads $0.20 vs $4/MTok base input; Azure OpenAI prefix caching — verify threshold/discount); **semantic caching** at APIM (`llm-semantic-cache-store/lookup`, needs Azure Managed Redis or RediSearch-compatible cache) **only** for answers that are not user-, vehicle- or time-specific (policy FAQs) — cross-user leakage and staleness risks otherwise.
4. **Route** — small models for triage/judging/summaries; cascade (cheap first, escalate on low confidence); or Foundry model router in Cost mode with a custom subset.
5. **Batch** — offline jobs (nightly incident-history summarisation, eval runs) via Batch at ~50% discount (Anthropic documents −50%; Azure Batch discount/turnaround target — verify for your models).
6. **Capacity model** — PAYG (Global/Data Zone Standard) vs **PTU**: PTU buys predictable throughput/latency at a fixed hourly cost; break-even depends on sustained utilisation. Compute from your observed TPM distribution: PAYG_month = Σ(tokens × price); PTU_month = units × hourly rate × 730; choose PTU for the steady base load, PAYG overflow for peaks (APIM priority pools). Verify PTU minimums and prices before modelling.

Worked example (prices from the course price table; frontier tiers as reported by an aggregator in Oct 2026 — verify before use): GPT-6 "Sol" $2/$10 per MTok in/out, "Luna" $0.10/$0.50. Incident: triage (Luna, 2k/0.3k) ≈ $0.0004; diagnostics (Sol, 15k/1.5k) ≈ $0.045; policy (Sol, 10k/0.8k) ≈ $0.028; planner ×2 (Sol, 8k/1k each) ≈ $0.052; notifier (Sol, 6k/0.6k) ≈ $0.018; judge (Luna, 3k/0.1k) ≈ $0.0004 → **≈ $0.14 per incident**. Running everything on the "Astra" tier ($10/$50) would be ~5× more. Caching the static 40% of diagnostics/policy input and routing the planner's first pass to Luna are the next levers — validate each with the C14 gate.

**APIM AI gateway** (policies GA): `llm-token-limit` (TPM or token quotas per counter key — per depot subscription, per tenant in A-track), `llm-emit-token-metric` (token metrics with custom dimensions such as depot, feature, user → chargeback), backend pools (round-robin, weighted, priority, session-aware) with **PTU first, PAYG overflow** and a circuit breaker that honours `Retry-After`, `llm-content-safety-policy`. Unified OpenAI-compatible model API and "AI gateway in Microsoft Foundry" are **preview**.

### 9. FinOps dashboards

- **Showback/chargeback** per depot (Plovdiv, Sofia, Varna), feature (incident workflow, assistant chat, analyst SQL), and later tenant (A-track).
- **Unit economics:** € per incident, per dispatcher-shift, per 1,000 chat turns; trend vs volume.
- **Reconciliation:** telemetry-estimated cost vs Azure Cost Management actuals monthly; the gap (unmetered calls, eval runs, retries, embeddings, search units) is itself a finding.
- **Alerts:** cost/task +20% week-over-week, token quota at 80%, anomaly on a single conversation (runaway loop).
- Eval and red-team runs are real cost — tag them (`trakia.workload=eval`) and budget them separately.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| OTel GenAI semantic conventions (`semantic-conventions-genai`, schema gen-ai/1.42.0) | span/metric/attribute names | **Development** | Pin; dual emission via `OTEL_SEMCONV_STABILITY_OPT_IN` later |
| OpenTelemetry .NET SDK + OTLP exporter | instrumentation | GA | — |
| `Microsoft.Extensions.AI` `UseOpenTelemetry` | GenAI spans/metrics for `IChatClient` | GA (10.x) | `EnableSensitiveData` off in prod |
| MAF observability | agent/workflow spans | GA in 1.0 (Foundry observability integration was preview at 1.0) | Verify source names |
| OpenTelemetry Collector (contrib) | tail sampling, `transform`, redaction | GA | Attribute normalisation |
| Aspire 13.6 dashboard | local traces/metrics, GenAI marker | GA | Dashboard persistence features in Oct 2026 posts |
| Azure Monitor OpenTelemetry Distro / Application Insights | production telemetry, KQL, workbooks, alerts | GA | Workbooks as IaC |
| Foundry tracing, monitoring, continuous evaluation | traces + evals in Control Plane | GA (Mar 2026, practitioner source); any-framework tracing **preview** at Build 2026 | Needs App Insights |
| Azure App Configuration + `Microsoft.FeatureManagement` | feature flags, canaries, prompt variants | GA (variant API — verify) | Config-only rollback |
| APIM AI gateway policies | token limits/metrics, semantic cache, pools, circuit breaker | GA; unified model API & AI gateway in Foundry **preview** | Semantic cache needs Azure Managed Redis |
| Foundry model router `2025-11-18` | per-prompt routing (Balanced/Quality/Cost) | Available, auto-updating | Smallest-model context limit |
| Azure Cost Management | actual cost, budgets | GA | Reconcile monthly |

## Labs

### Lab 1 — One incident, one trace (≈2.5h)
- **Goal:** End-to-end, privacy-safe tracing across workflow, agents, MCP server and database.
- **Start state:** tag `c15/lab1-start` — C12 workflow, C8 MCP server (C# SDK 2.0), Aspire AppHost, OTel Collector container with a stub config.
- **Steps:**
  1. Instrument API, workflow host, agents (MAF + MEAI `UseOpenTelemetry`), MCP server and `SqlClient`; add business tags (`trakia.incident.id`, `trakia.depot`, `trakia.prompt.id`, `gen_ai.agent.version`).
  2. Propagate context to the MCP server via `_meta.traceparent` (verify how the C# SDK 2.0 surfaces `_meta` on client/server; add a small client filter/server handler if needed). Confirm MCP server spans are children of the agent's `execute_tool` span.
  3. Pin semconv: record the schema URL/version in `docs/observability/semconv.md`; add a Collector `transform` rule that maps `gen_ai.system` → `gen_ai.provider.name` (the PyRIT/Python harness from C14 still emits the old name).
  4. Collector: tail sampling (keep errors, `EscalationRequired`, negative feedback, judge Fail; 10% of the rest); redaction processor for plates/names/phones in any content attributes; content capture disabled in the `Production` profile.
  5. View in Aspire; then export to Application Insights.
- **Break it:** Remove propagation in the MCP client; observe orphaned MCP spans and a broken trajectory assertion from C14. Then turn on content capture in `Production` config and make the privacy test fail.
- **Acceptance criteria:** integration test with an in-memory exporter asserts: a single trace ID spans API → `invoke_workflow` → ≥ 4 `invoke_agent` → `chat` → `execute_tool` → MCP server → SQL; required GenAI attributes present on every model span; zero orphan spans across 20 incidents; `Production` config test asserts no `gen_ai.input.messages`/`output.messages` attributes or events.
- **Stretch:** Emit `retrieval` and memory-operation spans from the C13 knowledge-base and memory code following the conventions.

### Lab 2 — Dashboards, alerts and the feedback loop (≈2.5h)
- **Goal:** Turn traces into operational and quality signals that close the loop to C14.
- **Start state:** tag `c15/lab2-start` — App Insights workspace with 3 days of simulator traffic; `infra/monitoring/` Bicep skeleton.
- **Steps:**
  1. KQL for cost per incident (verify attribute-to-column mapping in your workspace):
     ```kusto
     let Price = datatable(model:string, inUsd:real, cachedUsd:real, outUsd:real)
       [ "luna-deploy", 0.10, 0.01, 0.50, "sol-deploy", 2.0, 0.20, 10.0 ];   // from price-table v3 (illustrative)
     dependencies
     | where timestamp > ago(7d) and tostring(customDimensions["gen_ai.operation.name"]) == "chat"
     | extend model = tostring(customDimensions["gen_ai.response.model"]),
              inTok = toint(customDimensions["gen_ai.usage.input_tokens"]),
              cached = toint(customDimensions["gen_ai.usage.cache_read.input_tokens"]),
              outTok = toint(customDimensions["gen_ai.usage.output_tokens"]),
              incident = tostring(customDimensions["trakia.incident.id"]),
              depot = tostring(customDimensions["trakia.depot"])
     | lookup Price on model
     | extend usd = (inTok - coalesce(cached,0)) * inUsd / 1e6 + coalesce(cached,0) * cachedUsd / 1e6 + outTok * outUsd / 1e6
     | summarize incidentUsd = sum(usd) by incident, depot
     | summarize p50 = percentile(incidentUsd, 50), p95 = percentile(incidentUsd, 95), total = sum(incidentUsd) by depot
     ```
  2. Workbook (as code) with tiles: TTFT p50/p95, workflow latency excl. HITL, tokens by agent and type, cost/incident by depot, tool error rate per tool, budget escalations, HITL wait and approval/edit rates, cache-read share.
  3. Alerts (Bicep): tool error rate > 1% for 15 min; cost/incident p95 +20% WoW; any single trace > €1; HITL wait p95 > 2h.
  4. Feedback API: `POST /feedback {traceId, conversationId, verdict, reasonCode, comment}` → custom event + span event; implicit signals from the notice editor (diff size) and approval rejections.
  5. Queue job: negative feedback and judge-Fail traces → C14 trace viewer queue with priority.
- **Break it:** Inject a tool that fails 5% of calls (parts API timeout); confirm the alert fires and the failing traces appear in the queue.
- **Acceptance criteria:** workbook and alerts deployed from `infra/monitoring` via CI; KQL cost per incident matches the offline calculation from exported usage within ±5%; the injected failure triggers the alert within 20 min of simulated traffic; ≥ 95% of feedback events join to a trace.
- **Stretch:** Show the same KPIs in the Foundry Monitor tab for a hosted-agent wrapper and compare numbers.

### Lab 3 — Versioning, canary and a model-retirement drill (≈2.5h)
- **Goal:** Ship a prompt change and a model migration as safe, reversible releases.
- **Start state:** tag `c15/lab3-start` — notifier prompt v7 in production; candidate v8; instructor "retirement notice" for the deployment behind the planner role (60 days).
- **Steps:**
  1. Prompt registry: `prompts/registry.json` maps `notifier` → versions with SHA-256 of the rendered template; a CI check fails if a prompt file changes without a version bump. Emit `trakia.prompt.id` and `gen_ai.agent.version` on spans.
  2. Feature flag in Azure App Configuration: variant `notifier-prompt` = v7 (90%) / v8 (10%), targeted to the Sofia depot; resolved per incident so a run uses one variant consistently.
     ```csharp
     // shape only — verify variant API in your Microsoft.FeatureManagement version
     var variant = await featureManager.GetVariantAsync("notifier-prompt", targetingContext, ct);
     var prompt  = promptRegistry.Get("notifier", variant?.Configuration.Get<string>() ?? "v7");
     ```
  3. Compare v7 vs v8 online for 2 simulated days: judge Fail rates (corrected), edit rate, cost/incident, latency. Decide; promote or roll back via config only.
  4. Model-retirement drill: run the C14 migration A/B for the planner role (current vs candidate deployment); configure APIM weighted backend (90/10) for the planner's model endpoint; watch per-`gen_ai.response.model` metrics; promote; record the runbook.
  5. Lifecycle watcher: scheduled GitHub Actions job that lists your deployments' models and their deprecation/retirement dates (verify the Foundry/Azure OpenAI API you use) and opens an issue when any pinned model retires in < 120 days, or a PTU deployment references a model with a retirement date.
- **Break it:** Point a deployment config at a "retired" model (instructor mock returns `410 Gone`); verify the gateway fails over to the configured backup pool and an alert fires instead of user-facing errors.
- **Acceptance criteria:** rollback from v8 to v7 in < 5 minutes with no deployment; migration runbook `docs/runbooks/model-migration.md` executed end-to-end with eval evidence attached; lifecycle watcher opens an issue for the mocked retirement; `410` path covered by an integration test.
- **Stretch:** Add the Foundry model router (custom subset = current + candidate, Cost mode) for the chat assistant behind a flag; monitor which model serves which share of turns.

### Lab 4 — Cost engineering and FinOps (≈2.5h)
- **Goal:** Cut cost per incident by ≥ 40% without quality regression, and give finance a chargeback view.
- **Start state:** tag `c15/lab4-start` — baseline cost/incident from Lab 2; APIM instance in front of two Foundry deployments (priority 1 "PTU-simulated", priority 2 PAYG).
- **Steps:**
  1. Baseline: cost/incident, tokens by agent, cache-read share.
  2. Apply levers one at a time, each followed by the C14 gate: (a) static-first prompt layout and sorted tools (C13); (b) triage + judge + summaries on the fast small model; (c) planner cascade — small model first, escalate when the deterministic `ProposalGuard` rejects; (d) nightly incident-history summarisation and GraphRAG refresh moved to Batch; (e) context budget tightening from C13 Lab 1.
  3. APIM: `llm-token-limit` per depot subscription (monthly quota + TPM), `llm-emit-token-metric` with dimensions `depot`, `feature`; semantic cache **only** on the policy-FAQ route (cache key excludes vehicle/user data), measure hit rate; priority pool with circuit breaker; Azure Load Testing to force 429s on priority 1 and observe overflow.
  4. PTU vs PAYG sheet from the observed TPM distribution (p50/p95 per hour); recommend base-load PTU size or stay PAYG.
  5. Chargeback workbook by depot and feature; reconcile with Cost Management for the lab subscription.
- **Break it:** Enable semantic cache on the vehicle-status route; demonstrate a stale/cross-user answer (TRK-0471 status served for TRK-0417) and remove it — document why in ADR-0015.
- **Acceptance criteria:** cost/incident ≥ 40% lower than baseline; no C14 failure mode regresses > 2 pp (McNemar not significant at 0.05); per-lever contribution table; overflow observed under load with zero user-facing 429s; ADR-0015 "Cost architecture" with PTU/PAYG decision and semantic-cache scope.
- **Stretch:** Model the A-track scenario: three external fleet tenants with per-tenant quotas and noisy-neighbour protection.

## Kata

**"Five-minute incident review" (20–30 min, repeated).** You receive an alert (e.g., "cost/incident p95 +35% since 11:00", "tool error rate 4% on parts_check_availability", "TTFT p95 doubled for Bulgarian chats", "thumbs-down spike on customer notices"). Using only the dashboards, KQL and traces: identify the cause, the first bad version/model/time, the blast radius (depots, incidents), and the remediation (rollback flag, failover, quota, fix). Write a 5-line postmortem. Variations rotate the root cause: router behaviour change (`gen_ai.response.model` shift), prompt variant, compaction bug (cache-read share collapse), MCP server deploy, provider latency, a runaway loop.

## Product increment — Fleet Ops Copilot

Fleet Ops Copilot now has **full OTel tracing** across workflow, agents, MCP server and SQL with pinned GenAI conventions and production-safe content handling; **dashboards and alerts** for latency/TTFT, tokens, **cost per incident** by depot, tool errors, HITL and quality signals; a **feedback loop** into C14 error analysis; **versioned prompts, agents and models** with feature-flag and gateway canaries and config-only rollback; a rehearsed **model-migration** runbook and lifecycle watcher; and a measured **cost architecture** (caching, routing, batch, APIM quotas/metrics, PTU/PAYG analysis) with chargeback per depot. These operational artifacts are inputs to **Gate G3** (see G3), C17 deployment and the C19 SRE loop.

## Factory increment — your agentic SDLC

- **Prompt/model registry automated:** CI computes prompt hashes, enforces version bumps, regenerates `prompts/registry.json`, and blocks merges where a prompt changed without an eval run attached.
- **Lifecycle bot:** the scheduled lifecycle watcher opens a migration issue with the template (candidate model, eval A/B checklist, canary plan); a cloud coding agent (Copilot cloud agent or Claude Code in Actions) picks it up, drafts the config change and runs the C14 migration suite, and leaves promotion to a human.
- **Telemetry as agent context:** coding agents get read-only access to traces/metrics (e.g., Azure MCP Server monitor tools with a Reader identity) to debug from evidence; a skill `investigate-trace` teaches the KQL patterns from Lab 2.
- **Cost guard in CI:** the golden-set run reports tokens and € per incident; PRs that raise cost/incident > 10% require an explicit `cost-approved` label from a human.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Tracing | Logs only | Model calls traced | One connected trace incl. MCP + SQL; pinned semconv; privacy-safe config tested | Collector normalisation and tail sampling designed for failure discovery; trajectory evals read spans reliably |
| Metrics & dashboards | Monthly bill | Token and latency charts | Cost/task by depot, tool errors, HITL, alerts as code | SLOs with error budgets; reconciliation with actual cost; actionable runbooks |
| Feedback loop | None | Thumbs captured | Joined to traces, queued into error analysis | Implicit signals; bias-aware use; measurable reduction of top failure modes |
| GenAIOps | Manual edits in portal | Prompts in git | Versioned prompts/agents, canary, config-only rollback | Migration drill with eval evidence; lifecycle automation; router updates treated as migrations |
| Cost engineering | Picks cheapest model | Applies caching | ≥ 40% reduction with eval gate and per-lever attribution | PTU/PAYG and semantic-cache scope decisions with risk analysis; chargeback adopted |

**Auto-checked:** trace-connectivity and privacy integration tests; required GenAI attributes; workbook/alerts deployed via CI; KQL vs offline cost within ±5%; rollback < 5 min script; lifecycle watcher issue on mocked retirement; `410` failover test; cost reduction ≥ 40% with C14 gate green.

## Common pitfalls

- Logging full prompts/responses in production "for debugging" — GDPR exposure and cost.
- Treating GenAI semconv as stable; dashboards silently break on attribute renames.
- Head sampling at 1% — the interesting failures disappear.
- Reporting tokens per call instead of cost per task; ignoring cached and reasoning tokens.
- No version attributes on spans — impossible to attribute a regression to a prompt or model.
- Letting an auto-updating model router change customer-facing behaviour without monitoring per routed model.
- Discovering a model retirement from a `410` in production; forgetting PTU is not auto-upgraded.
- Semantic caching personalised or time-sensitive answers.
- Optimising cost without re-running evals (quality regressions disguised as savings).
- Eval and red-team spend mixed into product cost — distorted unit economics.


## References

- Dash0 — OpenTelemetry GenAI semantic conventions explained (updated Sep 2026): https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained
- DEV Community (Azena AI) — GenAI semconv not stable yet; what shipped in 2026: https://dev.to/azena-ai/opentelemetrys-genai-semantic-conventions-are-not-stable-yet-heres-what-actually-shipped-in-2026-3mke
- Greptime — OpenTelemetry GenAI semantic conventions (May 2026): https://www.greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions
- MCP 2026-07-28 changelog (trace context in `_meta`): https://modelcontextprotocol.io/specification/2026-07-28/changelog
- .NET AI essentials (MEAI `UseOpenTelemetry`, Aspire GenAI marker): https://devblogs.microsoft.com/dotnet/dotnet-ai-essentials-the-core-building-blocks-explained/
- Aspire blog: https://devblogs.microsoft.com/aspire/
- Foundry Agent Service at Build 2026 (Control Plane OTel pipeline; any-framework tracing **preview**): https://devblogs.microsoft.com/foundry/agent-service-build2026/
- J. Reinhard — Foundry observability / evaluations (practitioner): https://jannikreinhard.com/microsoft-foundry-observability/ · https://jannikreinhard.com/microsoft-foundry-agent-evaluations/
- Foundry model retirements: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
- Foundry model router: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-router
- APIM AI gateway capabilities (`llm-token-limit`, `llm-emit-token-metric`, semantic cache, pools; unified API **preview**): https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities
- Baseline Microsoft Foundry chat reference architecture (agents-as-code, immutable versions): https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
- GenAIOps for organisations with MLOps investments: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/genaiops-for-mlops
- Claude Opus 5.5 overview (cache and batch pricing): https://platform.claude.com/docs/en/models/opus-5-5/overview
- Digital Applied — per-task vs per-token cost example: https://www.digitalapplied.com/blog/ai-model-releases-september-2026-tracker
- FutureAGI — model landscape and prices (aggregator, verify): https://futureagi.com/blog/best-llms-september-2026/
