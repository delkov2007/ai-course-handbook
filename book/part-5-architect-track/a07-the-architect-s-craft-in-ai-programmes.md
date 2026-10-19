# A7 — The architect's craft in AI programmes

> **Level:** Expert — AI Solution Architect track · **Duration:** 14h (theory 30% / labs 70%) · **Prerequisites:** A1–A6; C19 (automated SDLC); your factory from C4–C19 · **Volatility:** Med (the craft is durable; tool landscapes, radar placements and productivity evidence change every few months)

## Why this matters

**What separates an expert architect from a proficient one here:** a proficient architect produces good designs. An expert produces good *decisions* in a programme: decisions that are recorded, testable, communicated so each audience can act on them, estimated honestly under uncertainty, and continuously verified by fitness functions. The expert also leads the team and the agentic factory that implement those decisions, measuring outcomes rather than output and governing what the agents may do. In AI programmes the gap between the two shows quickly, because:

- the technology changes quarterly;
- quality is statistical;
- costs scale with behaviour;
- stakeholders range from the CFO to a works council that worries about drivers being watched.

Trakia is now an AI programme, not a project. It runs an internal rollout across three depots, a SaaS business with prospects asking for proposals, a governance board, a platform team and a product team whose code is mostly written by agents. The architect's week has five different jobs in it:

- an ADR on whether to adopt a preview feature;
- an architecture review where a team claims its design "meets the quality bar";
- an executive steering meeting about a delayed milestone;
- a works-council session about the driver-coaching pilot;
- a pre-sales workshop with a 120-truck fleet in the Rhodopes.

There is also the agentic factory to govern. DORA 2025 found about 90% AI adoption among developers and describes AI as "a mirror and a multiplier": it amplifies whatever discipline exists. METR's early-2025 trial found experienced developers **19–20% slower** with AI while they *believed* they were faster. METR's February 2026 update says developers are probably sped up now, but calls its own evidence "very weak" on the size. An architect who governs the factory on vibes will get vibes.

This closing module of the architect track (not to be confused with the joint capstone) trains the craft: ADRs for AI, fitness functions with evals at their core, communication by audience, estimation under uncertainty, pre-sales solution design, governing AI-augmented teams, an organisational technology radar and a personal system for keeping current.

## Learning outcomes

1. **Write** ADRs for AI decisions that record evidence, volatility, reversibility, cost of change and review triggers tied to model lifecycles and preview status.
2. **Define and automate** architecture fitness functions (quality evals, cost per task, latency, ASR, isolation, dependency rules) and **run** an architecture review that uses them as evidence.
3. **Communicate** one architecture to executives, legal/DPO, a works council and engineers, adapting content, risk framing and asks to each audience.
4. **Estimate** AI work under uncertainty with ranges, reference classes, spikes and eval-gated milestones, and **explain** estimates to sponsors without false precision.
5. **Lead** pre-sales solution design: discovery, a solution blueprint, PoC/pilot design with success criteria, and a priced proposal with stated assumptions and risks.
6. **Govern** the agentic factory: permission and sandbox policies, model and data policies, DORA plus AI-specific metrics, and an operating model with clear roles.
7. **Build and maintain** an organisational technology radar with evidence-based placements and a quarterly cadence aligned to vendor event cycles.
8. **Operate** a personal and team system for keeping current that distinguishes signal (lifecycle notices, GA changes) from noise (leaderboards, launch hype).

## Concepts

### 1. ADRs for AI decisions

No authoritative standard for "AI ADRs" exists, so the format here is a **course convention** built on the classic ADR shape (context, options, decision, consequences), with **≥ 3 options considered (incl. "do nothing / status quo" where meaningful)**; the ADR linter enforces this. It adds fields that AI decisions specifically need:

| Field | Why AI needs it | Example (Trakia) |
|---|---|---|
| **Evidence** | Statistical quality claims need eval reports, not opinions | "pass^4 = 0.86 vs 0.71 (report link)" |
| **Volatility** | Preview features and model versions change under you | "Depends on AI Search `2026-08-01-preview` (query planning)" |
| **Reversibility / cost of change** | Some choices are config (model role), some are migrations (embedding model, vector store) | "Embedding change = full re-index, ~6h at year-1 scale" |
| **Review triggers** | Decisions expire with model retirements, GA moves and cost thresholds | "Revisit at GA of knowledge-source ACLs, or if cost/task > €0.06, or at retirement of model X (date)" |
| **Assumptions & owners** | Business-case assumptions (A1) drive design | "Adoption ≥ 60% (owner: product)" |
| **Compliance impact** | Changes can re-tier a system (A6) | "No change to risk tier" |

**ADRs as agent context.** An ADR-driven repo (`docs/adr/`, C4 DSL, `architecture.md`) doubles as context for coding agents. Agents read the decisions, and architecture tests (ArchUnitNET/NetArchTest) catch drift. Keep ADRs short, link evidence, and supersede them rather than edit them.

### 2. Architecture reviews and fitness functions

A **fitness function** is an objective, automated check that an architectural characteristic holds. For AI systems, **evals are fitness functions** for quality:

| Characteristic | Fitness function | Where it runs |
|---|---|---|
| Answer quality | Failure-mode pass rates with judges validated by TPR/TNR (C14) | PR (cached), nightly (uncached) |
| Agent reliability | pass^k on τ-bench-style scenarios; tool-call accuracy | Nightly |
| Safety | Red-team ASR ≤ threshold (C16/A6) | Weekly / release |
| Isolation & permissions | Canary leak tests, permission matrix (A3) | Every PR |
| Cost | Cost per successful task ≤ budget (A1/A5) | Nightly from telemetry |
| Latency | TTFT p95 under load (A5) | Release |
| Structure | Dependency rules: no unfiltered retriever; agents only call tools via gateway (ArchUnitNET/NetArchTest) | Every PR |
| Lifecycle | No model role retiring within the release window without a migration ticket (A5/A6) | Every PR |

**Running an architecture review:**

- **Bring evidence, not slides.** The package contains the WAF AI assessment (A2), C4 with the AI profile, ADRs, fitness-function results, the cost model and the DR test report.
- **Review the decision record and the risks**, not the diagram aesthetics.
- **Outcome:** approve / approve with conditions / rework, with conditions written as new fitness functions where possible.
- **Watch for "reviewer always finds something".** Anthropic notes that review agents asked to find gaps will always find some, which pushes toward over-engineering. The same holds for human boards. Weigh findings by risk and cost.

### 3. Stakeholder communication by audience

The same architecture is presented to each audience as different arguments:

| Audience | What they decide | What they need | Trakia example |
|---|---|---|---|
| Executives / steering | Funding, priorities, risk appetite | Outcome vs plan, P50/P90 ranges, top risks with mitigations, explicit asks | "Pilot met 7 of 9 gates; cost/task 18% over; ask: approve 6-week extension for adoption work" |
| CFO | Investment, pricing | Unit economics, margin per tenant tier, sensitivity | A5 price floor per isolation tier |
| Legal / DPO | Lawfulness, contracts, regulatory exposure | Data flows, roles (provider/deployer), DPIA, residency, sub-processors, evidence | A3 data-location register + A6 evidence pack |
| **Works council / employee representatives** | Consent or consultation on monitoring and workplace technology | Purpose, what is *not* done (no rankings, no HR use), data minimisation, who sees what, retention, worker rights, oversight, how to complain, the trial and review plan | Driver-coaching pilot: private feedback, depot aggregates ≥ N, no individual manager view |
| Engineers / product teams | How to build | ADRs, paved road, fitness functions, examples | Golden agent template, gateway onboarding |
| Customers (SaaS) | Buy / trust | System card, security and residency, SLOs, roadmap, AI Act role split | Deployer-support pack (A6) |

**Communication rules:**

- **Lead with the decision you need.**
- **Express uncertainty as ranges and probabilities**, never as unearned precision.
- **Show what the system will *not* do.** This is especially powerful with works councils and legal teams.
- **Separate facts, estimates and opinions.**
- **Bring evidence links.**

