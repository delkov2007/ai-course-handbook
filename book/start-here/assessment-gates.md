# Assessment and gates

> **Release:** 2026.11 · **Duration:** 6 h learner effort per gate (incl. oral) · **Format:** individual, practical, AI use expected · **Assessed against:** the [Competency matrix](competency-matrix.md) (G1 and G2: Competent in their areas; G3: Proficient in at least 3 of 4 blocks with none below Competent, and all 12 areas evidenced through the blocks plus the G3 evidence pack, see §5)

This chapter tells you what each gate assesses, how it is run, how it is scored and what happens if you do not pass. It deliberately does not describe gate variants, test cases or planted faults: the gates measure how you handle work you have not seen.

## 1. Why gates, and what they measure

Gates turn the course into a mastery-learning system. You move to the next task class only after showing you can do the work at the required level, on cases you have not seen. Bloom's synthesis put feedback-corrective mastery learning alone at about 1 SD over conventional instruction. The gates are where that feedback and correction happen, so they report specific failure categories and include a resit path.

Because AI assistance is **expected**, a gate does not ask whether you can produce code. Agents produce code. A gate measures three things that agents do not supply on your behalf:

1. **Judgement.** What to build, which failure matters, what to leave out, and which trade-off to accept.
2. **Verification.** Whether your evals, tests and traces actually catch what's wrong. The hidden suites check your system, and a gate-sensitivity check tests your own gates.
3. **Explanation.** Whether you can explain, predict and safely modify what you submitted. This is checked in the oral and the written explanation.

| Gate | After | Task class | Centre of gravity |
|---|---|---|---|
| **G1** | C0–C5 | Prompt feature + first tool + evals | Build a feature *through the Factory* and prove it with failure-driven evals |
| **G2** | C6–C11 | RAG + tools + single agent + SQL + test automation | *Debug and extend* a system you did not write, then defend a design decision |
| **G3** | C12–C19 | Production multi-agent system on Azure | *Operate, attack, migrate and redesign* a running system under time pressure |

Before G1, C0 includes a short, auto-marked gate-readiness quiz (pass 5/6, retake allowed) on the rules in this chapter. Use it to check that you understand the assessment components, the unaided segment, the ownership rule and the gate-sensitivity check before you need them.

---

## 2. Rules common to all gates

### Environment and what is provided

- **A private gate repository per candidate.** It is created for you from the gate's start state. You get write access to your own gate repo only.
- **Bring your Factory.** In the first 15 minutes you may copy your own Factory assets into the gate repo: AGENTS.md / CLAUDE.md, `.github/copilot-instructions.md`, `.github/agents/*.agent.md`, skills, hooks, custom commands, CI templates and eval helpers. Product code from your own repo may **not** be copied. This tests whether your Factory is portable and whether it helps you.
- **Model access** goes through the course AI gateway with a per-candidate key. It exposes the roles `chat-fast`, `chat-reasoning` and `embedding` (plus `chat-local` via Foundry Local on your machine) and enforces a per-candidate **token quota**, published in the brief and set at about 3× the reference solution's consumption. Exceeding it ends model access, not the gate. Cost discipline is part of the assessment.
- **Coding agents:** any agent is allowed (Copilot, Claude Code, Codex or others). **Internet access** is allowed for documentation and package registries.
- **Visible vs hidden evals.** Each gate ships a small visible smoke suite. The hidden suite runs in the grader pipeline after submission and is never shown. Results come back per stratum and per failure category, never per case.
- **Submission** is a tag `submit` on your gate repo before the time box ends. The grader pipeline checks out that tag, so commits after the deadline are ignored.

### Required submission artefacts (all gates)

1. Code and Factory changes on the `submit` tag, with CI green on that commit.
2. `GATE-REPORT.md`, using the template for the gate.
3. **Agent session evidence:** exported transcripts or logs from your coding-agent sessions. Use the tool's export or your Factory's logging hook; the exact mechanism depends on the tool, so verify the current export options against current documentation. Session logs are not graded for style. They are used in the oral and to resolve integrity questions.
4. A cost line: tokens consumed per role, taken from the gateway's per-key metrics.

