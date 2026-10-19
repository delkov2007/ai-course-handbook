# Competency matrix

*AI Solution Developer & AI Solution Architect*

> **Purpose:** the single definition of what learners must be able to *do* at each stage, used for self-assessment, lab rubrics, gate rubrics, capstone grading and portfolio statements. · **Release:** 2026.11 · **Owner:** course lead (changes go through the quarterly course review)

## 1. How to read this matrix

**Twelve competency areas (K1–K12)** cover the AI-specific part of the job. General software engineering (Git, testing basics, HTTP, SQL) is an entry prerequisite and is not repeated here.

**Four levels**, each defined by *observable behaviour*. Every cell describes what an assessor can see in a repo, a trace, a CI run, a document or an oral answer. Knowledge alone ("knows what RAG is") never qualifies.

| Level | General meaning | Typical point in the course | SFIA-style analogue (course-designer inference) |
|---|---|---|---|
| **Novice** | Follows a worked example. Can name the concept and reproduce the happy path with guidance. Doesn't yet see failure modes. | During Level 1 | Level 2 (assist) |
| **Competent** | Builds the thing independently from a spec, recognises the common failure modes when shown evidence, and fixes them with standard techniques. | Required at **G1** (L1 areas) and **G2** (L2 areas) | Level 3 (apply) |
| **Proficient** | Chooses among alternatives with measured trade-offs, anticipates failure modes before they happen, verifies systematically and explains decisions in writing. | Evidenced at **G3** in all core areas (blocks + evidence pack; pass rule and area mapping in [Assessment and gates](assessment-gates.md) §5) | Level 4 (enable) |
| **Expert** | Designs the verification and the system together, handles novel situations and conflicting constraints, teaches and sets standards for others, and defends decisions under questioning. The Expert level is **split by role**. | Required at **capstone** in the learner's track-critical areas | Developer: Level 4–5 · Architect: Level 5–6 |

**Expert is split by role.** At Expert level the Developer and the Architect are expected to do *different* things, not more or less of the same thing. The Developer goes deeper into engineering (implementing, measuring, hardening). The Architect goes broader in judgement (deciding, constraining, governing across systems and teams). Both must still meet Proficient everywhere.

**Graduation requirements:**
- Proficient in all 12 areas.
- Expert in the 6 **track-critical** areas for your track, marked ● in §3.
- No area below Proficient at the capstone defense.

**Evidence rules:**
1. A behaviour counts only if there is an artefact or an observation: a commit, a CI run, an eval report, a trace, a document, or an oral answer recorded on the assessor's sheet.
2. AI assistance is expected. The *learner* must be able to explain and modify the evidence (see the integrity stance in [Assessment and gates](assessment-gates.md)).
3. A single observation of a behaviour is enough to reach Novice or Competent. Proficient and Expert need consistency across at least two different contexts, such as a lab and a gate, or the product and the capstone.

---

## 2. The twelve areas

### K1 · AI foundations (models, tokens, economics, limits)

| Level | Observable behaviours |
|---|---|
| Novice | Calls a model from code. Can state that tokens, not words, are billed and limited. Repeats a lab measurement when given the script. |
| Competent | Predicts and then measures token counts and cost for EN vs BG text. Handles `finish_reason=length` and context overflow. Demonstrates that temperature 0 is not deterministic and stops asserting exact strings in tests. Picks a model role (fast-small / workhorse / frontier reasoning) for a task and states why. |
| Proficient | Builds a quality × cost × latency table for one task across ≥ 3 models, including a local one, and a reasoning-effort sweep. Recognises cases where an LLM is the wrong tool (tabular prediction, high-volume deterministic classification, fixed-layout extraction) and proposes the alternative with evidence. Distinguishes per-token price from per-task cost. |
| Expert — Developer | Diagnoses quality regressions to their mechanism (context position, tokenisation, sampling, effort, cache-busting prompt layout) from traces. Runs model bake-offs as reproducible eval jobs. Sizes local or self-hosted models (memory by total parameters, compute by active parameters for MoE, quantisation trade-offs). |
| Expert — Architect | Sets model-selection policy by capability class rather than by name. Writes the "LLM vs classical ML vs specialised service" decision as an ADR that survives model churn. Explains these trade-offs to non-technical stakeholders without overstating capability. Treats vendor benchmarks as saturating and mostly vendor-run, and requires domain evals. |

