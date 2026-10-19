# D5 — Performance & cost engineering

> **Level:** Expert (AI Solution Developer track) · **Duration:** 14h (theory 25% / labs 75%) · **Prerequisites:** Core C0–C19 and Gate G3; especially C13 (context engineering), C14 (eval gates), C15 (tracing, cost per task), C17 (APIM AI gateway); D1 (small models, calibration) recommended · **Volatility:** High (prices, cache discounts, router versions, PTU sizing, batch terms)

## Why this matters

A proficient practitioner cuts tokens and switches to a cheaper model. An expert optimizes **cost per successful task under a latency SLO, with quality held constant by evals**, and can prove each claim:
- every optimization is a paired experiment (quality delta with confidence interval, cost delta, latency delta);
- the expert knows which optimizations silently trade quality or safety for money (semantic caching across users, routers with smaller context windows, aggressive truncation);
- they decompose latency to the stage that dominates;
- they model capacity with arithmetic before buying provisioned throughput;
- they load-test AI endpoints with realistic token distributions rather than "100 users saying hello".

By month six, Fleet Ops Copilot serves ~1,500 internal users and two pilot customer fleets. The monthly bill tripled after the D2 planner and the D3 voice assistant launched. Dispatchers complain about 6-second answers at 08:00, when every depot opens. Finance proposes "switch everything to the cheapest model". Platform proposes "buy PTUs". Both proposals are guesses.

The evidence points elsewhere:
- per-token price is not per-task cost (a cheaper-per-token model can cost more per task because it uses more tokens);
- reasoning tokens are billed and inflate time-to-first-token;
- prompt caching can cut cached input cost by roughly 95% for some providers (Claude Opus 5.5: $0.20 vs $4 per MTok);
- most latency is decode time for output you did not need.

This module turns those facts into an engineering method. C15 already introduced the levers (prompt and semantic caching, routing, batch, PTU vs PAYG, APIM pools) at concept level; D5 does not re-teach them. It adds the experimental discipline around them: CPST as the KPI, paired quality checks per optimization, thresholds tuned on labelled curves, and capacity arithmetic validated under realistic load.

## Learning outcomes

1. **Define and compute** cost per successful task (model + tools + infrastructure + human review ÷ eval-verified successes), and **use** it as the release KPI with quality and latency guardrails.
2. **Decompose** end-to-end latency into queueing, prefill/TTFT, decode, reasoning, tool and orchestration time from OTel traces, and **target** the dominant term.
3. **Design** prompts and tool catalogs for provider prompt caching (static-first layout, deterministic tool order), and **measure** the cache hit ratio and the savings.
4. **Implement** gateway semantic caching with correct partitioning and eligibility rules, and **quantify** its false-hit rate and leakage risk.
5. **Choose and tune** routing (Foundry model router modes, custom subsets) or a confidence-based cascade, setting thresholds from dev-set curves.
6. **Apply** batch processing, parallel tool execution and context-size reduction where each fits, with paired quality checks.
7. **Model** PTU vs PAYG economics from observed traffic distributions, including spillover, and **validate** the model with Azure Load Testing against the APIM gateway.

## Concepts

### 1. The KPI: cost per successful task

```
CPST = (Σ model token cost + Σ tool/API cost + infra (search, compute, gateway, cache) + human review cost)
       ÷ (# tasks judged successful by evals or by business outcome)
```

- **Success** must be defined per task type. For a policy question: a grounded, correct answer with valid citations (C14 judges). For a fault triage: the decision matched the mechanic outcome (D1). For a weekly plan: approved without edits, executed without compensation (D2).
- Optimizations that cut cost but also cut success can **raise** CPST. Retries, escalations and human review count.
- **Guardrails:** the quality floor (a paired eval delta whose lower 95% bound is ≥ −1 point) and the latency SLO (for example, the dispatcher P95 end-to-end time) are both non-negotiable. Optimize CPST *within* them.
- Report CPST per task type, per tenant and per model version. A single blended number hides cross-subsidies.