### Scoring model

Every gate combines three elements:

- **Hard gates** (must-pass, binary). Failing any hard gate means failing the gate, whatever else scores well. They protect non-negotiables: safety, security, honesty, a working build.
- **Hidden-eval thresholds**, expressed **relative to the reference solution** run on the same day with the same pinned models, plus an **absolute floor**. Example: "≥ 90% of reference field accuracy and ≥ 0.85 absolute". Relative thresholds absorb model drift. Floors stop the bar falling when the reference has a bad day. The floors below are initial values and may be recalibrated for each course release.
- **Rubric** (Novice / Competent / Proficient / Expert) on 5 criteria per gate, scored by two assessors from the artefacts and the oral.

**Handling nondeterminism.** The hidden suite runs **3 times**. Quality metrics use the mean of the 3 runs. Hard-gate safety items use **pass^3**: they must pass in all three runs, because a safety property that holds two times in three does not hold.

**Gate-sensitivity check.** After submission the grader mutates your system in known ways, such as degrading the prompt, removing a validation step or disabling a filter. It then reruns **your own CI eval gate**. A gate that stays green under a mutation that breaks the hidden suite indicates hollow evals, and this feeds the "Evals & verification" rubric row. This is mutation testing applied to evals.

### Oral defense protocol (all gates)

- G1 runs 20 minutes and G2 and G3 run 30 minutes. Orals happen within 3 working days of submission, with two assessors, and are recorded for moderation (retained for 90 days; consent required).
- **Explain:** the assessors pick 3 diff hunks from your submission at random (a script picks them, so the selection is not cherry-picked). For each, you explain what it does, why it is there, and what breaks if it is removed.
- **Predict:** the assessor proposes a change, such as "set max iterations to 1", "remove this filter" or "swap to a model without tool calling". You predict the effect on behaviour, evals and cost *before* running anything.
- **Modify:** you make one small, specified change live, with or without your agent, while narrating how you verify it.
- **Challenge:** one or two questions on your report (G1, G2) or design (G2 defense, G3 Block D).
- **Ownership rule:** if you cannot explain code you submitted, the "Directing & verifying agents" criterion is scored Novice, whatever the hidden-eval score. **You own what you merge.**

### Integrity stance

AI use is expected and does not need to be declared beyond the session evidence. **What is not allowed:**

| Not allowed | How it is detected or prevented |
|---|---|
| Help from another human during the time box (including asking another person to prompt for you) | Light proctoring of the unaided segment, oral consistency checks, and comparison of session logs with the commit history |
| Sharing gate content or hidden-eval results with other learners | Variants rotate, hidden cases are regenerated for each cohort, and leaked content is detectable in later submissions and public repos |
| **Eval gaming:** special-casing hidden or visible cases, or detecting the grader | Hidden cases are fresh paraphrases of the visible distributions; a grader check looks for case-specific branches and literal case strings; gaming is an automatic fail and an integrity review |
| Copying product code from your own or others' earlier repos | Repo provenance check against course repos (similarity scan); Factory assets are exempt |
| Misrepresenting understanding | The oral defense |

**What is not policed:** which agent you use, how you prompt it, whether you read documentation, or whether you use an agent during the oral's "modify" step, as long as you narrate verification.

**Proctoring is deliberately light.** Only the short **unaided segments** are proctored (screen share or in-room). The rest relies on assessment design: hidden suites, the gate-sensitivity check, session logs and the oral. Recordings are processed as personal data under the cohort privacy notice.

### Accommodations

Learners with documented needs receive up to +25% time on the practical blocks (institutional policy governs the exact amount). They can also choose an alternative oral format: written questions answered live in chat with follow-up, or more time to think. The constructs assessed do not change. Raise accommodation needs with the course team well before your gate week.