**Typical evidence:** C1 measurement notebook, C1/C2 explanation write-ups, D1 sizing sheet, A1 portfolio memo.

### K2 · Prompting & structured I/O

| Level | Observable behaviours |
|---|---|
| Novice | Writes a system prompt and few-shot examples from a template. Uses structured output when told to. |
| Competent | Defines JSON-Schema-constrained outputs mapped to C# types. Measures schema-failure rate vs free-text parsing. Versions prompts in the repo. Writes tool descriptions that a reviewer finds unambiguous. |
| Proficient | Lays out prompts for caching (static prefix first) and verifies cache hits in telemetry. Designs abstention ("not in sources") and clarification paths. Handles BG/EN mixed input. Writes prompt changes as reviewable diffs with eval deltas. |
| Expert — Developer | Builds prompt and schema middleware (validation, repair, retry with budget) in the MEAI pipeline. Detects prompt brittleness with perturbation evals. Treats prompts, tool schemas and judge prompts as versioned, tested artefacts with owners. |
| Expert — Architect | Sets organisation-wide conventions for prompt and schema management (registry, versioning, review, ownership). Decides where structured contracts sit between systems, and when to use typed decision models or classifiers instead of free generation. |

**Typical evidence:** C3 labs, `prompts/` history, C15 prompt registry, A7 standards document.

### K3 · Retrieval & knowledge

| Level | Observable behaviours |
|---|---|
| Novice | Embeds documents and runs a vector query following a lab. Explains chunks and similarity in their own words. |
| Competent | Builds hybrid retrieval (BM25 + vectors with RRF) plus a reranker, with citations. Implements security trimming from identity claims (`allowed_groups`) and proves that no out-of-role document is returned. Knows that switching embedding models means re-embedding the corpus. |
| Proficient | Evaluates retrieval (recall@k, nDCG) separately from generation (groundedness, completeness) on a stratified golden set that includes abstention, permission and injection cases. Compares parsing options on tables and scans. Chooses a vector store via an ADR. Applies contextual chunking or quantisation where measurements justify it. |
| Expert — Developer | Climbs the retrieval ladder empirically (vector → hybrid → rerank → contextual → agentic retrieval) and stops where the evals plateau. Implements blue/green re-indexing with index aliases. Tunes BG/EN retrieval with language-specific analysers and evals. Decides on GraphRAG against measured global-question performance. |
| Expert — Architect | Designs the enterprise knowledge platform: source-of-truth ownership, data readiness, index lifecycle, permission propagation (GA pattern vs preview native ACLs), residency, cost model (fixed search units vs database capacity), and multi-tenant index strategy. Decides "no RAG" when the corpus fits in a cached prompt (roughly < 200k tokens). |

**Typical evidence:** C6/C7 ADR and eval report, C13 GraphRAG decision, A3 knowledge-platform design.

### K4 · Tools & MCP

| Level | Observable behaviours |
|---|---|
| Novice | Registers a C# method as a tool with `AIFunctionFactory` and observes the model calling it. Can explain that the model *requests* tool calls and the application executes them. |
| Competent | Designs consolidated, namespaced tools with pagination, truncation and actionable errors, and shows they beat CRUD-style tools on an eval set. Ships an MCP server with the C# SDK on the 2026-07-28 spec, consumed by the app and a coding agent. |
| Proficient | Proves statelessness (several replicas behind round-robin). Applies Entra OAuth to MCP. Propagates trace context via `_meta`. Recognises outdated 2025-era MCP patterns (handshake, sessions, SSE, sampling) and migrates them. Picks a hosting model (Functions vs ACA vs APIM export) with justification. |
| Expert — Developer | Builds code-as-tool-interface variants and measures the token savings. Implements tool-definition pinning and hashing against rug pulls. Writes MCP Apps or Tasks-extension features where they fit. Builds tooling for coding agents, such as an MCP server over the project's own schema and tickets. |
| Expert — Architect | Designs the tool and MCP topology for an organisation: a gateway (APIM / toolbox) with per-tool policy via `Mcp-Method`/`Mcp-Name` headers, a server registry, approval and pinning, identity (on-behalf-of vs agent identity), and the seams with low-code (Copilot Studio) and A2A peers. Rejects "MCP by default" when a direct API call is simpler. |

