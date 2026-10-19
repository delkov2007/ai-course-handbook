# A1 — AI strategy, use-case discovery & business case

> **Level:** Expert — AI Solution Architect track · **Duration:** 16h (theory 30% / labs 70%) · **Prerequisites:** Core C0–C19 and Gate G3 passed (you have a working, traced, evaluated Fleet Ops Copilot) · **Volatility:** Med (methods are stable; prices, SKUs, licensing and certification blueprints change quarterly)

## Why this matters

**What separates an expert architect from a proficient one here:** a proficient architect can estimate what an AI feature costs to run. An expert can show, with numbers they can defend, *which* problems deserve AI at all, which should be bought instead of built, and what evidence must exist before a pilot is allowed to become a product. The expert treats the business case as a falsifiable hypothesis that evals and telemetry will confirm or kill. The proficient architect treats it as a slide that unlocks budget.

Trakia Freight's board has decided, after a good demo, to (a) roll Fleet Ops Copilot out to all 600 drivers, ~45 dispatchers, ~35 mechanics and the office functions across Plovdiv, Sofia and Varna, and (b) sell it as multi-tenant SaaS to other fleets. The usual failure pattern follows:

- Every department submits "AI ideas" and the team builds the loudest one.
- Time savings are counted as cash.
- Token costs are estimated from one happy-path prompt, although a multi-agent workflow burns roughly 15× the tokens of a chat turn.
- Nobody budgets for eval labelling, red-teaming or the model migrations that 12–18-month lifecycles force.
- The HR policy bot is custom-built when an M365 Copilot licence would have done.
- Driver-behaviour scoring, an EU AI Act Annex III employment use case, slips in as "just analytics".

Experts run discovery as a structured, evidence-producing process:

- They score use cases on value, feasibility *and* risk, and kill most of them early and cheaply.
- They model TCO across five cost families: tokens, infrastructure, people, evals and ops.
- They apply the Cloud Adoption Framework (CAF) rule of "least operational responsibility".
- They write pilot-to-production criteria *before* the pilot starts.

## Learning outcomes

By the end of this module you can:

1. **Facilitate** a use-case discovery workshop, using persona interviews, a process walk and a pain/value inventory, and produce a backlog of at least 8 use-case canvases with explicit value hypotheses.
2. **Score and rank** use cases on value, feasibility and risk with a weighted, documented rubric. **Defend** at least two "kill" decisions and one "not an LLM problem" decision.
3. **Assess** AI readiness across six dimensions (data, platform, skills, governance, process, culture) and **quantify** data readiness with queries against the real estate (`TrakiaOps`, document corpus).
4. **Build** a ROI/TCO model as code plus a spreadsheet view, covering tokens, infrastructure, people, evals and ops. **Calibrate** cost per task from production traces, not prompt guesses.
5. **Run** sensitivity and Monte Carlo analysis, and **identify** the three assumptions that drive the business case.
6. **Choose and justify** build vs buy vs extend per use case (M365 Copilot, Copilot Studio, Foundry agents, custom MAF), applying the CAF "least operational responsibility" rule, and record the choice as an ADR.
7. **Define** measurable pilot-to-production gates covering eval thresholds, adoption, cost per task, SLOs, security and compliance, plus success metrics with leading, lagging and guardrail indicators.
8. **Map** your deliverables to the AB-100 "Plan AI-powered business solutions" skill area.

## Concepts

### 1. Strategy is a portfolio, not a project

An AI strategy for a mid-size company is a *portfolio* of bets with different risk/return profiles, governed by one platform and one set of controls. For Trakia it has three horizons:

- **H1 — productivity inside existing workflows** (low risk, mostly buy/extend): HR and policy Q&A, email drafting for customer service, meeting summaries.
- **H2 — process redesign with agents** (medium risk, build on the platform): incident triage → diagnostics → maintenance booking (C12), the Fleet Analyst over telematics (C10).
- **H3 — new revenue** (high risk, build): Fleet Ops Copilot as SaaS for other fleets.

H1 funds credibility, H2 funds the platform, and H3 needs the platform to exist. A common mistake is to start H3 (SaaS) before H2 has proven unit economics and operational maturity internally. Trakia's internal rollout is the cheapest place to learn what a tenant costs.

The CAF AI adoption scenario structures the journey as **AI planning → AI ready → govern, secure, manage**. Its build-vs-buy heuristic is explicit: prefer the option "with the least operational responsibility". That means SaaS such as M365 Copilot and Copilot Studio first, then PaaS (Foundry, Fabric, Azure ML, Container Apps). IaaS "shouldn't be the default". CAF folds skilling into workforce enablement and has no separate agent-adoption guidance, so you supply that yourself (A7).