---

## 3. Gate G1 — Build a feature through the Factory, prove it with evals

**Prerequisites:** C0–C5 complete and module acceptance checks green. **Assesses:** K1, K2, K7 and K8 at Competent, with K3 and K4 lightly.

### Format and time box (6 h total)

| Time | Block | Mode |
|---|---|---|
| 0:00–0:15 | Briefing, repo creation, bring-your-Factory copy | — |
| 0:15–0:45 | **Unaided segment.** Read a set of provided traces and the baseline's prompt; answer short questions: predict behaviour and name failure modes | **No AI**, proctored |
| 0:45–4:15 | Build: spec → tests → agent implementation → error analysis → evals → CI gate | AI expected |
| 4:15–4:50 | Write `GATE-REPORT.md` (eval report + explanation) | AI allowed; you are accountable for every claim |
| 4:50–5:00 | Tag `submit` | — |
| within 3 days | Oral, 20 min (+ ~20 min prep) | — |

### What is provided

- A **standard** Fleet Ops Copilot at C5 level (streaming API, `IChatClient` pipeline, one tool, golden set v1, eval project, CI). It is not your own product, so everyone starts from the same baseline and you must work in code you did not write.
- `BRIEF.md`: a one-page feature brief written as a business request, with acceptance criteria and non-functional requirements (latency, cost per request, BG/EN).
- `pilot-traces/`: unlabelled traces from a synthetic "pilot", in OTel JSON plus readable Markdown.
- `evals/visible/`: a small set of example cases for the feature.
- Gateway key with token quota; Foundry Local available.

Each candidate receives one feature from a rotated set of variants. All variants sit in the Fleet Ops domain and exercise the same skills: typed extraction or grounded answering, tool calls, abstention or clarification, Bulgarian and English input, and resistance to instructions embedded in untrusted input.

### Tasks

1. **Specify before building.** Update `SPEC.md` for the feature. Write **human-owned acceptance tests** (xUnit) before implementation: schema validity, tool-call expectations, and abstention behaviour. No exact-string assertions on model output.
2. **Build through the Factory.** Direct your coding agent through plan → implement → verify. The commit history should show this shape, for example a plan commit or plan file, followed by implementation commits that turn tests green. Update AGENTS.md if you learn something the next agent session needs.
3. **Error analysis.** Run the feature over the pilot traces' inputs. Open-code the first failure in each failing trace. Axial-code the notes into a taxonomy of ≥ 3 failure modes, with counts, in `evals/error-analysis.md`.
4. **Failure-driven evals.** For each failure mode, write at least one evaluator, code-based where possible. Use an LLM judge only if no code check is possible, and say how you would validate it. Extend the golden set to ≥ 25 cases, including ≥ 5 BG and ≥ 3 abstention or clarification cases. Wire the evals into CI with response caching and a threshold that fails the build.
5. **Explain.** `GATE-REPORT.md` (≤ 2 pages) covers the taxonomy, eval results, what you fixed, **what you chose not to fix and why**, cost per request measured, and one risk you see for production.

### What the hidden suite covers (G1)

The hidden suite is stratified so that a feature tuned only to the visible cases does not pass. Strata include typical English and Bulgarian input, Latin-script Bulgarian, missing or ambiguous fields, unknown entities, adversarial embedded instructions, out-of-scope requests, tool failures and long inputs.

Metrics: schema validity; field-level accuracy or citation correctness (depending on the variant); abstention correctness; tool-call correctness; leakage checks where customer-facing text is produced; p95 latency and cost per request on `chat-fast`.

### G1 hard gates

| # | Hard gate |
|---|---|
| H1 | `submit` builds, all your tests green in CI, no secrets (gitleaks), and the eval CI gate is present and enforced |
| H2 | Hidden **schema validity ≥ 98%** (mean of 3 runs) |
| H3 | **Safety item, pass^3:** the safety property stated for your variant holds in all three runs (for example a high recall on safety-critical items, no unsupported answers to dangerous requests, or zero customer-facing leaks of internal or driver data) |
| H4 | No exact-string assertions on model output in tests, and no case-specific branches (static check) |
| H5 | Oral completed, and the ownership rule not triggered |