**Typical evidence:** C3/C8 labs, C16 poisoned-MCP lab, A4 integration design.

### K5 · Agents & orchestration

| Level | Observable behaviours |
|---|---|
| Novice | Runs a MAF agent with tools from a template. Distinguishes a workflow (predefined code paths) from an agent (model-directed). |
| Competent | Writes a tool loop by hand and ports it to MAF. Adds explicit termination: max iterations, token and cost budgets, timeouts, a final-answer schema, repetition detection. Adds human approval for consequential actions. |
| Proficient | Chooses the lowest rung on the complexity ladder (direct call → workflow → single agent → multi-agent) using eval, cost and latency evidence. Implements checkpointed, resumable workflows with HITL. Explains when multi-agent helps (read-heavy, parallel) and when it hurts (write-heavy, coupled), with the ~15× token cost in view. |
| Expert — Developer | Builds durable, long-running agents (persisted sessions, HITL waits without compute). Hosts them (Foundry hosted agents / Container Apps). Engineers reliability (pass^k, simulators, fault injection). Builds custom harnesses with the Copilot SDK or Claude Agent SDK where they fit. |
| Expert — Architect | Defines the agent platform: which agent types are allowed where (prompt, hosted, low-code), registry and lifecycle (agents as code, immutable versions), inter-agent trust boundaries (A2A, signed agent cards), and an autonomy policy that ties levels of agency to risk class and oversight. |

**Typical evidence:** C9/C12 labs and ADRs, D2/D7 reliability report, A4 platform design.

### K6 · Context & memory

| Level | Observable behaviours |
|---|---|
| Novice | Keeps chat history in a session. Can explain why the context window is a budget. |
| Competent | Demonstrates context rot and "lost in the middle" with a lab measurement. Implements tool-result clearing and summarisation-based compaction. Scopes session memory per user. |
| Proficient | Chooses between compaction, structured notes, sub-agents and just-in-time retrieval for a long-horizon task on measured outcomes. Designs memory with TTL, GDPR "forget", write-time validation against poisoning, and multi-session evals. Decides what goes in memory files vs skills vs hooks for coding agents. |
| Expert — Developer | Builds context-assembly pipelines with explicit token budgets per section and tests them. Implements procedural memory distilled from trajectories, with evaluation of the gain. Diagnoses agent failures caused by context composition from traces. |
| Expert — Architect | Sets memory and retention policy across products (what may be remembered, where, for how long, under whose control). Aligns that policy with the DPIA, residency and the AI Act logging requirements. Decides platform memory (preview) vs owned memory stores with lock-in and audit in view. |

**Typical evidence:** C13 labs, C4/C19 Factory memory files, A6 retention policy.

### K7 · Evaluation

| Level | Observable behaviours |
|---|---|
| Novice | Runs a provided eval suite and reads its report. |
| Competent | Reads ≥ 30 real traces before writing evaluators. Open-codes failures and builds a golden set from them. Writes binary, code-based checks where possible. Gates CI on eval thresholds with response caching. |
| Proficient | Builds a failure taxonomy through axial coding. Writes one judge per failure mode, validated against human labels with TPR and TNR on separate dev and test splits. Builds trajectory evals from spans. Runs a pairwise model-migration comparison per failure mode. Refreshes the eval set from new traces on a schedule. |
| Expert — Developer | Builds evaluators *for others' systems* (the "green agent"). Builds simulated-user harnesses (τ-bench style) reporting pass^k. Calibrates judges for Bulgarian where vendor classifiers are English-only. Detects eval overfitting and leakage. Keeps eval cost under control. |
| Expert — Architect | Defines the organisation's evaluation policy: which evidence is required for release, migration and risk files, who owns golden sets, how evals feed AI Act technical documentation and ISO/IEC 42001 evidence, and the acceptance thresholds tied to business risk. Rejects generic "helpfulness" scores as release criteria. |

**Typical evidence:** C5/C14 eval reports, G1–G3 hidden-eval results, capstone eval report, A6 evidence pipeline.

### K8 · Testing & SDLC automation (the Factory)