### 2. Use-case discovery: how experts run it

Discovery fails when it starts from "where can we use AI?". It succeeds when it starts from *work*: who does what, how often, how long it takes, what it costs when it goes wrong, and what data exists at that moment. The expert sequence:

1. **Frame**: the business goals for the year (Trakia: cut unplanned downtime, cut SLA penalties, grow revenue without growing headcount 1:1) and the constraints (GDPR, EU AI Act, Bulgarian-language users, works council).
2. **Persona interviews** (30 min each, 6–8 personas): use "tell me about the last time…" questions, never "would AI help you?".
3. **Process walk**: map the incident flow from fault code to repaired truck. Mark waiting time, handoffs, rework and lookups.
4. **Pain/value inventory**: one sticky per pain with frequency × time × cost-of-error.
5. **Use-case canvas** per candidate, with these fields:
   - actor and trigger;
   - task;
   - current KPI baseline;
   - value hypothesis ("We believe X will reduce Y from A to B, measured by M");
   - data needed and where it lives;
   - action level (inform / recommend / act with approval / act autonomously);
   - failure cost;
   - regulatory flags;
   - "is an LLM the right tool?" check.
6. **Score, then cut**: most candidates should die at this step.

**"Is it an LLM problem?" check.** Apply it ruthlessly, because many of Trakia's ideas are not LLM problems:

- **Predicting component failure from telematics** is tabular prediction → ML.NET/AutoML.
- **Reading scanned delivery notes** is fixed-layout extraction with per-field confidence → Content Understanding or Document Intelligence.
- **Classifying 50k engine fault codes per day** is high-volume deterministic classification → a fine-tuned small model (D1) or a typed decision model.
- **Answering "which clause of the customer SLA applies to this late delivery?"** needs language understanding over documents → an LLM with RAG.

The architect's value is often in redirecting a use case to the cheaper, more explainable technique.

### 3. Scoring: value × feasibility × risk

Use a weighted rubric with anchored levels (1–5). Anchors make scores comparable between assessors.

| Dimension | Sub-criteria (weight) | Anchor examples |
|---|---|---|
| **Value** (40%) | Hard € impact (50%), strategic fit (20%), frequency × reach (20%), time-to-value (10%) | 5 = > €200k/yr hard benefit or enables revenue; 1 = < €10k/yr, soft only |
| **Feasibility** (35%) | Data readiness (35%), eval-ability (25%; can we define pass/fail?), integration effort (20%), skills (20%) | 5 = data clean and accessible, golden set exists; 1 = data on paper, no ground truth |
| **Risk** (25%, scored inverted) | Regulatory class (35%), failure cost and reversibility (30%), security exposure / lethal trifecta (20%), change/people impact (15%) | 5 = minimal-risk, read-only, reversible; 1 = Annex III high-risk, autonomous actions on people |

Two decision rules sit on top of the weighted score:

- **Hard gates override the score.** A prohibited practice (Art. 5) is killed regardless of value. An Annex III use case cannot enter a pilot without a governance-board decision (A6). A use case with eval-ability 1 cannot enter a pilot until someone can say what "correct" means.
- **Plot, don't just rank.** A value-vs-feasibility bubble chart, with bubble size = risk, shows the "quick wins", the "strategic bets" that need a spike first, and the "money pits".

**Misconception to unlearn: "high value + high feasibility = do it now".** For an agent that *acts* (books maintenance, emails a customer), feasibility must include whether you can build the HITL step and the evals for that action. "We can call the API" is not enough.

### 4. AI readiness assessment

Microsoft and others publish AI readiness instruments (verify the current Microsoft instrument before teaching). This course uses a six-dimension, evidence-based assessment. The rule is that every score must cite an artefact or a query result, never an opinion.

| Dimension | Evidence you collect at Trakia |
|---|---|
| Data | % of incident reports with a valid vehicle ID; document freshness (share of policies reviewed < 12 months ago); ACL coverage (share of documents with role metadata); BG/EN split; corpus size in tokens |
| Platform | Landing zone exists? Private networking? APIM? Observability (C15)? IaC coverage? |
| Skills | Who can run error analysis, write evals, operate agents? Named people, not roles |
| Governance | AI policy, inventory, DPIA practice, risk classification process (A6) |
| Process | Can the target process absorb a recommendation? Who acts on it, and in which system? |
| Culture / change | Works council stance, driver trust, manager sponsorship |