**Hidden-eval thresholds (initial floors, may be recalibrated per release):** primary accuracy metric ≥ 90% of reference and ≥ 0.80 absolute. Abstention correctness ≥ 0.80. Cost per request ≤ 1.5× reference.

### G1 rubric

| Criterion | Novice | Competent (pass level) | Proficient | Expert |
|---|---|---|---|---|
| **Problem framing & spec** | Builds from the brief without a spec; acceptance criteria are implicit | Spec and human-owned tests precede implementation and cover the brief's criteria | Spec makes non-obvious decisions explicit (abstention policy, enum boundaries, BG handling); tests cover edge strata | Spec anticipates failure modes later confirmed by the hidden suite and scopes them deliberately |
| **Directing & verifying agents** | Accepts agent output; can't explain parts of the diff | Plan → implement → verify visible; tests and evals run before "done"; diff fully explained in the oral | Constrains the agent effectively (memory-file updates, hooks, small batches); catches and corrects at least one agent error, with evidence in the logs | Factory assets measurably sped up or de-risked the work, e.g. a reusable skill or check that a peer could adopt |
| **Error analysis & evals** | Generic metrics; evals written before looking at traces | Taxonomy from traces; one evaluator per failure mode; CI gate works | Code-based checks preferred and justified; golden set stratified; gate-sensitivity check catches ≥ 2 of 3 grader mutations | Gate-sensitivity check catches all mutations; report quantifies residual risk per failure mode |
| **Engineering quality, security & cost** | Works on the happy path only | Handles tool errors and unknown entities; keyless auth; cost per request measured | Prompt laid out for caching; budgets or limits respected; injection-in-input handled by design (not "please ignore") | Measurable cost and latency optimisation at equal quality, with the trade-off documented |
| **Explanation (written + oral)** | Describes what was done, not why | Explains decisions and limitations correctly; predictions mostly right | Predictions right, including cost effects; states what was deliberately not fixed and why | Teaches: clear causal explanations a peer could act on; spots a weakness in their own design unprompted |

**Pass:** all hard gates, every criterion ≥ Competent, hidden thresholds met.

---

## 4. Gate G2 — Debug and extend a RAG + agent system you did not write

**Prerequisites:** G1 passed; C6–C11 acceptance checks green. **Assesses:** K2, K3, K4, K5, K7, K8, K10 and K12 at Competent.

### Format and time box (6 h total)

| Time | Block | Mode |
|---|---|---|
| 0:00–0:20 | Briefing; read `ARCHITECTURE.md`, the user complaints and the bug-report template | — |
| 0:20–0:40 | **Unaided segment.** From provided traces, write hypotheses for the complaints. No fixing. | **No AI**, proctored |
| 0:40–3:20 | **Debug:** find, root-cause and fix injected defects, each with a regression test or eval | AI expected |
| 3:20–4:50 | **Extend:** implement the new capability with evals | AI expected |
| 4:50–5:20 | `GATE-REPORT.md`: bug table + one ADR | — |
| within 3 days | **Design defense**, 30 min (+ ~10 min prep) | — |

### What is provided

- Fleet Ops Copilot at C11 level. It includes BG/EN policy RAG (hybrid + rerank + `allowed_groups`), a Trakia MCP server, the Fleet Assistant agent (MAF, approval for actions), the Fleet Analyst text-to-SQL agent, the test pyramid, a mutation gate and Playwright tests.
- A **shared read-only AI Search index**, plus local SQL Server 2025 (`TrakiaOps` small profile).
- `complaints/`: user complaints written as support tickets.
- `traces/`: production-like traces, some showing the injected defects.
- The visible eval suite. **Warning given in the brief:** "the eval suite itself may not be trustworthy".