| Level | Observable behaviours |
|---|---|
| Novice | Uses a coding agent in chat or agent mode to scaffold and explain code, and reviews the diff before committing. |
| Competent | Maintains short, curated AGENTS.md/CLAUDE.md files. Runs plan → implement → verify. Writes failing acceptance tests that the agent must satisfy. Configures permissions and a format/build hook. Requires the agent to run tests and evals before claiming done. |
| Proficient | Runs test-first specs with a mutation-score gate and E2E test agents, and audits healer changes. Picks the right spec ceremony for the change size. Runs parallel agents in worktrees. Puts AI review and CodeQL autofix in CI under branch protection. Can explain every merged line. |
| Expert — Developer | Builds custom agents, skills, plugins and harnesses (Copilot SDK / Claude Agent SDK). Runs unattended agents safely: sandboxes, least-privilege tokens, egress allow-lists, package allow-lists against slopsquatting. Measures first-pass acceptance, rework and cost per merged PR, and improves them. |
| Expert — Architect | Governs the Factory across teams: agent permission and sandbox policy, required gates, data and model choices for coding agents, Azure Repos vs GitHub capability differences, DORA plus AI-specific metrics, an operating model, and a review practice that prevents codebase cognitive debt. |

**Typical evidence:** Factory repo history, agent session logs, C11/C19 labs, G1 oral, A7 governance policy.

### K9 · Operations, observability & cost

| Level | Observable behaviours |
|---|---|
| Novice | Turns on OTel in MEAI and finds a model call in the Aspire dashboard. |
| Competent | Traces a request across app, agent, tools and MCP server. Writes KQL for latency, errors and token usage. Sets budgets and TPM limits and keeps lab spend within them. |
| Proficient | Attributes cost per task, per feature and per tenant. Keeps trace content capture off by default and documents why. Versions prompts and models with canary promotion. Rehearses a model migration with a go/no-go memo. Diagnoses an incident from traces within a time box. |
| Expert — Developer | Engineers cost and latency down (caching, routing and cascades, batch, semantic cache where safe) at equal eval scores. Load-tests 429 behaviour and failover. Pins semconv versions and maps attributes in the Collector. Writes runbooks and postmortems that others can execute. |
| Expert — Architect | Designs the AI gateway (quotas, chargeback, priority pools PTU → PAYG, circuit breaking), the FinOps model (PTU vs PAYG break-even, showback), the model-lifecycle process (retirement watch, 60-day plan, PTU not auto-upgraded), SLOs and DR by reconstruction. Checks cost models against actuals. |

**Typical evidence:** C15/C17 dashboards, G3 incident block, D5 cost report, A5 lifecycle and FinOps plan.

### K10 · Security

| Level | Observable behaviours |
|---|---|
| Novice | Keeps secrets out of the repo and uses keyless auth. Can state that prompt injection is unsolved at the model level. |
| Competent | Identifies the lethal trifecta in a design and removes one leg. Implements least-privilege tools, approval for state changes and conversation-ownership checks (BOLA). Runs safety evaluators in CI. |
| Proficient | Threat-models with STRIDE mapped to OWASP LLM Top 10 (2025) and Agentic Top 10 (ASI01–ASI10). Applies injection design patterns (plan-then-execute, dual LLM, action selector, context minimisation). Runs red-team scans and reports attack success rate (ASR) before and after fixes. Uses Foundry guardrails as a second layer, not the first. |
| Expert — Developer | Builds and runs attack suites (PyRIT / AI Red Teaming Agent [Python], custom attacks in BG/EN). Implements sandboxed code execution with egress blocks. Implements MCP pinning, memory-poisoning defences and package allow-lists. Fixes classes of vulnerability, not single instances. |
| Expert — Architect | Designs agent identity and access (Entra Agent ID, Conditional Access, OBO vs app identity), network isolation (private endpoints, egress firewall), trust boundaries between agents and tenants, and the security review process. Applies the Agents Rule of Two in design reviews. |

**Typical evidence:** C16 threat model and ASR report, capstone red-team swap, G3 red-team block, A4/A6 designs.

### K11 · Responsible AI & governance