Corpus size is a design input, not trivia. Anthropic's rule of thumb is that knowledge bases under ~200k tokens can skip RAG and go into a cached prompt. A department-specific use case (e.g., the 40-page depot safety handbook) may need no retrieval pipeline at all.

### 5. ROI and TCO: the five cost families

The TCO of an AI product has five families. Most business cases model only the first.

1. **Tokens.**
   - *Formula:* cost per task = Σ over model calls of (uncached input × p_in + cached input × p_cached + (output + reasoning tokens) × p_out). Reasoning tokens are billed and share the context budget.
   - *Per-token price ≠ per-task cost.* A model with a cheaper per-token price can cost more per task because it uses more tokens.
   - *Multi-agent multiplier:* multi-agent systems use ~15× the tokens of chat (Anthropic's research system). Calibrate from your C15 traces, never from a single prompt.
2. **Infrastructure.**
   - *Fixed baseline:* AI Search tier, Cosmos DB, App Gateway + WAF, Azure Firewall, DDoS Protection, APIM tier, private endpoints, Log Analytics ingestion. The baseline Foundry chat reference architecture names Cosmos DB, AI Search and DDoS Protection as the largest cost lines.
   - *Variable:* compute for hosted agents and Container Apps, Redis for the semantic cache, storage, egress.
3. **People.**
   - Platform team, product team share, an SME "benevolent dictator" for quality labels, a governance role, on-call.
   - People usually dominate internal-product TCO in Bulgaria-scale salary markets.
4. **Evals and assurance.**
   - Error-analysis time: practitioners report spending 60–80% of development time on error analysis and evaluation.
   - Human labelling: 100–200 labelled examples per failure mode to validate a judge.
   - Judge tokens on CI and on sampled production traffic, red-team runs, re-labelling after every model change.
5. **Ops and change.**
   - *Model migrations.* GA models get a minimum of 18 months (12 for Anthropic, DeepSeek, Fireworks and Mistral; some Grok models 6), with ≥60 days' retirement notice. Budget at least one migration per primary model per year, including eval re-runs and prompt re-tuning (A5).
   - *Other run costs:* index rebuilds, incident handling, user support, training and adoption.

**Worked example (illustrative prices — verify current Azure prices before use).** A Fleet Assistant policy Q&A turn on a "Sol-class" model priced at $2 / $10 per million input/output tokens:

- 2,500 static tokens (system prompt and tool schemas, cacheable), 4,000 retrieved tokens, 500 history tokens, 500 output tokens and 800 reasoning tokens.
- Uncached cost: 7,000 × $2/M + 1,300 × $10/M ≈ $0.027.
- Caching the static prefix trims this further. The exact saving depends on the provider's cached-read discount: Anthropic lists cached reads at $0.20 vs $4 base input for Opus 5.5, while the Azure OpenAI discount must be verified.
- At 3,000 such turns per working day, that is ~$80/day, roughly €19k/year.

Now compare that with one platform engineer's loaded cost, or with a DDoS Protection plan. The lesson is that **for the internal rollout, tokens are rarely the dominant TCO line. For the SaaS product at 40 tenants with heavy Fleet Analyst usage, they can become one.** You only know which case you are in after modelling both.

**Benefits: hard vs soft.**

- Time saved is a *soft* benefit unless the capacity is redeployed or avoids a hire. Example: 35 mechanics × 20 min/day × 220 days × €18/h ≈ €46k/year of *capacity*, not cash.
- *Hard* benefits for Trakia are fewer unplanned downtime days, which carry lost revenue per truck-day, lower SLA penalties, and SaaS subscription revenue.
- An expert presents hard and soft benefits separately and never lets the soft line carry the case.

**Model the uncertainty.** Every input gets a range (P10/P50/P90), not a point. Run:

- a one-at-a-time sensitivity analysis, shown as a tornado chart;
- a Monte Carlo simulation (10k draws) to report P(NPV > 0) and payback-period percentiles.

The three assumptions at the top of the tornado chart become the **pilot's learning objectives**. If adoption rate drives the case, the pilot must measure adoption.

### 6. Build vs buy vs extend

| Option | What it is | Choose when | Trakia example |
|---|---|---|---|
| **Buy: M365 Copilot** (and its agents) | SaaS assistant over Microsoft Graph content | Knowledge work inside M365, users already licensed, content in SharePoint/Teams/Outlook | HR policy Q&A and email drafting for office staff |
| **Extend: Copilot Studio** | Low-code agents with connectors and topics, publishable to Teams/M365; A2A integrated | Departmental workflows, citizen-dev maintainability, moderate integration | Customer-service "where is my shipment" agent calling the C8 MCP server |
| **Build on PaaS: Foundry Agent Service** (prompt agents, hosted agents, Foundry IQ) | Managed agent runtime, knowledge bases, guardrails, evaluations, tracing | Pro-code needs but you want the platform to own hosting, state and safety plumbing | Incident triage agents; policy RAG via Foundry IQ |
| **Build custom: MAF on Container Apps / Functions** | Full control of orchestration, hosting, networking, multi-tenancy | Multi-tenant SaaS, unusual isolation or residency constraints, deep workflow control, portability | The SaaS product's tenant-aware agent runtime |

**Decision rules:**

1. Apply the CAF rule first: the least operational responsibility that *meets the requirements*.
2. Then test the knock-out requirements:
   - **Multi-tenancy for external customers:** M365 Copilot cannot serve another company's drivers. The SaaS product is a build.
   - **Data residency and processing location:** see A3.
   - **Eval-ability:** can you run your golden set and judges against the option? If you cannot evaluate it, you cannot govern it.
   - **Exit cost:** where do prompts, knowledge and conversation state live, and can you export them?
   - **Seam availability:** MCP and A2A let low-code and pro-code agents share tools and call each other, so "extend" no longer means "dead end".

**Misconception to unlearn: "buying is always cheaper".** Per-seat licences × 600 drivers can exceed a consumption-priced custom agent, and drivers do not live in M365. Compare cost at your *actual* adoption curve, and verify licence prices on the day you decide.

### 7. Pilot-to-production criteria and success metrics

Write the gate before the pilot starts. A Trakia pilot charter defines:

- **Scope:** one depot (Plovdiv), 12 dispatchers, 10 mechanics, 8 weeks, named sponsor and product owner.
- **Learning objectives:** the top three tornado assumptions.
- **Exit to production requires *all* of:**
  - eval pass-all rate ≥ target on the hidden suite (C14), with no failure mode below its floor;
  - Bulgarian-calibrated groundedness judge ≥ 90% on sampled traffic;
  - red-team ASR ≤ agreed threshold;
  - cost per task P50 within ±25% of model;
  - p95 latency SLO met for 4 consecutive weeks;
  - weekly active use ≥ 60% of pilot users in weeks 6–8;
  - DPIA approved and AI inventory entry complete (A6);
  - security review closed (C16 threat model);
  - runbooks and rollback tested.
- **Kill criteria:** for example, cost per task > 2× model after optimisation, or adoption < 30% by week 6 with no fixable cause found in interviews.

**Success metrics come in three kinds:**

- **Leading** (adoption, task completion, deflection to human, thumbs-down rate).
- **Lagging** (downtime days per truck, SLA penalties, incident handling time).
- **Guardrail** (escalations, wrong-action incidents, complaints, cost per task, ASR).

A metric without a baseline is not a metric. Capture baselines in week 0.

### 8. AB-100 alignment

AB-100's "Plan AI-powered business solutions" area (25–30%) maps onto this module:

- requirements and grounding-data readiness → Labs 1–2;
- CAF adoption and an AI CoE → §1 and Lab 5;
- ROI including TCO → Lab 3;
- build/buy/extend and multi-agent design across M365 Copilot, Copilot Studio and Foundry → Lab 4;
- model router → Lab 3 stretch.

Its deploy domain (ALM, governance, residency, audit trails) is covered in A4–A6.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| Lab repo `architecture/business/` | Baselines (`baseline.xlsx`), persona cards, use-case canvas template | Course asset | Synthetic Trakia data |
| `Trakia.CostModel` (.NET 10 console + xUnit) | Cost/ROI model as code: `assumptions.yaml` → per-task, per-tenant, annual TCO, Monte Carlo | Course asset | Uses `YamlDotNet`; pin version |
| Azure Retail Prices API | Pull current list prices for infra SKUs | GA | Public REST endpoint; prices are list, not your EA rate |
| Azure Pricing Calculator / Foundry pricing pages | Token, PTU, AI Search, APIM prices | — | Verify before every business case; model prices change monthly |
| Application Insights + KQL (from C15) | Measured tokens per task from `gen_ai.usage.*` attributes | GA (semconv "Development") | Pin semconv version as in C15 |
| Microsoft Foundry (prompt agent + Foundry IQ knowledge base) | "Build on PaaS" spike | Foundry IQ KBs GA; Serverless preview | |
| Copilot Studio | "Extend" spike | GA | Licensing model: verify against current documentation |
| M365 Copilot declarative agent | "Buy/extend" spike | GA | Requires tenant licences; instructor tenant provided |
| MAF 1.0 (`Microsoft.Agents.AI`) | Existing custom build | GA | From C9/C12 |
| `Microsoft.Extensions.AI.Evaluation` + `dotnet aieval` | Same golden set across options | GA (verify package versions on NuGet) | |
| Model router (`2025-11-18`) | Cost lever in the stretch lab | Latest auto-updating version | Effective context = smallest model in pool |

## Labs

### Lab 1 — Discovery workshop with simulated stakeholders (≈3h)

- **Goal:** Produce a defensible use-case backlog from structured interviews, not from an ideas list.
- **Start state:** branch `a1/start`. Contains `architecture/business/personas/*.md`: dispatcher (Sofia), mechanic (Varna), fleet manager, HR lead, customer-service lead, CFO, works-council representative, and the commercial director pushing SaaS. Also contains `baseline.xlsx` and `canvas-template.md`.
- **Steps:**
  1. Spin up the **stakeholder simulator**: a MAF agent per persona card (instructions = persona, goals, hidden pains, data they know). The cards contain *hidden facts* that only good "tell me about the last time…" questions reveal.
     ```csharp
     // One agent per persona; instructions loaded from the card. Verify exact API against current docs.
     AIAgent dispatcher = chatClient.AsAIAgent(
         name: "persona-dispatcher-sofia",
         instructions: File.ReadAllText("personas/dispatcher-sofia.md"));
     AgentSession s = await dispatcher.CreateSessionAsync();
     var reply = await dispatcher.RunAsync("Tell me about the last breakdown you handled.", s);
     ```
  2. Run 30-minute interviews with at least 6 personas. Log every interview transcript to `discovery/interviews/` (the factory will analyse them).
  3. Walk the incident process (fault code → triage → workshop slot → parts → customer notice). Annotate waits, handoffs and lookups in a swimlane diagram (`discovery/process-incident.md`, Mermaid).
  4. Fill ≥ 8 use-case canvases. At least one must be redirected to non-LLM technology, and at least one must carry an AI Act flag (driver-behaviour scoring).
  5. Score all canvases with the rubric (`scoring.yaml`). Two team members score independently, then reconcile the scores and record the disagreements.
- **Break it:** The instructor injects a "CEO pet project": "AI that predicts which drivers will quit". Score it honestly: value is unclear, it is Annex III employment, it involves profiling, and works-council exposure is high. Write the one-paragraph kill or defer memo.
- **Acceptance criteria:**
  - `dotnet test architecture/business/tests`: the canvas schema validator passes (all mandatory fields filled; the value hypothesis matches the pattern "We believe … from … to … measured by …").
  - ≥ 6 interview transcripts exist.
  - Inter-rater score difference ≤ 1 point on ≥ 80% of sub-criteria after reconciliation (computed by script).
  - The hidden-fact coverage report shows ≥ 5 of 9 hidden pains discovered.
- **Stretch:** Use the factory to run axial coding over interview transcripts (as you did with traces in C14) and compare the agent's pain taxonomy with yours.

### Lab 2 — AI readiness and data-readiness spike (≈2.5h)

- **Goal:** Replace readiness opinions with measured evidence and find the data blockers before they find you.
- **Start state:** `a1/lab2-start`, plus `TrakiaOps` and the document corpus from `/data`.
- **Steps:**
  1. Write `readiness/queries.sql` against `TrakiaOps`:
     - % of incidents with a valid `VehicleId` and `FaultCode`;
     - median lag between telematics fault event and incident record;
     - % of work orders with parts lines;
     - null rates on driver pseudonym joins.
  2. Write a small .NET tool that profiles the corpus:
     - token counts per document and per collection, BG vs EN, using `Microsoft.ML.Tokenizers` with the encoding matching your pinned model;
     - % of documents with an owner, a review date and role ACL metadata;
     - duplicate and near-duplicate ratio (content hash plus embedding similarity > 0.95).
  3. Compute per-use-case corpus size. Flag every use case whose relevant corpus is < 200k tokens as a "cached-prompt candidate, no RAG".
  4. Score the six readiness dimensions. Each score cites a query result or artefact path.
  5. Produce `readiness/report.md` with a "blockers & remediation" table: owner, effort and the date the use case unblocks.
- **Break it:** The instructor swaps in a corpus snapshot where 30% of HR documents lack ACL metadata. Re-run the analysis. Your report must now block the HR use case (custom-build path) until security trimming can be guaranteed, or redirect it to M365 Copilot, which inherits SharePoint permissions.
- **Acceptance criteria:**
  - Profiler unit tests pass.
  - The report includes a token count per collection (±2% of the reference).
  - Every readiness score has an evidence link (checked by script).
  - At least one use case changes its score because of measured data.
- **Stretch:** Estimate golden-set effort per use case (questions × minutes per label × SME rate). This number feeds the evals family in Lab 3.

### Lab 3 — ROI/TCO model as code, calibrated from traces (≈4h)

- **Goal:** A business case where every number traces to a measurement, a price source or an explicit, ranged assumption.
- **Start state:** `a1/lab3-start` with `Trakia.CostModel` skeleton, `assumptions.yaml` (empty ranges) and `prices.2026-10.yaml`. The price file carries illustrative list prices from vendor and aggregator sources (e.g., GPT-6 Sol $2/$10, Luna $0.10/$0.50, Claude Opus 5.5 $4/$20, Haiku 5.5 $0.10/$0.50 per MTok, Haiku price: verify against current documentation). It is labelled **verify on Azure pricing before use**.
- **Steps:**
  1. **Measure** per-task tokens from your C15 telemetry. Run the KQL below for three task types (policy Q&A, Fleet Analyst query, multi-agent incident workflow).
     ```kusto
     dependencies
     | where customDimensions["gen_ai.operation.name"] == "chat"
     | extend task = tostring(customDimensions["trakia.task.type"]),
              inTok = toint(customDimensions["gen_ai.usage.input_tokens"]),
              outTok = toint(customDimensions["gen_ai.usage.output_tokens"]),
              cached = toint(customDimensions["gen_ai.usage.cache_read.input_tokens"])
     | summarize calls=count(), p50In=percentile(inTok,50), p90In=percentile(inTok,90),
                 p50Out=percentile(outTok,50), p90Out=percentile(outTok,90), cachedShare=avg(todouble(cached)/inTok)
       by task
     ```
     Join on `operation_Id` to get calls per task. Expect the incident workflow to be an order of magnitude above Q&A.
  2. **Infra:** pull prices via the Azure Retail Prices API for the C17 bill of materials (AI Search, Cosmos DB, APIM, App Gateway WAF, Firewall, DDoS Protection, Log Analytics, Container Apps). Store the raw response with its retrieval date.
  3. **People, evals, ops:** FTE ranges, labelling hours (Lab 2 stretch), model migrations (primary models × 1/year × engineer-days), red-team runs per release.
  4. **Benefits:** hard (downtime days avoided × € per truck-day, SLA penalties avoided) and soft (hours) on separate lines. SaaS scenario: tenants × trucks × €/truck/month (fictional) × churn.
  5. Implement `MonteCarlo.Run(10_000)` with triangular distributions. Output NPV P10/P50/P90, P(NPV > 0), payback percentiles and a tornado chart.
  6. Generate the executive spreadsheet from the model (`dotnet run -- export xlsx`). The spreadsheet is a *view*, never edited by hand.
- **Break it:** Three shocks, applied one at a time, each with its effect on P(NPV > 0) recorded:
  - (a) the provider's newer model uses 1.6× more tokens per task at the same price;
  - (b) the incident workflow gains a reflection loop, doubling calls;
  - (c) adoption reaches only 35%.
- **Acceptance criteria:**
  - `dotnet test`: unit tests validate the per-task formula against three hand-computed cases (±0.5%).
  - Every assumption has `{p10,p50,p90,source}`, with no empty `source` (schema test).
  - Infra prices carry a retrieval timestamp < 30 days old.
  - The tornado chart's top 3 assumptions are listed in `business-case.md`.
  - A reviewer can regenerate the spreadsheet bit-for-bit from the repo.
- **Stretch:** Add the model router (Balanced / Quality / Cost modes) as a scenario. Measure the per-task cost delta on 100 replayed Q&A traces. Note that the effective context window equals the smallest model in the pool.

### Lab 4 — Build vs buy vs extend spike (≈4h)

- **Goal:** Decide, with evidence, how Trakia should deliver *HR & policy Q&A for office staff*, and how that differs from the *driver-facing* and *SaaS* use cases.
- **Start state:** `a1/lab4-start`. Instructor M365 tenant with SharePoint HR library (same documents as `/data/hr`). Your C7 RAG and C14 golden set (HR subset, 60 questions, including 10 permission-restricted and 8 "not in corpus").
- **Steps:**
  1. **Extend/buy:** build an M365 Copilot declarative agent or a Copilot Studio agent over the SharePoint library (time-box 60 min, and log effort).
  2. **PaaS:** create a Foundry prompt agent with a Foundry IQ knowledge base over the same documents (time-box 60 min).
  3. **Custom:** use your existing MAF RAG agent from C7/C9.
  4. Run the same 60 questions through all three. For the SaaS options, use your eval harness. For M365/Copilot Studio, capture answers via the available test or export path, or manually if needed; record how you did it, because eval-ability is itself a criterion. Score them with the C14 judges, the Bulgarian-calibrated groundedness judge, and permission-leak checks.
  5. Fill the decision matrix: quality, permission correctness, BG quality, effort to build, ops responsibility (who patches, monitors, migrates models), per-user-month cost at your adoption curve, exit cost, eval-ability.
  6. Write **ADR-A1-001 "HR & policy Q&A delivery option"** and ADR-A1-002 "SaaS product delivery option". These are different answers for different use cases.
- **Break it:** Remove one HR document's permissions in SharePoint mid-test. Which options reflect the change, and how fast? Record the propagation latency for each option. This previews A3.
- **Acceptance criteria:**
  - The eval report for all three options is committed (`dotnet aieval report` for the harness-driven options).
  - Zero permission leaks is a hard requirement for any option you recommend.
  - Both ADRs pass the ADR linter: context, ≥ 3 options considered (incl. "do nothing / status quo" where meaningful), decision, consequences, evidence links and a review date.
  - The matrix records real measured effort hours.
- **Stretch:** Make the Copilot Studio agent call the C8 MCP server for live shipment status, and the incident agent via A2A. Document what the "extend" option becomes once protocol seams exist.

### Lab 5 — Business case, pilot charter and ARB defence (≈2.5h)

- **Goal:** Package everything into the artefacts an executive committee and an architecture review board (ARB) will act on.
- **Start state:** Outputs of Labs 1–4.
- **Steps:**
  1. Write a 2-page **executive memo**: decision asked for, portfolio (H1/H2/H3), P50 NPV with P10–P90 range, top 3 risks, what the pilot will prove, cost of *not* doing it.
  2. Write the **pilot charter** with gate criteria (Concepts §7) and kill criteria. Every metric needs a baseline and a measurement method (KQL query, survey or system report).
  3. Write the **success-metric tree**: lagging business outcome → leading indicators → guardrails.
  4. Write a half-page **AI CoE/platform charter** sketch: who owns the platform, the eval practice and the governance gate (expanded in A4/A7).
  5. Defend the case to the ARB (instructor + 2 peers) in 15 minutes plus 10 minutes of questions. At least one ARB member plays the CFO and one plays the works council.
- **Break it:** The ARB "CFO" demands a single number with no ranges. Respond without losing the uncertainty, e.g., P50 plus the probability of loss plus the assumption the pilot retires.
- **Acceptance criteria:** All artefacts are in `architecture/business/`. The pilot charter linter passes (every gate has a threshold, a source query and an owner). The ARB rubric score is ≥ Proficient on all criteria.
- **Stretch:** Draft a 1-page SaaS go-to-market assumption sheet (tenant segments, pricing hypothesis, cost to serve per tenant) that A4/A5 will validate.

## Kata

**"Twenty-five-minute use-case triage"** (repeat 4–6 times, each with a new card).

The instructor deals one use-case card (half a page: actor, pain, data, desired action). In 25 minutes you produce:

1. Is it an LLM problem? Name the alternative technique if not.
2. Value/feasibility/risk scores with one-line justifications.
3. Hard regulatory flags (Art. 5 / Annex III / Art. 50 / GDPR special categories).
4. Build/buy/extend recommendation.
5. The single riskiest assumption and the cheapest spike that tests it.

Variations:
- Customer-contract clause lookup.
- Fault-code classification at 50k/day.
- Driver fatigue detection from cabin camera. Check the Art. 5 workplace emotion-recognition prohibition and its safety exception (verify against current documentation; not legal advice).
- Tachograph infringement explainer for drivers in Bulgarian.
- Supplier invoice matching.
- Customer churn prediction for the SaaS business.

Compare with the instructor's reference triage. The score is the number of dimensions within ±1 point plus a correct regulatory flag.

## Product increment — Fleet Ops Copilot

Fleet Ops Copilot now has a **business owner's view**:

- a scored use-case portfolio (H1/H2/H3);
- a calibrated ROI/TCO model that regenerates from code and telemetry;
- two delivery ADRs: HR Q&A bought or extended, SaaS built;
- a pilot charter for the Plovdiv depot with measurable gates;
- a readiness report whose blockers (ACL metadata, incident data quality) become backlog items for the platform.

The driver-behaviour scoring idea is formally *deferred* to the A6 governance board, with its Annex III flag recorded.

## Factory increment — your agentic SDLC

- **`/usecase-triage` skill:** reads a canvas, runs the scoring rubric, checks regulatory flags against a keyword and decision table, and writes a draft score file *for human review*. It never commits a final score.
- **`cost-per-task` CI job:** nightly KQL export → `Trakia.CostModel` → fails the build if measured P50 cost per task drifts > 25% from the business-case assumption. A cost regression gate now sits next to your eval gates.
- **ADR linter and pilot-charter linter** in CI, so architecture artefacts get the same treatment as code.
- **Interview and trace analysis agent:** the C14 open/axial coding workflow reused on discovery transcripts.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Discovery quality | Ideas list; no baselines | Canvases with some baselines | ≥ 8 canvases with baselines and falsifiable hypotheses; ≥ 5 hidden pains found | Plus redirected non-LLM cases and a reasoned kill memo; interview evidence cited per canvas |
| Scoring & prioritisation | Unweighted ranking | Weighted rubric | Anchored rubric, inter-rater reconciliation, hard gates applied | Plus sensitivity of the ranking to weights shown; portfolio balanced across horizons with explicit sequencing logic |
| ROI/TCO model | Token cost only | Tokens + infra | Five cost families, ranges, trace-calibrated tokens, hard vs soft benefits | Plus Monte Carlo, tornado-driven pilot objectives, reproducible from code, model-migration and eval costs explicit |
| Build/buy/extend | Preference stated | Matrix without evidence | Measured spike across 3 options, ADRs per use case | Plus exit cost, eval-ability and protocol seams (MCP/A2A) analysed; different answers per use case justified with CAF |
| Pilot gates & communication | "Pilot for 3 months" | Some metrics | Gates with thresholds, sources, owners, kill criteria | Plus metric tree with guardrails, executive memo that survives CFO and works-council challenge |

**Auto-checked:**
- canvas schema;
- inter-rater script;
- readiness evidence links;
- cost-model unit tests and assumption schema;
- price freshness;
- spreadsheet regeneration diff;
- `dotnet aieval` reports for the spike;
- permission-leak test results;
- ADR and charter linters.

## Common pitfalls

- Counting hours saved as cash, or letting soft benefits carry the NPV.
- Estimating tokens from one prompt, forgetting reasoning tokens, retries, judges and the multi-agent multiplier.
- Ignoring the cost of evals, labelling and model migrations.
- One build/buy answer for the whole programme.
- Risk scored as an afterthought, so Annex III or Art. 5 issues surface after the pilot.
- Pilot criteria written after the pilot, or metrics without baselines.
- RAG for a corpus that fits in a cached prompt.
- Prices without a source and a date.


## References

- CAF AI adoption scenario (plan, ready, govern, secure, manage; "least operational responsibility"): https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/
- AB-100 study guide (ROI/TCO, build/buy/extend, CoE, model router): https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ab-100
- Baseline Microsoft Foundry chat reference architecture (cost drivers: Cosmos DB, AI Search, DDoS; PAYG vs PTU): https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
- Foundry model retirements (lifecycle durations, 60-day notice): https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
- Model router concepts (modes, custom subset, smallest-context rule): https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-router
- Anthropic, multi-agent research system (~15× tokens vs chat): https://www.anthropic.com/engineering/multi-agent-research-system
- Anthropic, contextual retrieval (skip RAG below ~200k tokens): https://www.anthropic.com/news/contextual-retrieval
- Claude Opus 5.5 pricing and caching (illustrative price source): https://platform.claude.com/docs/en/models/opus-5-5/overview
- Hamel Husain & Shreya Shankar, evals FAQ (labelling effort, 60–80% time on evals): https://hamel.dev/blog/posts/evals-faq/
- Per-task vs per-token cost (aggregator, treat as indicative): https://www.digitalapplied.com/blog/ai-model-releases-september-2026-tracker
- Azure Retail Prices API: https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices (verify URL before teaching)
- Foundry IQ / What's new in Microsoft Foundry, Build 2026 (Foundry IQ GA; Serverless preview): https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-build-2026/
- Linux Foundation A2A press release (Copilot Studio and Foundry integration): https://linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year