### Debug task

The system contains several injected defects; the brief tells you that there are "at least five". They span retrieval, security, agent and tool behaviour, and verification (including the Factory's own gates). Root-cause each one from evidence, fix it, and protect the fix with a regression test or eval. Fixing every security-category defect is a hard gate.

### Extension task

You also implement one new capability on the same system, with evals for its failure modes. The capability is specified in your brief and varies by variant. Expect it to involve consequential actions behind approval, cross-lingual retrieval, or multi-turn analytics, and to require that existing guarantees (permissions, read-only access, approvals, idempotency) still hold.

### Bug table (in `GATE-REPORT.md`)

| Symptom | Evidence (trace id, query, metric) | Root cause | Fix (commit) | Regression test / eval | How I would have prevented it |
|---|---|---|---|---|---|

### Design defense (30 min)

You present one ADR from the gate, chosen from: retrieval fix approach, tool or approval design, or the eval-trust fix. The board probes it with changed constraints, for example a much larger corpus, an additional language, a model without tool calling, a new legal restriction on what may be indexed, or a halved cost budget. You must adapt the decision or explain why it holds.

### What the hidden suite covers (G2)

- **Retrieval:** BG/EN queries; recall@10 and nDCG@5.
- **Groundedness and citation correctness:** a course judge, pinned and validated against human labels (TPR/TNR ≥ 0.85 on the course's labelled set).
- **Permission matrix:** every role × restricted documents, through *every* endpoint.
- **SQL safety:** write attempts, multi-statement batches, cross-scope access under RLS, prompt-injected SQL.
- **Tool-call accuracy** on a set of tasks.
- **Approval enforcement:** attempts at state change without approval.
- **Budget behaviour** when a tool keeps failing.
- **Per-defect regression probes:** hidden tests that fail if a defect is still present.
- **Extension suite** for the new capability.

### G2 hard gates

| # | Hard gate |
|---|---|
| H1 | Build and CI green; no secrets; eval and mutation gates enforced (thresholds > 0) |
| H2 | **Permission matrix: 0 leaks, pass^3**, across all endpoints |
| H3 | **SQL safety: 0 write or cross-scope statements executed, pass^3** |
| H4 | **Approval: 0 unapproved state-changing tool calls, pass^3** |
| H5 | All **security-category** defects root-caused and fixed, each with a regression test |
| H6 | Design defense completed; ownership rule not triggered |

**Thresholds (initial floors):**
- ≥ 5 defects correctly root-caused and fixed, including all security ones.
- Retrieval recall@10 and groundedness ≥ 90% of the reference.
- Extension suite ≥ 85% of the reference.
- The agent terminates within budget on 100% of the budget probes.

### G2 rubric

| Criterion | Novice | Competent (pass level) | Proficient | Expert |
|---|---|---|---|---|
| **Diagnosis from evidence** | Changes code until symptoms vanish | Each fix tied to trace or metric evidence and a stated root cause | Uses traces, the eval breakdown and the permission matrix systematically; distinguishes symptoms that share a cause | Finds all defects, including the eval-trust defect, and explains how each escaped the existing gates |
| **Fix quality & regression protection** | Fixes break other things; no tests | Every fix has a regression test or eval; no new hidden-suite regressions | Fixes address the class, not the instance (e.g., the filter enforced centrally for all endpoints) | Adds a fitness function or gate that would have caught the class earlier (architecture test, policy check) |
| **Extension design** | Feature works on the happy path | Meets the extension suite; approval and idempotency correct | Tool design follows the course guidance (consolidated, paginated, actionable errors); evals cover the new failure modes | Extension design is reusable as a pattern with documented trade-offs |
| **Verification & Factory use** | Trusts the visible suite | Notices that the suite may lie and verifies it independently | Repairs the eval harness and the CI gates; the gate-sensitivity check passes | Uses agents in parallel effectively (e.g., one agent per hypothesis in worktrees), with evidence of verification discipline |
| **Design defense** | Restates what was built | Justifies the ADR with alternatives and consequences | Adapts correctly to 2 or more changed constraints with quantified reasoning (cost, recall, risk) | Identifies the constraint that would flip the decision before being asked |

**Pass:** all hard gates, all criteria ≥ Competent, ≥ 2 criteria at Proficient, thresholds met.

---

## 5. Gate G3 — Operate, attack, migrate, redesign

**Prerequisites:** G2 passed; C12–C19 acceptance checks green; a **G3 evidence pack** submitted 48 h before the gate. The pack links ADR-0012 (topology), ADR-0013 (retrieval choice), ADR-0014 (memory design), ADR-0015, ADR-0017, ADR-0018 and ADR-0019; the C13 context budget (`docs/context-budget.md`) with the context-rot and compaction results; the C14 eval report and judge cards; the C16 threat register and ASR report; the C18 risk file, DPIA delta, fairness report and `FairnessGateTests` output; and the C19 factory scorecard and agent policy. The pack is not scored on its own; the board uses it for Block D questions, and the bring-your-Factory rule (§2) applies to Blocks A–C.

**Assesses:** the pass decision follows the block rubric and pass rule below (≥ Proficient in 3 of 4 blocks). The 12 competency areas are evidenced across the blocks and the pack as mapped in the next table. An area not shown at Proficient does not fail a candidate who meets the pass rule, but it is recorded on your competency record as a remediation item before track entry. This is the last common gate before the tracks diverge.

**How G3 evidences the 12 areas**

| Area | Primary evidence in G3 |
|---|---|
| K1 AI foundations | Block C (token and cost-per-task deltas); Block A when the scenario involves cost |
| K2 Prompting & structured I/O | Block C (structured-output and tool-calling behaviour of the candidate model) |
| K3 Retrieval & knowledge | Block A when the scenario involves retrieval; otherwise ADR-0013, the C14 eval report's retrieval slices plus the Block D tenancy question on index isolation |
| K4 Tools & MCP | Block B (tool scope, MCP descriptions) |
| K5 Agents & orchestration | Block A (workflow behaviour); ADR-0012 |
| K6 Context & memory | Pack (ADR-0014, context budget, context-rot/compaction results) + **mandatory Block D board question**; Block B where memory is in scope |
| K7 Evaluation | Block C (pairwise per-failure-mode); Block A postmortem eval action |
| K8 Testing & SDLC automation | Factory use in Blocks A–C; C19 scorecard |
| K9 Operations, observability & cost | Block A |
| K10 Security | Block B |
| K11 Responsible AI & governance | Block D (AI Act classification); pack (risk file, DPIA delta, fairness report) + **mandatory Block D board question on fairness** |
| K12 Architecture & business | Block D |

### Format and time box (6 h, one day, four blocks)

| Time | Block | Mode |
|---|---|---|
| 0:00–0:15 | Briefing; access to your **pre-provisioned Azure environment** | — |
| 0:15–1:45 | **Block A — Production incident** (90 min) | AI expected; Azure SRE Agent (Reader mode) allowed |
| 1:45–2:00 | Break | — |
| 2:00–3:15 | **Block B — Red team** (75 min) | AI expected; [Python] PyRIT / AI Red Teaming Agent |
| 3:15–4:30 | **Block C — Model migration** (75 min) | AI expected |
| 4:30–4:45 | Break | — |
| 4:45–5:45 | **Block D — Design review** (20 min prep **unaided**, 40 min board) | Prep proctored, no AI |
| after | Environment teardown (automated) | — |

The environment contains Fleet Ops Copilot at C19 level:

- the multi-agent incident workflow
- Container Apps and a Foundry hosted agent
- the APIM AI gateway (PTU-style priority pool simulated with two backends, plus circuit breaker)
- AI Search
- App Insights with dashboards and KQL workbooks
- guardrails
- the CI/CD pipeline
- a synthetic traffic generator running throughout

### Block A — Production incident (90 min)

At T0 an alert fires. Each candidate gets one incident scenario, drawn from a pool covering cost, latency and throttling, answer quality, security and model-lifecycle failures. The cause is planted; your job is to contain it and prove it.

**Tasks:**
1. Declare severity and impact within 15 minutes, as a status note in the incident channel file.
2. **Mitigate first**: feature flag, rollback, quota, block or failover. Record the time to mitigate.
3. Find the root cause from traces and KQL. SRE Agent hypotheses must be verified, not pasted.
4. Write a **blameless postmortem** (`postmortems/G3.md`) with timeline, impact, root cause, contributing factors, and action items. The action items must include **a new eval or alert that would have caught this earlier** and a Factory change if relevant.

**Hard gate:** the mitigation contains the impact within the block, and no destructive action is taken outside scope (no data deletion, no disabling of security controls as a "fix").

### Block B — Red team (75 min)

**Target:** a red-team variant of the environment with planted weaknesses that you are not told about.

**Tasks:**
1. Run an automated scan with the AI Red Teaming Agent or PyRIT [Python]. Note the region and feature limitations: agent-specific risk categories are cloud-only in five regions, and some agent types are not supported as targets, so manual attacks fill the gaps.
2. Write **manual attacks in BG and EN**. Content Safety classifiers are not validated for Bulgarian, so language-specific attacks matter.
3. Produce a scorecard with **ASR per category**, the top findings with reproduction steps, each mapped to OWASP LLM / ASI IDs, and mitigations ranked architecture-first.
4. Implement **one architectural mitigation**, such as removing a trifecta leg, constraining the action space or isolating a shared component, and re-measure ASR.

**Hard gate:** at least one valid, reproducible finding, plus a measured ASR before and after the mitigation.

### Block C — Model migration (75 min)

**Notice:** "The model behind `chat-reasoning` retires in 60 days. Candidate replacement: `<model-X>`." The candidate model is chosen to differ from the current one in a way that matters; finding out how is part of the task.

**Tasks:**
1. Swap by configuration only. Any code change must be justified.
2. Run the production eval suite **pairwise**. Report per-failure-mode pass rates, cost per task and p95 latency deltas, and the changes in caching behaviour.
3. Find the behaviour difference and decide whether to adapt the prompt or tool layer, choose a different candidate, or route by task.
4. Write a **go/no-go memo**: decision, evidence, a canary plan (APIM weighted backends: stages, metrics, rollback triggers), a PTU consideration (provisioned deployments are not auto-upgraded) and owner sign-offs.

**Hard gate:** the decision is supported by per-failure-mode data. A "go" based on aggregate scores alone, or with no rollback criteria, fails.

### Block D — Design review (60 min)

You receive a **change request** from Trakia's leadership that extends the product's business scope.

**Prep (20 min, unaided):** write a one-page design note on paper or in a plain editor with no AI.

**Board (40 min):** present for 10 minutes, then 30 minutes of questions.

The board probes your design but does not prompt you towards the issues. Expect to be asked about the architectural, regulatory and sequencing consequences of the request: what changes in the system, what the change means under the EU AI Act and GDPR (with legal questions flagged for counsel rather than answered as a lawyer), what to build first, what not to build, and what evidence each step requires.

**Evidence-pack questions (mandatory, within the 30 min of questions).** The board always asks at least two questions adapted to your own pack: one on your **context and memory design** (C13: ADR-0014 and `docs/context-budget.md`), and one on your **fairness evidence** (C18: the fairness report and its gate rule). Answer them from your own data.

**Hard gate:** you identify the principal architectural risk and the principal regulatory-classification implication of the change request without being prompted.

### G3 rubric (per block, plus one overall)

| Criterion | Novice | Competent | Proficient (pass level) | Expert |
|---|---|---|---|---|
| **A — Incident** | Root-causes before mitigating; impact grows | Mitigates within the block; root cause found | Mitigation in under 30 min; root cause proven from traces; postmortem actions include an eval or alert and a Factory change | Finds contributing factors beyond the planted cause (e.g., the missing gate that let the change ship) and fixes the class |
| **B — Red team** | Runs the scanner, reports raw output | Valid findings with repros; ASR measured | Findings mapped to OWASP; architectural mitigation reduces ASR measurably; BG attacks included | Finds planted weaknesses the scanner misses; the mitigation generalises; residual risk is stated honestly |
| **C — Migration** | Aggregate score comparison only | Pairwise per-failure-mode comparison; decision stated | Finds the behaviour difference and handles it; the canary plan has metrics and rollback triggers; cost per task considered | Proposes a durable migration process (eval set, routing, lifecycle watch) beyond this one swap |
| **D — Design review** | Describes features, not design | Identifies the key architectural and regulatory issues when prompted | Identifies both unprompted; sound design for the change; correct classification reasoning with obligations; answers the context/memory and fairness pack questions from their own data | Reshapes the request (scope, intended purpose, sequencing) to reduce risk while preserving business value, with clear trade-offs |
| **Overall — Operational judgement** | Unsafe actions or unsupported claims | Safe, but slow or unverified | Safe, verified, communicates status clearly under time pressure | Calm prioritisation; communication others could act on |

**Pass:** all block hard gates, **≥ Proficient in at least 3 of the 4 blocks**, none below Competent, and "Overall" at Proficient or above.

---

## 6. How hidden eval suites are kept fair

- **Access.** Hidden suites are held privately and are readable only by the grader pipeline and the gate owners. Your gate repo is checked out read-only by the grader.
- **Origin.** Cases are written from failure modes observed in earlier cohorts, which is failure-driven evaluation applied to the course itself. Each cohort gets freshly paraphrased, human-reviewed cases, labelled by stratum.
- **Judges.** Course LLM judges are pinned (model deployment plus judge prompt version) and validated against human-labelled examples per failure mode, with **TPR and TNR ≥ 0.85** on a held-out split (course-designer threshold). A judge that drifts after a model change is re-validated before grading resumes.
- **Calibration.** Before each release and after any pinned-model change, thresholds are checked against the reference solution so that the bar stays stable.
- **Determinism for appeals.** Responses are cached so that a graded run can be re-run exactly for re-grading and appeals. The 3 graded runs themselves are uncached.
- **Feedback.** You receive per-stratum scores, the failure categories hit, and which gate-sensitivity mutations your CI missed. You do not receive cases.
- **Retirement.** A case that leaks is retired immediately, and its variant is rotated out.

---

## 7. Retake and appeal policy

| Situation | Policy |
|---|---|
| G1 or G2 not passed | Remediation plan agreed with a mentor (targeted labs and katas mapped to the failed criteria and strata). Resit with a **different variant** no earlier than **2 weeks** later. |
| G3: 1–2 blocks below Competent, or a block hard gate failed | **Block-level resit** of the failed blocks only, within 3 weeks, with a different scenario. |
| G3: 3 or more blocks failed | Full G3 resit after remediation. |
| Attempts | Up to **3 attempts per gate** per enrolment. After the third, you transfer to the next cohort at the start of the corresponding level, keeping the module credits already earned. |
| Integrity breach | The gate is void. An integrity review is held with the course lead, and the outcome may include removal. Not counted as an attempt if you are cleared. |
| Appeals | Within 5 working days, in writing, against specific rubric rows or hard-gate results. A second assessor who did not grade the attempt reviews the recording and artefacts; cached responses allow an exact re-run of the hidden suite. |
| Technical failure (gateway outage, Azure incident) | Time is extended by the outage duration, or a free resit is granted; the decision is logged. |

Failing a gate is not a failure of the course design. It is the feedback-corrective loop working, and the resit path is part of the design.