| Level | Observable behaviours |
|---|---|
| Novice | Adds an AI disclosure to the UI. Knows the EU AI Act exists and has risk tiers. |
| Competent | Classifies a feature under the AI Act as amended by Regulation (EU) 2026/1744, identifying prohibited, high-risk (Annex III), transparency (Art. 50) and minimal-risk cases. Recognises the provider vs deployer role. Writes a DPIA-relevant data flow. Recognises that Trakia's driver monitoring touches Annex III employment use cases. |
| Proficient | Produces a risk file: intended purpose, classification rationale, data governance, logging, human-oversight design, accuracy and robustness evidence from evals, and transparency notices. Designs oversight that works (interrupt and override, not rubber-stamping). Knows the current dates (Art. 50 from 2 Aug 2026; Annex III from 2 Dec 2027; Annex I from 2 Aug 2028) and that the Bulgarian implementing details need checking at source. |
| Expert — Developer | Implements oversight, logging and transparency mechanisms as tested features. Produces evidence (eval reports, red-team scorecards, model and system cards) automatically from the pipeline. Builds bias and performance-disparity evals, e.g. BG vs EN users. |
| Expert — Architect | Designs the AI management system (ISO/IEC 42001-style): inventory, risk classification process, roles, controls mapped to the AI Act, NIST AI RMF and ISO 42001, an evidence pipeline and change control. Shapes the intended purpose to avoid unnecessary high-risk classification where that is legitimate. Advises leadership on the regulatory timeline and where legal counsel is required. |

**Typical evidence:** C18 risk file, capstone AI Act risk file, A6 governance design.

### K12 · Architecture & business

| Level | Observable behaviours |
|---|---|
| Novice | Draws a context diagram of the product and writes a first ADR from a template. |
| Competent | Writes ADRs with real alternatives and consequences. Maintains C4 context and container diagrams as text. Estimates the monthly cost of a feature from token measurements. |
| Proficient | Deploys with IaC behind a gateway with private networking. Writes a cost model that matches actuals within an agreed tolerance. Writes a DR plan for components without native DR (reconstruction from agents as code) and runs a drill. Runs a WAF AI assessment and acts on findings. |
| Expert — Developer | Shapes technical architecture from below: proposes ADRs backed by measurements, prototypes risky decisions as spikes with evals, enforces architecture with fitness functions (ArchUnitNET/NetArchTest) and explains trade-offs to architects and product owners. |
| Expert — Architect | Moves from business problem to a scored use-case portfolio, ROI and TCO, build/buy/extend (least operational responsibility first), reference architecture and landing zone, multi-tenancy, a roadmap and an operating model (CoE). Defends these decisions to a review board and to non-technical stakeholders. Keeps the design simple enough to operate. |

**Typical evidence:** ADR log, C17 deployment, A1–A7 deliverables, capstone architecture package and defense.

---

## 3. Track-critical areas

● = must reach Expert for the track. ○ = Proficient is enough (Expert welcome).

| Area | Developer | Architect |
|---|---|---|
| K1 AI foundations | ● | ○ |
| K2 Prompting & structured I/O | ● | ○ |
| K3 Retrieval & knowledge | ○ | ● |
| K4 Tools & MCP | ● | ○ |
| K5 Agents & orchestration | ● | ● |
| K6 Context & memory | ○ | ○ |
| K7 Evaluation | ● | ○ |
| K8 Testing & SDLC automation | ● | ○ |
| K9 Operations, observability & cost | ○ | ● |
| K10 Security | ○ | ● |
| K11 Responsible AI & governance | ○ | ● |
| K12 Architecture & business | ○ | ● |

Both tracks share K5 (agents and orchestration) as critical, because the most expensive mistakes of 2026, such as needless multi-agent systems and unbounded loops, are made jointly by builders and designers.

---

## 4. Traceability: which modules build each area

Legend, following the spiral: **I** = introduced, **O** = operationalised (built and used), **N** = industrialised (automated, gated, at production quality), **S** = strategised (policy, organisation, business). Gates assess the area at the level shown in brackets.