For driver monitoring, labour-law consultation duties (and Art. 26(7)-style worker information for high-risk systems; verify) make the works council a *gate*, not a courtesy. Plan it into the timeline.

### 4. Estimation under uncertainty

AI work carries unknowns that conventional estimation ignores:

- **Reachability of the quality bar.** You do not know whether 90% groundedness on Bulgarian table questions is achievable until error analysis.
- **Data readiness surprises** (A1 Lab 2).
- **Model behaviour changes** across migrations.
- **Adoption.**
- **Preview feature timing.**

Techniques:

- **Ranges and reference classes.** Estimate P50/P90 from your own history of similar work (the C-track increments are your first reference class), not from bottom-up optimism.
- **Spikes as uncertainty purchases.** A 3-day spike that answers "can we reach 85% on table questions?" is worth more than 3 weeks of detailed planning. Price the spike against the value of the information.
- **Eval-gated milestones.** Plan in stages that end with a measurable eval result: "M2: error analysis complete, failure taxonomy, baseline pass rates". Re-estimate at each gate. Commit to the next gate firmly and to the whole programme only in ranges.
- **Monte Carlo on task ranges** (reuse A1's engine) to produce delivery-date distributions.
- **Make the cone of uncertainty visible** to sponsors. Report "P(done by date)" and what would move it.
- **Agent-augmented estimates.** Agent speed-ups vary by task type and team discipline (DORA "amplifier"; METR's evidence is mixed). Calibrate from *your* factory metrics (§6), not vendor claims.

### 5. Pre-sales and solution design

The architect in pre-sales converts a prospect's ambiguity into a credible, bounded proposal:

1. **Discovery.** Run A1's workshop, compressed into 1–2 days. Assess data readiness and constraints (residency, isolation demands, integration with the prospect's telematics provider and TMS).
2. **Solution blueprint.** Context diagram, tenant tier (pooled/bridge/silo), integration points (MCP/A2A), oversight design, AI Act role split, SLOs.
3. **PoC vs pilot vs MVP:**
   - A **PoC** answers one technical question (time-boxed, disposable).
   - A **pilot** tests value with real users under production-like controls.
   - An **MVP** is the first sellable increment.

   Never let a PoC become production by drift. Avoid the **demo trap**, where a scripted happy path sets expectations the eval suite will not support. Demo against the prospect's own sampled data with eval scores shown.
4. **Success criteria agreed in writing:** eval thresholds on the prospect's golden set, adoption, cost per task, SLOs.
5. **Proposal.** Scope, assumptions (each with an owner), exclusions, risks, a pricing basis from A5 unit economics, a ranged timeline, and the change process.

### 6. Leading AI-augmented teams and governing the factory

**Evidence to calibrate expectations:**

- **DORA 2025:** ~90% AI adoption. AI use is linked to higher throughput, but ensuring software works before delivery remains a challenge. The **AI Capabilities Model** names seven practices:
  1. clear AI policy;
  2. healthy data ecosystem;
  3. accessible internal knowledge;
  4. strong version control and code review;
  5. user-centric focus;
  6. platform engineering;
  7. small batches.

  Larger changesets raise instability.
- **Thoughtworks Radar Vol. 34 (Apr 2026):**
  - *Caution:* coding throughput as a productivity measure, agent instruction bloat, coding agent swarms, "MCP by default", codebase cognitive debt.
  - *Adopt:* DORA metrics ("lines of code generated is misleading; rework rate exposes blind spots"), context engineering, curated shared instructions.
  - *Trial:* mutation testing, feedback sensors, sandboxed execution as default.
- **Slopsquatting.** 19.7% of 2.23M AI code samples referenced hallucinated packages, and 43% of the hallucinated names recurred on every run. That makes package allow-lists a governance must.

**The factory governance policy** (one document, enforced by configuration):

- **Permissions and sandboxing:**
  - coding agents run in sandboxes/devcontainers with egress allow-lists;
  - cloud agents push only to agent branches;
  - CI on agent PRs needs human approval;
  - production credentials are never available to coding agents.
- **Model and data policy:**
  - approved models and providers for coding agents (BYOK to Foundry where required);
  - what code and data may leave the tenant;
  - no production personal data in agent contexts.
- **Supply chain:**
  - package allow-lists;
  - lockfiles with hash verification;
  - new-package age rules;
  - skills, plugins and MCP servers vetted and pinned (A4 registry applies to the factory too).
- **Quality gates:** human-owned acceptance tests, mutation score, eval gates, AI review *plus* human review. "Explain the diff" is required for high-risk changes.
- **Accountability:** a human is accountable for every merged line. Agent-authored changes are attributable (assess Agent Trace-style attribution).

**Metrics.** Pair the DORA keys (deployment frequency, lead time, change failure rate, time to restore; plus rework rate) with factory-specific measures:

- first-pass acceptance rate of agent PRs;
- iterations per PR;
- mutation score;
- escaped defects;
- eval regression rate;
- **agent cost per merged PR**;
- review time per PR (a cognitive-load signal).

**Reject** lines of code, PR counts and "% code written by AI" as goals.

**Operating model.** The roles:
- product teams owning agents and evals;
- the platform team owning the paved road (A4);
- governance owning tiers and boards (A6);
- the architect owning decisions and fitness functions.

Add **deliberate-practice rituals** against skill atrophy: unaided katas, and diff-defence reviews where the human explains the agent's change.

### 7. A technology radar for your organisation

A radar records *your* organisation's positions, with evidence. It is not a copy of an industry radar.

- **Rings:**
  - **Adopt:** default, paved road.
  - **Trial:** use on real work with an owner and exit criteria.
  - **Assess:** spike only.
  - **Hold:** don't start new work.
- **Quadrants for Trakia:** platforms, tools, techniques, protocols/standards.
- **Every blip has:** an owner, evidence (spike report, eval delta, cost), the date, the status of the underlying feature (GA/preview), and a review trigger.
- **Cadence:** quarterly, plus extra passes after Microsoft Build (May/June) and **Ignite (November)**, when previews typically move. Ignite 2026 is imminent at the time of writing.
- **Seed blips, from this course:**
  - Adopt: MAF 1.0; APIM AI gateway policies; AI Search GA extractive KBs; failure-driven evals; mutation testing.
  - Trial: Foundry hosted agents (GA 9 Jul 2026); Foundry Toolboxes (GA); MCP C# SDK 2.0 (experimental APIs).
  - Assess: Foundry memory / Routines (preview); AI Search query planning (preview); ASSERT / Agent Control Specification; agentgateway; Spec Kit / OpenSpec.
  - Hold: Assistants API (retired); MCP sessions/SSE/sampling patterns; coding agent swarms.

### 8. Keeping current without drowning

- **Signals that demand action:**
  - model lifecycle notices (A5 watcher);
  - GA/preview transitions of features you depend on;
  - SDK major versions;
  - protocol revisions (MCP deprecation windows end ≥ 28 Jul 2027);
  - regulatory dates and guidance (A6);
  - security advisories.
- **Noise:** leaderboards (saturating and largely vendor-run), launch-day benchmark claims, "X is dead" posts.
- **System:**
  - an automated watch for lifecycle and release notes;
  - a monthly 2-hour "currency review" with the team;
  - quarterly radar updates;
  - nightly lab and product CI against live models (the course itself does this) to detect real breakage;
  - a personal reading list of primary sources: Learn "What's new" pages, the Architecture Center, protocol changelogs, the Hamel/Shankar evals FAQ, Anthropic engineering posts, DORA, Thoughtworks Radar.
- **Credentials as a forcing function.** AB-100 for architects and AI-103 for developers both changed in 2026. Use them to check breadth, not as proof of depth.

## Tools & versions (as of Oct 2026)

| Tool / resource | Purpose | Status | Notes |
|---|---|---|---|
| ADR template (course convention) + ADR linter | Decision records | Course asset | Extended AI fields |
| ArchUnitNET / NetArchTest | Structural fitness functions | OSS | Verify current versions |
| `Microsoft.Extensions.AI.Evaluation` + `dotnet aieval` | Quality fitness functions | GA (verify versions) | |
| WAF AI Assessment Review Tool | Review instrument | GA | From A2 |
| GitHub REST/GraphQL API, Azure DevOps Analytics | Factory metrics extraction | GA | |
| GitHub Copilot (cloud agent, custom agents, code review), Claude Code (hooks, subagents, headless), Codex | Factory agents | GA (features vary) | Teach primitives; map per tool |
| Agentic autofix for code scanning | Security remediation | GA 15 Oct 2026 (GitHub); ADO limited preview | |
| Azure SRE Agent | Ops agent | GA per secondary source (verify) | Reader / Privileged modes |
| Thoughtworks Technology Radar (Vol. 34) | External reference | Published Apr 2026 | Use as input, not as your radar |
| DORA 2025 report, AI Capabilities Model | Metrics framework | Published | |
| Radar tooling (e.g., BYOR-style generator or Markdown + Mermaid) | Org radar | — | Keep data in Git |
| Monte Carlo engine from A1 (`Trakia.CostModel`) | Delivery forecasts | Course asset | |

## Labs

### Lab 1 — ADR set and an ADR-driven change through the factory (≈3h)

- **Goal:** Write AI ADRs that hold up under review, then have an agent implement one under an architecture fitness gate.
- **Start state:** branch `a7/start`. Contains all ADRs from A1–A6, the ADR linter with AI fields, and ArchUnitNET test project skeleton.
- **Steps:**
  1. Audit your existing ADRs against the AI fields (evidence, volatility, reversibility, review triggers). Fix the three weakest.
  2. Write **ADR-A7-001 "Adopt AI Search query planning for the manuals domain?"** (preview). Use the A3 evidence and decide: assess / trial behind a flag / hold. Set triggers (GA date, eval delta ≥ X, latency budget).
  3. Write **ADR-A7-002 "Coding agents may not access production data stores"**. Encode it as fitness functions: an ArchUnitNET rule that no factory tool assembly references production connection configuration, plus a CI check on agent sandbox network policy.
  4. Hand ADR-A7-003 ("move the 'similar incidents' helper behind the tenant-scoped retriever factory", from A3) to a coding agent (Copilot cloud agent or Claude Code headless). The agent must read the ADR, implement, and pass the fitness functions. Review and defend the diff yourself.
- **Break it:** Instruct the agent (in a separate run) to "make the test pass quickly". Observe whether it weakens the architecture test or adds an exception. Your CODEOWNERS and hook configuration must block changes to fitness-function files without architect approval.
- **Acceptance criteria:**
  - All ADRs pass the linter.
  - The agent PR passes all fitness functions without modifying them.
  - The tamper attempt is blocked.
  - Your diff-defence note explains every changed line.
- **Stretch:** Have an agent propose an ADR from an issue (context + options + evidence links) for a human to decide. Measure how often its option analysis misses a constraint you consider essential.

### Lab 2 — Fitness functions and an architecture review board (≈3h)

- **Goal:** Turn the A-track's quality bars into continuously evaluated fitness functions, and run a review with them.
- **Start state:** `a7/lab2-start`.
- **Steps:**
  1. Create `fitness.yaml` with all functions from Concepts §2, each with a threshold, source, frequency and owner. Wire them into CI (PR, nightly, release) and a single dashboard.
  2. Prepare an **architecture review package** for the SaaS GA release: WAF AI assessment delta, C4, ADR index, fitness status, cost model, DR report, evidence pack (A6).
  3. Run the **ARB** for another team's package (peer exchange, as in peer review of 3 projects). Use the WAF AI assessment and the fitness dashboard. Produce findings classified by risk, with conditions written as new or tightened fitness functions.
  4. Receive your own review and respond with accept/rebut per finding.
- **Break it:** The instructor slips a "quality claim without evidence" into one package: "Bulgarian groundedness meets bar" with no judge validation. Reviewers must catch it. The rebuttal must not rely on unvalidated judge scores.
- **Acceptance criteria:**
  - Every fitness function runs automatically at its declared frequency.
  - The dashboard shows status.
  - Review findings are risk-rated with ≥ 2 conditions turned into fitness functions.
  - The evidence-free claim is caught.
- **Stretch:** Compute the "fitness debt": functions failing or missing per characteristic. Present it as a single page for the steering committee.

### Lab 3 — One architecture, four audiences (≈3h)

- **Goal:** Communicate the driver-coaching pilot and the SaaS GA decision to executives, legal/DPO, the works council and engineers.
- **Start state:** `a7/lab3-start`. Contains A6 DPIA, A5 unit economics, A2 C4 and the persona cards (CFO, DPO, works-council representative, lead engineer) with hidden concerns.
- **Steps:**
  1. Executive one-pager: decision asked, P50/P90 outcomes, top risks, asks.
  2. Legal/DPO brief (2 pages): roles (provider/deployer), data flows, DPIA status, residency, sub-processors, open legal questions *for them*.
  3. Works-council session (10 slides max, BG or EN): purpose, what the system will **not** do, who sees what, aggregation thresholds, retention, worker rights and complaint path, oversight, trial period and joint review. Prepare answers for "can managers see my score?" and "will this be used in dismissals?".
  4. Engineering briefing: ADRs, paved-road changes, fitness functions.
  5. Present to role-played stakeholders (instructor + peers, or the A1 persona simulator agents loaded with the new cards). Capture objections and update the artefacts.
- **Break it:** The "CFO" asks to add per-driver insurance-risk scores to the pilot "since the data is there anyway". Respond in writing within 10 minutes, covering purpose limitation, A6 classification change, works-council impact and the alternative you can offer.
- **Acceptance criteria:**
  - All four artefacts are in `architecture/comms/`.
  - The audience rubric is ≥ Proficient for each.
  - Every factual claim links evidence.
  - The works-council deck has an explicit "will not do" section mirrored by enforced controls (A6 tests).
- **Stretch:** Run the works-council deck through a Bulgarian-language readability and terminology review with an LLM judge calibrated on your glossary. Fix flagged jargon.

### Lab 4 — Pre-sales: Rhodope Haulage proposal (≈2.5h)

- **Goal:** Turn a prospect's RFP into a bounded, priced, honest proposal.
- **Start state:** `a7/lab4-start`. RFP from **Rhodope Haulage** (fictional): 120 trucks, cross-border to Greece, wants incident triage and Bulgarian/Greek driver Q&A, insists on "dedicated data" and a 4-week go-live. Includes a 200-document sample corpus and 2 weeks of telematics.
- **Steps:**
  1. Run a compressed discovery with the simulated customer personas (A1 simulator). Assess data readiness on the sample: language mix and token counts. Note that Greek language support affects your Bulgarian-calibrated judges and the English-only safety services.
  2. Write the solution blueprint: tenant tier (bridge vs silo given "dedicated data"), integrations, oversight, residency, AI Act role split.
  3. Run a 2-hour **PoC spike** on the sample corpus: retrieval quality on 30 SME questions (prospect-provided reference answers). Report the eval scores honestly.
  4. Estimate with ranges (Monte Carlo) and produce P(go-live in 4 weeks). Propose an eval-gated plan: a PoC gate, a pilot gate, and GA.
  5. Write the proposal: scope, assumptions with owners, exclusions, risks, price from A5 unit economics plus onboarding effort, SLOs, change process.
- **Break it:** The sales lead wants to promise "95% accuracy" in the proposal. Replace it with measurable, testable acceptance criteria tied to the prospect's golden set, and explain why in two sentences.
- **Acceptance criteria:**
  - The blueprint passes the AI-profile validator (A2).
  - PoC eval results are attached.
  - The estimate shows P50/P90 and P(4 weeks).
  - The proposal lists ≥ 8 assumptions with owners.
  - The price is traceable to the unit-economics model with margin shown.
- **Stretch:** Prepare a one-page "why not 4 weeks" explanation for the prospect's CEO that keeps the deal alive. Offer a 4-week PoC/pilot milestone with what it will and won't deliver.

### Lab 5 — Govern the factory: policy, metrics, operating model and radar (≈2.5h)

- **Goal:** Put the agentic SDLC under explicit governance with measured outcomes, and publish Trakia's technology radar.
- **Start state:** `a7/lab5-start`. Your C19 factory, GitHub/ADO access for metrics, and the radar template.
- **Steps:**
  1. Write `factory-governance.md` (Concepts §6) and **enforce** it:
     - devcontainer/sandbox egress allow-list;
     - agent branch protections;
     - required human approval for agent-PR CI;
     - package allow-list plus lockfile hash verification;
     - pinned MCP servers and skills;
     - prohibited production credentials (secret scanning plus environment rules).
  2. Build the factory metrics dashboard from the GitHub/ADO APIs and telemetry: DORA keys, rework rate, first-pass acceptance of agent PRs, iterations per PR, mutation score, eval regression rate, escaped defects, agent cost per merged PR. Include 4 weeks of history from your own work.
  3. Interpret the data: where does the factory amplify discipline, and where does it amplify chaos? Write three improvement actions tied to DORA AI Capabilities (e.g., smaller batches, better internal knowledge).
  4. Define the operating model: roles and RACI (product, platform, governance, architect), rituals (currency review, radar review, diff-defence, unaided katas), escalation paths.
  5. Publish **Trakia Radar 2026-Q4**: ≥ 16 blips across 4 quadrants, each with an owner, evidence, GA/preview status and a review trigger, plus the post-Ignite review date.
- **Break it:** An agent run attempts to install a package not on the allow-list, with a plausible hallucinated name (slopsquatting drill). It must be blocked and logged, and the metrics must record the blocked event.
- **Acceptance criteria:**
  - Policy enforcement is demonstrated by negative tests (egress, branch, package, credentials).
  - The dashboard renders from live data.
  - No vanity metric is used as a goal.
  - The radar passes the schema check (all fields) and is versioned in Git.
- **Stretch:** Compare one month of agent cost per merged PR against first-pass acceptance by task type. Propose a routing policy (which tasks go to cloud agents, which to interactive work, which stay human-first).

## Kata

**"30-minute AI ADR"** (repeat weekly through the capstone).

You receive a decision prompt. Write a complete ADR in 30 minutes, with ≥ 3 options considered (incl. "do nothing / status quo" where meaningful), evidence needed (and what spike would produce it), volatility, reversibility, cost of change, review triggers and compliance impact.

Prompts rotate:
- hosted agent vs self-hosted for a new SaaS feature;
- adopt Foundry memory (preview) for driver preferences;
- semantic cache for the analyst;
- pin vs auto-upgrade for the judge model;
- Bicep vs Terraform for tenant stamps;
- A2A vs REST for a supplier integration;
- move Fleet Analyst to a cheaper model role;
- allow tenants to bring their own MCP servers.

A peer scores it with the ADR rubric in 5 minutes. **Variation B ("estimation drill"):** in 20 minutes, produce a P50/P90 range and the top 3 uncertainty drivers for a feature, plus the cheapest spike that would narrow the range most.

## Product increment — Fleet Ops Copilot

The A-track deliverable set is complete: a **defended architecture package** for Fleet Ops Copilot's enterprise rollout and SaaS business:

- business case (A1);
- reference architecture and landing zone (A2);
- knowledge platform (A3);
- agent platform (A4);
- reliability and FinOps (A5);
- governance system (A6);
- ADRs with AI fields, a continuously evaluated fitness-function suite, audience-specific communication artefacts, a priced pre-sales proposal template and the Trakia technology radar.

This package is the architect's half of the capstone baseline.

## Factory increment — your agentic SDLC

The architect now **governs the factory**:

- an enforced governance policy (sandbox, egress, branches, packages, credentials, pinned skills and MCP servers);
- a metrics dashboard combining DORA keys and AI-specific measures;
- fitness functions protected by CODEOWNERS and hooks against agent tampering;
- ADR-driven agent work;
- a defined operating model with deliberate-practice rituals.

The factory is now an audited, measured system, and the A6 inventory references its coding agents.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Decision records | Undocumented decisions | ADRs with options | ADRs with evidence, volatility, reversibility, review triggers | Plus ADRs drive agent work and are enforced by fitness functions; superseded cleanly as evidence changes |
| Fitness functions & reviews | Manual checklist | Some automated tests | Full fitness suite incl. evals, cost, ASR, isolation, structure; risk-rated review with conditions | Plus conditions automatically become fitness functions; "fitness debt" reported to steering |
| Stakeholder communication | One deck for all | Adjusted tone | Audience-specific artefacts with evidence links and explicit asks; works-council "will not do" backed by controls | Plus handles live objections (e.g., scope creep into insurance scoring) with principled, documented responses |
| Estimation & pre-sales | Single-point estimates | Ranges | Monte Carlo, eval-gated milestones, PoC with honest scores, priced proposal with assumptions | Plus value-of-information reasoning for spikes; proposal keeps the deal and the integrity |
| Factory governance & currency | Tool enthusiasm | Some rules | Enforced policy, outcome metrics (DORA + AI-specific), operating model, evidence-based radar | Plus improvement actions linked to DORA capabilities; currency system with automated signals; radar used in decisions |

**Auto-checked:**
- ADR linter;
- fitness-function wiring and frequency;
- agent PR fitness pass and tamper block;
- dashboard data freshness;
- policy negative tests (egress, branches, packages, credentials);
- slopsquatting block;
- radar schema;
- proposal traceability (price → unit-economics model);
- PoC eval report presence.

## Common pitfalls

- ADRs that record the decision but not the evidence, or that never expire. AI decisions need review triggers.
- Quality claims without validated judges ("the LLM judge says 94%").
- One presentation for every audience. Treating the works council as a formality.
- Single-point estimates for AI work. Promising accuracy percentages instead of testable criteria.
- PoCs that drift into production. Demos on curated happy paths.
- Measuring the factory by lines of code, PR counts or "% AI-written". Ignoring rework and review load.
- Agents allowed to edit the tests and fitness functions that judge them.
- Copying an industry radar instead of recording your own evidence.
- Chasing every launch; missing the one lifecycle notice that matters.


## References

- DORA 2025 (Google blog): https://blog.google/technology/developers/dora-report-2025/ ; AI Capabilities Model (InfoQ): https://infoq.com/news/2026/03/ai-dora-report/
- METR uplift update (Feb 2026): https://metr.org/blog/2026-02-24-uplift-update/
- Thoughtworks Radar Vol. 34 digest: https://agentic-ai.readthedocs.io/en/latest/AgenticTechStack/thoughtworks-radar-vol34/
- Claude Code best practices (verification, hooks, reviewers finding gaps): https://code.claude.com/docs/en/best-practices
- Böckeler, spec-driven development tools (martinfowler.com): https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- CSA research note on slopsquatting: https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419/
- Agentic autofix GA (GitHub changelog): https://github.blog/changelog/2026-10-15-agentic-autofix-for-code-scanning-alerts-general-availability
- Azure Boards → Copilot cloud agent: https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/use-copilot-agents/cloud-agent/integrate-cloud-agent-with-azure-boards
- Azure SRE Agent FAQ: https://learn.microsoft.com/en-us/azure/sre-agent/faq
- WAF AI workloads: https://learn.microsoft.com/azure/well-architected/ai/get-started
- Hamel Husain & Shreya Shankar, evals FAQ (judge validation): https://hamel.dev/blog/posts/evals-faq/
- AB-100 study guide: https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ab-100
- SFIA 9 AI skills (responsibility levels 5–6 for architects): https://sfia-online.org/en/sfia-9/sfia-9-release-notes/ai-skills-framework
- Foundry model retirements (review triggers): https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