**Misconceptions to unlearn:**
- "Cheaper per token = cheaper." Token *usage* varies by model. A vendor's ~40% per-task saving claim is a vendor estimate, not a list price.
- "Latency is the model's problem." Orchestration, tools and output length usually dominate.
- "Caching is free money." Wrong-cache hits are quality incidents, and cross-user hits are data leaks.

### 2. Latency anatomy

For an agent run with *n* model calls:

```
E2E ≈ queue + Σᵢ [ TTFTᵢ + (reasoning_tokensᵢ + output_tokensᵢ) × ITLᵢ + toolsᵢ ] + orchestration overhead
TTFTᵢ ≈ network + prefill(input_tokensᵢ − cached_tokensᵢ) + provider queueing
```

- **Prefill** grows with *uncached* input tokens. **Decode** grows with output tokens, *including hidden reasoning tokens*. For most chat workloads, decode dominates. Halving output length helps more than halving input.
- **Reasoning effort** is the biggest single latency/cost dial on 2026 frontier models. Input, output and reasoning tokens share one context budget, and reasoning may be invisible (encrypted chain-of-thought exists).
- **Sequential tool rounds** multiply TTFT. Three rounds of "think → call → read" cost three TTFTs plus tool time.
- **Measure** with the OTel GenAI metrics (still "Development" status, so pin the semconv version):
  - `gen_ai.client.operation.duration`;
  - `gen_ai.client.operation.time_to_first_chunk` and `time_per_output_chunk` (streaming);
  - `gen_ai.client.token.usage` by token type;
  - `gen_ai.usage.cache_read.input_tokens` and `gen_ai.usage.reasoning.output_tokens` on spans.

Lever ranking for interactive agents (typical, verify on your traces):
1. cut output tokens and reasoning effort;
2. remove sequential rounds (parallel tools, pre-fetch);
3. cache the static prefix;
4. use smaller or faster models for sub-steps;
5. regional proximity and gateway overhead.

### 3. Designing for provider prompt caching

Providers cache the KV state of an **identical prefix**. Layout rules:
1. **Static first:** system instructions, tool schemas (in a **deterministic order**; the MCP 2026-07-28 spec says servers SHOULD return `tools/list` deterministically "to improve LLM prompt cache hit rates"), skills metadata, few-shot examples, and the stable corpus (if under the ~200k-token "skip RAG" threshold).
2. **Semi-static next:** tenant/depot context and user profile.
3. **Dynamic last:** retrieved chunks, the conversation tail, and the current question. **Never put timestamps, request IDs or random IDs at the top.**

Economics: for Claude Opus 5.5 a cache read costs $0.20/MTok against $4/MTok base input. Writes cost $5/MTok (5-minute TTL) or $8/MTok (1-hour TTL), and the minimum cacheable prompt is 512 tokens (write prices and minimum: verify against current documentation). A prefix pays off when expected reads × (base − read price) > write premium. Azure OpenAI caches repeated prefixes of ≥ 1,024 tokens at a discount. The discount level and model coverage are unverified for GPT-6-era deployments, so check the pricing page.

Measure `cache_read.input_tokens ÷ input_tokens` per route, and alert when a deploy drops it. That usually means someone added a dynamic field to the system prompt.

### 4. Semantic caching at the gateway

APIM's `llm-semantic-cache-lookup` / `llm-semantic-cache-store` embed the prompt and return a cached completion when vector proximity exceeds a threshold. They need Azure Managed Redis or another RediSearch-compatible cache.

**Eligibility rules:**
- **Cache only** answers that are identical for everyone in a partition and stable over the TTL. Policy FAQs ("What is the overtime rule for weekend loading?") qualify.
- **Never cache** user-specific, time-sensitive or tool-calling/agentic responses: driving hours, a truck's status, "my shipments".
- **Partition keys:** tenant, role (security trimming!), language, and corpus version. A cache shared across roles bypasses C7's permission trimming. That is a data leak.
- **TTL** aligned with document refresh, plus invalidation on corpus re-index (index alias swap → new partition key).
- **Threshold** tuned on a labelled set of paraphrase pairs and near-miss pairs ("overtime on weekends" vs "overtime on holidays"). Measure the false-hit rate and accept only thresholds where false hits are ≤ 0.5% on near-misses.
- **Poisoning:** never store responses that failed guardrails or judges. Store only after the online groundedness check passes.