| Module | K1 Found. | K2 Prompt/IO | K3 Retrieval | K4 Tools/MCP | K5 Agents | K6 Context/Mem | K7 Eval | K8 SDLC | K9 Ops/Cost | K10 Security | K11 RAI/Gov | K12 Arch/Bus |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | I | | | | | | | I | I | I | | |
| C1 | **O** | I | I | | | I | I | | I | | | |
| C2 | O | O | | | | I | | I | O | I | | I |
| C3 | O | **O** | | I | I | | I | | | I | | |
| C4 | | O | | | | I | | **O** | | I | | |
| C5 | O | | | | | | **O** | O | | | | |
| **G1** | [C] | [C] | | [–] | | | [C] | [C] | | | | |
| C6 | O | | **O** | | | | O | | O | | | O |
| C7 | | O | **O** | | | O | O | | | O | | O |
| C8 | | O | | **O** | I | | | O | | O | | O |
| C9 | | | | O | **O** | O | O | | O | O | I | |
| C10 | | O | O | O | O | | O | | | **O** | | |
| C11 | | | | | | | O | **O** | | | | |
| **G2** | | [C] | [C] | [C] | [C] | | [C] | [C] | | [C] | | [C] |
| C12 | | | | | **N** | O | O | | O | | O | O |
| C13 | | | N | | O | **N** | O | O | | O | O | |
| C14 | | | | | | | **N** | N | | O | O | |
| C15 | N | N | | | | | N | N | **N** | | | O |
| C16 | | | | N | N | N | | N | | **N** | O | O |
| C17 | | | | N | N | | | N | N | N | | **N** |
| C18 | | | | | | O | O | | | | **N** | O |
| C19 | | | | | | N | N | **N** | N | N | | |
| **G3** | [P] | [P] | [P] | [P] | [P] | [P] | [P] | [P] | [P] | [P] | [P] | [P] |
| D1 | **E** | E | | | | | E | | E | | | |
| D2 | | | | E | **E** | E | | | E | | | |
| D3 | E | E | | E | E | | | | | | | |
| D4 | | E | | E | E | | | | | | E (oversight UX) | |
| D5 | E | E | E | | | E | | | **E** | | | |
| D6 | | | | **E** | E | E | | **E** | | E | | |
| D7 | | | | | **E** | | **E** | E | E | E | | |
| A1 | S | | | | | | | | S | | S | **S** |
| A2 | | | | | S | | | | S | **S** | | **S** |
| A3 | | | **S** | | | S | | | | S | S | S |
| A4 | | S | | **S** | **S** | | | | S | S | | S |
| A5 | S | | S | | | | S | | **S** | | | S |
| A6 | | | | | | S | S | | | S | **S** | |
| A7 | | S | | | | | S | **S** | S | | | **S** |
| Capstone | E/S | E/S | E/S | E/S | E/S | E/S | E/S | E/S | E/S | E/S | E/S | E/S |

Gate levels: [C] Competent, [P] Proficient. G1 marks K4 as [–] (not assessed; not to be confused with N = industrialised). Its one-tool scope is too narrow to judge tools.

**Coverage rules the course applies each release:**
- Every area has ≥ 1 I, ≥ 2 O/N and ≥ 1 E or S entry.
- Every ● area for a track has ≥ 2 modules in that track at E or S.
- Every gate assesses every area it claims, with at least one rubric row.

Current known thin spots, to address in the next revision:
- **K6 (context and memory)** has no architect-track module that strategises it deeply. A3 and A6 cover retention and knowledge scope only.
- **K11 for developers** relies on C18 plus D4. Developer-track learners who want Expert in K11 should take the A6 module as an elective.

---

## 5. Using the matrix

- **Self-assessment.** At the start, at each gate and before the capstone, learners rate themselves per area and attach one evidence link per rating. Mentors compare the ratings with gate results. Large gaps in either direction, particularly over-confidence, are discussed in mentor sessions. The METR finding that developers felt ~20% faster while measuring ~19% slower is the motivating example of why self-perception is not evidence.
- **Rubric derivation.** Every module rubric (Novice / Competent / Proficient / Expert) is derived from the relevant cells here. If a module rubric contradicts the matrix, the matrix wins and the module is fixed in the next release.
- **Portfolio statements.** Graduates describe themselves by area and level with linked evidence, e.g. "Evaluation: Expert (Developer) — built a calibrated BG groundedness judge, TPR 0.91 / TNR 0.88 on held-out test split; capstone eval report link". Graduates do not use generic claims like "experienced in GenAI".
- **Hiring-side reading.** Employers should read the Expert level as "demonstrated on realistic, assessed tasks with synthetic data", not as years of production ownership.