### 5. Routing and cascades

**Foundry model router.**
- Version `2025-11-18` is "Active (latest)" and **auto-updated**; `2025-08-07` and `2025-05-19` are frozen.
- Modes are **Balanced** (default), **Quality** and **Cost**. A **custom model subset** restricts the pool and doubles as the failover set.
- The effective context window is **the smallest model's in the pool**.
- It runs on Global Standard and Data Zone Standard.

The routing pool can span OpenAI, Anthropic (Claude must be deployed separately), Grok, DeepSeek, Llama and others. Check the data-residency implications per model. An auto-updating router is a drift source, so pin a frozen version for regulated paths, or re-run evals on router updates.

**Your own cascade.** A cheap model, or the D1 distilled student, answers first. Escalate to the frontier model when a **calibrated** signal is below τ: the classifier probability, judge score, retrieval coverage, or a schema/validator failure.

```
E[cost] = c_small + P(escalate) × c_large
E[quality] = Q_small|accepted × (1 − P(esc)) + Q_large|escalated × P(esc)
```

Pick τ from the dev-set curve of (P(escalate), quality). Validate on test with paired comparisons against "always frontier".

**When to use which:**
- Use the router for heterogeneous open-ended chat where you cannot build a confidence signal.
- Use a cascade where you have a calibrated signal and a narrow task (triage, classification, extraction).
- Use static routing by task type (planner → frontier, summarizer → small) whenever the task type is known. It is the cheapest router of all.

### 6. Batch, parallelism and speculation

- **Batch API:** asynchronous bulk processing at a ~50% discount (Claude: input and output; Azure Batch deployments: about 50% cheaper with a 24h target, verify current terms). Use it for anything not user-blocking: nightly incident-report summarization, contextual-retrieval chunk enrichment (C13), embedding back-fills, eval runs and red-team sweeps. Design for partial failure and idempotent result ingestion.
- **Parallel tool calls:** when the model emits several independent calls in one turn, execute them concurrently (`Task.WhenAll`). Check that your function-invocation layer allows concurrent invocation (verify the MEAI `FunctionInvokingChatClient` option name), and that tools are thread-safe and rate-limit aware. Prompt the model to batch independent lookups ("call all needed tools in one step").
- **Pre-fetch (speculative tool execution):** when the next tool is near-certain (the driver's tachograph state at the start of a voice session), fetch it before the model asks. It costs some wasted reads and saves a full round.
- **Speculative decoding** (a draft model proposes tokens, the large model verifies) speeds decoding without changing the output distribution. It is a **serving-engine** feature (vLLM, self-hosted), not something you toggle on a managed API.
- **Hedged requests** (sending to two backends and taking the first) cut tail latency at up to 2× cost. Use them only on small, cheap, latency-critical calls.

### 7. Context-size reduction without quality loss

- Trim tool results at the source: pagination, field projection, `response_format: concise|detailed`, and summaries plus IDs instead of raw rows (C8 tool design).
- Clear tool results from history once they have been used. Compact long sessions (C13).
- Reduce the tool catalog per task (fewer tools means a shorter prefix and better selection). Foundry **tool search** (preview) and skills' progressive disclosure load definitions on demand.
- **Code execution as the tool interface:** filter data in a sandbox before it reaches the model. Anthropic's example went from ~150k to ~2k tokens.
- Cap output with explicit length instructions plus `max_output_tokens`, and handle `finish_reason=length` (C1).
- Every cut is a paired eval. Context reduction is where silent quality regressions hide (lost-in-the-middle helps you, but missing evidence hurts).

### 8. PTU vs PAYG: arithmetic before purchase

Notation:
- *P_ptu*: price per PTU-hour.
- *k*: input tokens/min one PTU sustains for *your* input/output mix and model (same unit as *T* below) (from the capacity calculator plus a benchmark; verify per model).
- *p_in*, *p_out*: PAYG prices.
- *r*: the output/input ratio.

```
PAYG cost per hour at throughput T (input tok/min) = 60 × T × (p_in + r × p_out)
PTU cost per hour for N units                          = N × P_ptu, serving up to N × k
Break-even utilisation u* = P_ptu ÷ [60 × k × (p_in + r × p_out)]
```

If your sustained utilisation of the provisioned capacity exceeds *u\**, PTU wins on cost. Below it, PAYG wins.

Real traffic is peaky (08:00 depot opening), so the expert design is:
- **PTU sized near the P60–P70 of the TPM distribution**;
- **PAYG spillover** for peaks via APIM **priority backend pools** (PTU priority 1, PAYG priority 2), with a circuit breaker that honours `Retry-After`.

Include in the model:
- PTU deployments are **not auto-upgraded**, so a model retirement means a planned migration with capacity overlap;
- Data Zone (EU) vs Global pricing for GDPR residency;
- the predictability benefit, which has real value for the CFO.

All prices are taken from the pricing pages on the day of the exercise. The course does not freeze them.

### 9. Load testing AI endpoints

- **Workload realism:**
  - sample prompt and response token-length *distributions* from production traces (C15);
  - mix task types in the observed ratios;
  - add think time;
  - drive streaming endpoints with clients that record TTFT and completion separately.
- **Little's law:** concurrency = throughput × latency. 30 req/s at 4 s mean latency means ~120 in-flight requests. Size connection pools, APIM limits and rate limits accordingly.
- **Separate concerns:**
  - **gateway/orchestration tests** against a mock LLM backend (cheap, run often);
  - **capacity tests** against real deployments (expensive, run rarely, budgeted);
  - **failover tests** that force 429s on the priority-1 pool.
- **Load tests cost money.** Estimate the token bill before running (requests × mean tokens × price) and cap it with a gateway quota on the test subscription key.
- Tools: **Azure Load Testing** (managed; JMeter, and Locust per recent docs, verify), k6 and NBomber (.NET). Report P50/P95/P99 TTFT and E2E, 429 rate, spillover share and € per 1,000 tasks.

### 10. Quotas and fairness

- `llm-token-limit` per tenant, per feature and per user (TPM and longer-period quotas, with pre-estimation of prompt tokens) prevents one tenant's batch from starving dispatchers.
- `llm-emit-token-metric` with tenant/feature dimensions feeds chargeback and CPST dashboards.
- Interactive traffic gets priority. Background agents (the D2 planner) get lower quotas and the batch path.

## Tools & versions (as of Oct 2026)

| Tool / feature | Purpose | Status | Notes |
|---|---|---|---|
| APIM AI gateway policies: `llm-token-limit`, `llm-emit-token-metric`, `llm-semantic-cache-lookup/store`, backend pools (priority/weighted), circuit breaker | Quotas, chargeback, semantic cache, spillover | GA (policies) | Semantic cache needs Azure Managed Redis or RediSearch-compatible |
| APIM unified model API; AI gateway in Foundry | Single endpoint across providers | **Preview** | |
| Foundry model router `2025-11-18` | Per-prompt routing; Balanced/Quality/Cost; custom subset | Active, auto-updating | Frozen: `2025-08-07`, `2025-05-19`; smallest-context constraint |
| Provider prompt caching | Prefix KV reuse | GA (per provider) | Opus 5.5 read $0.20 vs $4/MTok; Azure discount level: verify |
| Batch API / Batch deployments | ~50% discount, async | GA (per provider) | Verify Azure terms per model |
| Azure Load Testing | Managed load tests | GA | Verify Locust support; JMeter supported |
| NBomber / k6 | Code-first load testing | OSS | NBomber for .NET-native scenarios |
| OTel GenAI semconv (`gen_ai.client.*`, `gen_ai.usage.*`) | Latency/usage metrics | **Development** | Pin semconv version; map in Collector |
| MEAI `ChatClientBuilder` (+ caching, OTel) and MAF middleware | Client-side caching, budgets, metrics | GA | `IDistributedCache` response cache for exact repeats in tests |
| MEAI.Evaluation (+ response caching) | Paired quality checks for every optimization | GA | Nightly uncached run for drift |

## Labs

Lab repo: `trakia-fleetops`. The `perf/` folder holds the k6/NBomber scenarios, the `TraceSampler` that extracts token-length distributions from App Insights, and the `infra/apim` Bicep modules. Two Foundry deployments simulate "PTU" (priority 1, low quota) and "PAYG" (priority 2).

### Lab 1 — Latency and cost anatomy, and the CPST baseline (≈2.5h)

- **Goal:** Know where time and money go for the three main task types (policy Q&A, fleet analyst query, fault triage), and establish CPST.
- **Start state:** tag `d5/lab1-start` (the full product from C19 with tracing).
- **Steps:**
  1. Add the missing span attributes: `gen_ai.usage.cache_read.input_tokens`, `gen_ai.usage.reasoning.output_tokens`, tool durations, and a `task.type` attribute. Add a `CostEnricher` (an OTel processor) that computes € per span from a pinned price table in config.
  2. Join traces to eval outcomes, from the nightly eval run and online judges: `success = judge_pass ∧ no_human_override`.
  3. Build a KQL workbook with: the latency waterfall per task type (queue, TTFT, decode, reasoning, tools, overhead), the output-token share of latency, CPST per task type and tenant, and the cache hit ratio.
     ```kusto
     dependencies | where customDimensions["gen_ai.operation.name"] == "chat"
     | extend task = tostring(customDimensions["task.type"]), eur = todouble(customDimensions["cost.eur"])
     | summarize cost = sum(eur), p95_ttft = percentile(todouble(customDimensions["ttft_ms"]), 95) by task, bin(timestamp, 1h)
     ```
  4. Write `perf/baseline.md` with the top three latency contributors and the CPST per task type.
- **Break it:** Raise the fleet analyst's reasoning effort to high. Quantify the change in TTFT, cost and success. Is the quality gain worth it under the CPST definition?
- **Acceptance criteria:**
  - The workbook is deployed via Bicep.
  - A `CpstTests` integration test recomputes CPST from a fixture trace set within ±1%.
  - The baseline report names the dominant latency term per task type, with evidence.
- **Stretch:** Add human-review minutes (from the D3 delivery-note review queue) into CPST at a loaded hourly rate.

### Lab 2 — Prompt-cache layout and context diet (≈2.5h)

- **Goal:** Cut input cost and TTFT without losing quality.
- **Start state:** tag `d5/lab2-start`.
- **Steps:**
  1. Audit the prompts of the Fleet Assistant and the planner. Move the static parts first, remove the timestamp and request ID from the system prompt, and make the Trakia MCP server return tools in a deterministic (sorted) order.
  2. Trim tool outputs: `GetVehicleStatus` returns concise fields by default, and telematics queries paginate with a summary plus IDs. Clear consumed tool results from history.
  3. Cap output length per task type, and handle `finish_reason=length` with a "continue?" affordance.
  4. Run the golden suites before and after. Report paired quality deltas with 95% CIs, the cache hit ratio, TTFT P50/P95 and CPST.
- **Break it:** Insert `Current time: {DateTime.UtcNow:O}` at the top of the system prompt and watch the cache hit ratio collapse in the workbook. Add an alert rule for it.
- **Acceptance criteria:**
  - Cache hit ratio ≥ 70% on the assistant route.
  - Input cost per task −40% or better.
  - TTFT P95 improved.
  - Paired quality delta lower bound ≥ −1 point on every suite.
  - The cache-regression alert fires in the Break-it scenario.
- **Stretch:** Move rarely used instructions into skills (progressive disclosure) and measure prefix length vs skill-load frequency.

### Lab 3 — Semantic cache, router and cascade (≈3h)

- **Goal:** Serve repetitive questions from cache safely, and route each request to the cheapest model that meets quality.
- **Start state:** tag `d5/lab3-start` (APIM in front of the deployments, Azure Managed Redis provisioned).
- **Steps:**
  1. Enable `llm-semantic-cache-lookup/store` **only** on the `/policy-faq` route. Use a partition key of `tenant|role|lang|corpusVersion`, a TTL of 24h, and invalidation on index alias swap. Store only responses with `x-trakia-judge: pass` set by the backend.
  2. Build `SemanticCacheEval`: 200 paraphrase pairs (should hit) and 200 near-miss pairs (should not). Sweep the similarity threshold and choose the highest hit rate with false hits ≤ 0.5%.
  3. Deploy the **Foundry model router** with a custom subset (fast small model + workhorse + frontier, all EU-resident). Compare the Balanced, Quality and Cost modes on the policy and analyst suites, logging the `model` actually used per response.
  4. Build a **cascade** for fault triage: D1 student first, then escalation to frontier when `Confidence < τ` or the schema is invalid. Pick τ on dev and report test results.
  5. Produce a decision table: route by task type, router mode or cascade, with CPST, quality and P95 for each.
- **Break it:**
  - Remove `role` from the cache partition key and replay the HR-restricted question set as a dispatcher. Count the leaked answers, then restore the key and add `CacheLeakTests`.
  - Add a pool model with a much smaller context window to the router subset and observe failures on long analyst prompts.
- **Acceptance criteria:**
  - Semantic cache false-hit rate ≤ 0.5% on near-misses, with **0 cross-role hits** (`CacheLeakTests`).
  - The cascade's triage CPST is ≤ 30% of always-frontier, with a paired quality delta lower bound ≥ −1 point and `StopNow` recall ≥ 0.97.
  - The router-mode comparison is committed, including a pinning decision (frozen vs latest) with justification.
- **Stretch:** Implement the cascade as MEAI middleware (`EscalatingChatClient`) so any route can opt in by configuration.

### Lab 4 — Batch, capacity model and load test with spillover (≈2.5h)

- **Goal:** Move non-interactive work to batch, and decide PTU vs PAYG with arithmetic validated by a load test.
- **Start state:** tag `d5/lab4-start`.
- **Steps:**
  1. Move the nightly incident-report summarization (≈3,000 reports per night) to the Batch path. Make result ingestion idempotent by report ID and handle partial failures. Compare cost and wall time with the synchronous run.
  2. Using `TraceSampler`, extract the TPM distribution per 5-minute bucket for a week. Fill `perf/capacity-model.xlsx` (or a C# notebook) using today's prices, the PTU throughput per unit for your model and token mix (calculator plus benchmark), and the break-even utilisation u*. Size PTU at the P60–P70 TPM and compute the monthly cost of PAYG-only, PTU-only (sized for peak) and PTU+spillover.
  3. Configure APIM priority backend pools (simulated PTU deployment priority 1, PAYG priority 2) with a circuit breaker honouring `Retry-After`.
  4. Run an Azure Load Testing scenario that replays the sampled token distribution at a 08:00-peak profile against APIM. First set a test-key quota as a cost cap. Record the TTFT and E2E percentiles, the 429 rate, the spillover share and €/1,000 tasks.
- **Break it:** Remove the circuit breaker and repeat the run. Observe 429 storms and retry amplification. Then set the client retry policy to ignore `Retry-After` and measure the damage.
- **Acceptance criteria:**
  - The batch run is ≥ 45% cheaper with no lost reports (`BatchIngestionTests`).
  - The capacity model includes u*, the TPM percentiles and three scenarios, with the price sources and date cited.
  - The load test report shows the P95 E2E SLO met at peak with spillover, and the client-visible 429 rate below 0.5%.
  - The ADR `ADR-0D5-capacity.md` is committed.
- **Stretch:** Repeat the load test with the semantic cache and prompt caching on vs off, and attribute the latency gain to each.

## Kata

**"Find the euro" (30 min, repeat 4×).** You get one trace export (20 runs) and the current price table:
- Variant 1: a planner run.
- Variant 2: a voice session.
- Variant 3: an analyst query with 5 tool rounds.
- Variant 4: a RAG answer with a 60k-token context.

Within 30 minutes, produce:
1. the CPST and latency waterfall;
2. the top two optimizations with an estimated € and ms saving;
3. the quality risk of each and the paired eval you would run;
4. what you would *not* do, and why.

The instructor scores against the measured outcome of each optimization.

## Product increment — Fleet Ops Copilot

Fleet Ops Copilot now runs on a cost and performance baseline:
- Prompts and tool catalogs are cache-friendly, with a cache-regression alert.
- Semantic caching covers the policy FAQ route only, with tenant/role/language/version partitioning and a measured false-hit rate.
- Routing is per task type, combining a pinned model router for open chat with a D1-student cascade for fault triage.
- Nightly enrichment runs through batch.
- PTU-plus-spillover capacity sits behind APIM priority pools.
- CPST dashboards break down cost per task type and per tenant.

## Factory increment — your agentic SDLC

- A **perf gate** in CI runs the mock-backend NBomber suite for orchestration overhead and the cached eval suite for each PR. It fails on a P95 regression over 15%, a CPST regression over 10% on the fixture traces, or a cache-hit drop over 10 points.
- A `/cost-review` skill lets an agent read a PR diff and the trace workbook and comment on prompt-layout changes, new dynamic prefix fields, unbounded tool outputs and missing `max_output_tokens`.
- An agent may propose an optimization, but merging needs the paired eval report attached. This is recorded in `AGENTS.md`.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| KPI discipline | Tracks the token bill | Cost per request | CPST per task type with success from evals | CPST with guardrails (quality CI bound, latency SLO), per tenant, including human review |
| Latency diagnosis | Total time | TTFT vs total | Per-stage waterfall from traces | Targets the dominant term; quantifies reasoning and output share; validates under load |
| Caching | None or global | Prompt reordering | Prompt cache + semantic cache with TTL | Partitioned semantic cache with measured false-hit and leak tests; cache-regression alerting |
| Routing & batch | One model for all | Static routing | Router or cascade with chosen thresholds | Thresholds from dev curves, paired tests, a router pinning policy; batch for all non-blocking work |
| Capacity & load | Buys PTU on instinct | Uses the calculator | Break-even math | Distribution-based sizing with spillover, validated by a cost-capped realistic load test |

**Auto-checked:** `CpstTests`, the cache-hit alert, `CacheLeakTests`, `SemanticCacheEval` thresholds, the cascade quality/cost gates, `BatchIngestionTests`, the perf gate thresholds, and the Bicep deployment of the workbook and APIM policies.

## Common pitfalls

- Optimizing cost per token instead of cost per successful task.
- Dynamic fields (time, IDs) at the start of prompts, and nondeterministic tool order.
- Semantic caching personalized, time-sensitive or role-trimmed answers. That is a data leak, not an optimization.
- Router pools that include a small-context model, or EU-residency violations through Global deployments.
- Escalation thresholds picked by intuition instead of dev curves.
- Load-testing with uniform tiny prompts, and running real-model load tests without a cost cap.
- Ignoring `Retry-After`, so retries amplify 429 storms.
- Buying PTU for peak, or for a model about to be deprecated (PTU deployments are not auto-upgraded).
- Shipping "optimizations" without paired quality evals.


## References

- Microsoft Learn — APIM AI gateway capabilities (token limits, metrics, semantic cache, backend pools, circuit breaker): https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities
- Microsoft Learn — Foundry model router concepts: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-router
- Microsoft Learn — Models sold directly by Azure (shared context budget, reasoning tokens): https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure
- Microsoft Learn — Foundry model retirements (PTU not auto-upgraded): https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
- Claude Opus 5.5 overview (prompt caching and batch pricing): https://platform.claude.com/docs/en/models/opus-5-5/overview
- MCP 2026-07-28 changelog (deterministic `tools/list` for cache hit rates): https://modelcontextprotocol.io/specification/2026-07-28/changelog
- Anthropic — Code execution with MCP (token reduction): https://www.anthropic.com/engineering/code-execution-with-mcp
- Anthropic — Contextual retrieval (cost with caching, <200k-token rule of thumb): https://www.anthropic.com/news/contextual-retrieval
- OTel GenAI semantic conventions status: https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained ; https://dev.to/azena-ai/opentelemetrys-genai-semantic-conventions-are-not-stable-yet-heres-what-actually-shipped-in-2026-3mke
- Digital Applied — September 2026 model tracker (per-task vs per-token cost): https://www.digitalapplied.com/blog/ai-model-releases-september-2026-tracker
- Leviathan et al., Speculative decoding: https://arxiv.org/abs/2211.17192 · Kwon et al., PagedAttention: https://arxiv.org/abs/2309.06180
- Azure Architecture Center — Baseline Foundry chat RA (PTU for baseline, PAYG for variable load): https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
