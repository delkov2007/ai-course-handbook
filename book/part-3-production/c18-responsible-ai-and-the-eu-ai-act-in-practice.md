# C18 — Responsible AI & the EU AI Act in practice

> **Level:** 3 — Production systems (Advanced) · **Duration:** 8h (theory 45% / labs 55%) · **Prerequisites:** C10 (Fleet Analyst over telematics), C12 (incident workflow, HITL), C14 (evals, red-team report), C15 (tracing, retention), C16 (threat register), C17 (deployment, Teams channel) · **Volatility:** High (Digital Omnibus just changed the timeline; Commission guidelines, codes of practice and Bulgarian national designations are still arriving)

> **Disclaimer.** This module teaches builders how to engineer *for* regulatory requirements and how to produce evidence counsel can use. It is **not legal advice**. Classifications produced in the labs are training exercises on a fictional company. Real systems need review by qualified legal and data-protection professionals, and the regulatory texts in force on the day.

## Why this matters

Trakia's fleet managers loved the C10 Fleet Analyst. Within a week, HR asked for a monthly "driver safety ranking" built from harsh braking, speeding and idling events. They want it to "inform bonuses and, where needed, disciplinary conversations", and they want the copilot to draft the coaching letters. That request moves Fleet Ops Copilot from a convenient internal assistant into **Annex III, point 4 of the EU AI Act** (employment and workers management: monitoring and evaluating the performance and behaviour of workers). It is also squarely GDPR employee monitoring and profiling territory. The same week, a sales lead wants a dashcam vendor's "driver stress and anger detection" add-on. That runs into the Act's **prohibition on emotion recognition in the workplace**.

Teams without this skill fail in one of two ways. Some ignore regulation until a works council, the data-protection authority or a large customer's procurement questionnaire stops the rollout. Others drown in legal prose and freeze. Builders who can classify a feature in an afternoon, design it to stay *out* of a high-risk class where that is legitimate, and otherwise produce the risk file, logs, oversight UI and transparency notices as normal engineering artefacts become the people the organisation trusts with AI.

The good news for engineers is that the Act's high-risk requirements (Arts. 9–15: risk management, data governance, documentation, logging, transparency, human oversight, accuracy/robustness/cybersecurity) map almost one-to-one onto practices you already built in C14–C17: evals, traces, threat models, red teaming, HITL. The **Digital Omnibus on AI (Regulation (EU) 2026/1744)** moved the Annex III deadline to **2 December 2027**. That is a design window, not permission to wait.

## Learning outcomes

1. **Classify** each Fleet Ops Copilot feature by AI Act risk tier (prohibited, high-risk Annex III/Annex I, Art. 50 transparency, minimal) and **identify** Trakia's role (provider, deployer or both), with article-level justification.
2. **Apply** the post-Omnibus timeline to a feature roadmap and **state** which obligations bind Trakia today versus from 2 Dec 2027.
3. **Produce** a risk file skeleton for a high-risk feature, mapping Arts. 9–15 to concrete evidence artefacts (eval reports, traces, threat register, oversight design).
4. **Design** a feature variant that legitimately avoids high-risk classification, and **argue** the trade-off in an ADR.
5. **Integrate** GDPR duties (lawful basis, DPIA, minimisation, Art. 22, retention of logs that contain personal data) with AI Act logging and oversight requirements.
6. **Execute** a fairness/bias test on driver-scoring outputs with exposure-normalised metrics and confidence intervals, and **interpret** confounders.
7. **Implement** human-oversight UX that resists automation bias, and **measure** it (override rate, seeded-error detection).
8. **Write** Art. 50 disclosures, a worker information notice and a Microsoft-style Transparency Note for Fleet Ops Copilot.

## Concepts

### 1. The AI Act's structure in one page

The AI Act (Regulation (EU) 2024/1689) regulates **AI systems** by use-based risk and **general-purpose AI (GPAI) models** by capability:
- **Prohibited practices (Art. 5)**: e.g., manipulative or exploitative techniques causing significant harm, social scoring, untargeted facial-image scraping, **emotion recognition in the workplace and education (except for medical or safety reasons)**, and biometric categorisation inferring sensitive traits.
- **High-risk systems (Art. 6)**: either safety components of products under Annex I sectoral legislation, or uses listed in **Annex III** (biometrics, critical infrastructure, education, **employment and workers management**, access to essential services, law enforcement, migration, justice/democracy).
- **Transparency obligations (Art. 50)** for certain systems regardless of risk tier.
- **GPAI model obligations (Chapter V)** on model providers.
- Everything else is **minimal risk** (voluntary codes).

*(The article structure above is background knowledge of the 2024 text; verify article numbering against the consolidated text after the Omnibus amendments.)*

**Roles.** The **provider** develops a system (or has it developed) and places it on the market or puts it into service *under its own name*. The **deployer** uses it under its authority. Importers and distributors also have roles. A deployer becomes a provider (Art. 25) when it puts its name or trademark on a high-risk system, substantially modifies it, or changes its intended purpose so that it becomes high-risk. **Trakia building Fleet Ops Copilot in-house for its own use is both provider and deployer.** When Trakia sells the product to other fleets (A-track), it is the provider and its customers are deployers.

### 2. The timeline after the Digital Omnibus

Regulation (EU) 2026/1744 was published in the OJ on 24 Jul 2026 and **entered into force on 27 Jul 2026**.

| Date | What applies | Source confidence |
|---|---|---|
| 2 Feb 2025 | Prohibitions (Art. 5); AI literacy (Art. 4) | Background, stable |
| 2 Aug 2025 | GPAI model obligations; governance; penalties framework | Background, stable |
| **2 Aug 2026** | **Art. 50 transparency obligations** | Verified (Omnibus sources) |
| **2 Dec 2026** | Deadline for Art. 50(2) machine-readable marking by generative systems **already on the market before 2 Aug 2026**; **new prohibition** on AI generating non-consensual intimate imagery/CSAM (or lacking reasonable safeguards against it) | Verified |
| 2 Aug 2027 | Each Member State must have ≥1 national AI regulatory sandbox; legacy GPAI models compliance (background) | Sandbox verified; legacy GPAI background |
| **2 Dec 2027** | **Annex III high-risk obligations** (was 2 Aug 2026) | Verified |
| **2 Aug 2028** | **Annex I product-embedded high-risk** obligations | Verified |

Other Omnibus changes builders should know:
- **AI literacy (Art. 4)** is softened to a duty to *support* literacy measures, with no mandated level; the Commission will publish examples.
- **Small mid-caps** (new Art. 3(14b)) get SME-style privileges: simplified technical documentation, proportionate QMS, lower fine caps.
- **High-risk EU database registration is reinstated** in streamlined form.
- **New Art. 4a** permits strictly necessary processing of special-category data for bias detection and correction under safeguards, now extended beyond high-risk systems.
- The **AI Office** gets exclusive supervision of AI systems built on a GPAI model by the same provider or group (Art. 75), plus fining powers.

The broader "Digital Omnibus" amending GDPR, NIS2 and the Data Act was still in the legislative process as of July 2026. **Do not assume GDPR changes.**

Penalties (background, verify): up to €35M or 7% of worldwide turnover for prohibited practices, €15M or 3% for most other infringements; SMEs (and now small mid-caps) pay the lower of the two.

### 3. Prohibited practices that matter to a logistics company

**Emotion recognition at work.** Art. 5(1)(f) prohibits AI systems that infer emotions of natural persons in the workplace, except for medical or safety reasons. The Act's recitals distinguish *emotions* from *physical states*. Detecting **fatigue** of professional drivers to prevent accidents is given as an example of what is *not* emotion recognition. *(Recital wording from background knowledge: verify the exact recital text before teaching.)* For Trakia:
- an in-cab drowsiness alert that warns the driver in real time is plausibly outside the prohibition;
- a vendor feature scoring "stress", "anger" or "frustration" from the driver's face or voice is emotion recognition in the workplace;
- the "safety reasons" exception is narrow. Using emotion scores for HR evaluation is not a safety reason. Treat any such feature as **stop and escalate to counsel**.
- Facial images are also **biometric data** under GDPR Art. 9, which brings its own prohibition-with-exceptions.

**Social scoring and manipulation** are unlikely in Trakia's roadmap. Still, a "driver trust score" reused across unrelated contexts (housing for drivers on long routes, loans from a partner bank) is the shape of social scoring, so name it as a design smell.

### 4. High-risk: Annex III point 4 and the Art. 6(3) filter

**Annex III point 4** covers AI systems intended to be used (a) for recruitment/selection, and (b) to make decisions affecting terms of work relationships, promotion or termination, to **allocate tasks based on individual behaviour or personal traits**, or to **monitor and evaluate the performance and behaviour** of persons in work relationships *(paraphrased from background knowledge; verify the exact annex wording)*.

**Art. 6(3)** lets an Annex III system escape high-risk status if it poses no significant risk of harm, e.g., it performs a narrow procedural task, improves the result of a previously completed human activity, detects decision patterns without replacing human assessment, or performs a preparatory task. **But an Annex III system that performs profiling of natural persons is always high-risk.** The provider must document the assessment *before* placing the system on the market.

Applied to Trakia:

| Feature | Classification (training answer) | Why |
|---|---|---|
| Ask Fleet Ops (policy/manual RAG, staff) | Minimal + Art. 50(1) disclosure | No Annex III use; users interact with AI |
| Incident report extraction (C3) | Minimal | Structuring text; human handles incident |
| Fleet Analyst – vehicle/route analytics | Minimal | About vehicles and routes, not evaluating individuals |
| Fleet Analyst – per-driver queries by fleet managers | **Grey zone** | Becomes Annex III 4(b) when used to evaluate drivers; intended purpose and controls decide |
| **Driver Coaching Insights** (per-driver risk score → bonuses/discipline) | **High-risk, Annex III 4(b)** | Monitors and evaluates worker behaviour; profiling, so 6(3) is unavailable |
| Shift/route allocation using individual behaviour scores | **High-risk, Annex III 4(b)** | Allocates tasks based on individual behaviour |
| Customer notification drafting (C12) | Art. 50 (generated text) assessment | See §6 |
| Driver voice assistant (D3) | Art. 50(1) disclosure | Interaction with AI |
| Fault-code classifier at depots (D1) | Minimal | Vehicles, not people |
| Dashcam "stress/anger" add-on | **Prohibited** (workplace emotion recognition) | §3 |
| Fleet Ops sold to other fleets (A-track) | Trakia = provider; customers = deployers | Art. 3/25 roles |

**Design lever.** The *intended purpose* is defined by the provider and enforced technically. A "Driver Coaching" variant that gives the **driver** (not HR) their own trend data and coaching tips, with **no per-driver output to management** (only depot aggregates with k-anonymity ≥ 10) and contractual and technical bars on use for employment decisions, is a legitimate way to stay out of 4(b). If HR insists on individual evaluation, accept high-risk and build the full risk file. **Never** choose the label first and then retrofit the argument. Lab 2 makes you write this ADR.

### 5. What high-risk means for builders: Arts. 9–15 as engineering

| Article | Requirement | Fleet Ops evidence artefact |
|---|---|---|
| 9 Risk management system | Continuous, lifecycle, foreseeable misuse | Threat register (C16) + harms register; residual risk sign-off |
| 10 Data & data governance | Relevant, representative, examined for bias | Data sheet for telematics features; bias test (Lab 3); Art. 4a basis if special-category data is used |
| 11 + Annex IV Technical documentation | System description, design, evals, monitoring | `docs/ai-act/technical-file/` generated from ADRs, eval reports, model/agent versions |
| 12 Record-keeping | Automatic logs over the lifetime | OTel traces + immutable decision log (score, inputs ref, model/prompt version, reviewer, outcome) |
| 13 Transparency & instructions for use | Deployers can interpret output | Instructions for use + Transparency Note (Lab 4) |
| 14 Human oversight | Understand, avoid automation bias, override, stop | Oversight UI + honeypot metrics (Lab 3) |
| 15 Accuracy, robustness, cybersecurity | Declared metrics; resilience incl. adversarial | C14 eval suite with declared thresholds; C16 ASR report |
| 17 QMS | Procedures, change management | The factory (C19): gated pipeline, CODEOWNERS, release records |
| 72–73 Post-market monitoring, serious incidents | Monitor in production; report | Foundry continuous eval + incident runbook |

Conformity assessment for most Annex III systems is internal control (Annex VI) *(background; verify)*, followed by EU declaration of conformity, CE marking and registration in the EU database (reinstated, streamlined).

**Deployer duties (Art. 26)** also bind Trakia as the user of its own system: use per instructions; assign human oversight to competent, trained people; ensure input data is relevant; monitor and report; **keep logs for at least six months**; and **inform workers' representatives and affected workers before putting a high-risk system into service at the workplace**. A fundamental-rights impact assessment (Art. 27) targets public bodies, private entities providing public services and certain credit/insurance uses, so it is probably not Trakia's case *(verify scope)*. A DPIA under GDPR will be required regardless (§7).

### 6. Art. 50 transparency, binding now

From **2 Aug 2026**:
- **50(1)** Providers must design systems that interact with people so those people are informed they are interacting with AI, unless that is obvious from context. Fleet Ops chat, the Teams bot and the driver voice assistant need a clear disclosure in BG and EN.
- **50(2)** Providers of AI systems generating synthetic audio, image, video or text must mark outputs in a machine-readable format, detectable as AI-generated, as far as technically feasible. There are exceptions for assistive editing functions and outputs that do not substantially alter the input. Legacy systems on the market before 2 Aug 2026 have until **2 Dec 2026**.
- **50(3)** Deployers of emotion recognition or biometric categorisation must inform exposed persons. Trakia should have none (§3).
- **50(4)** Deepfake disclosure; AI-generated text *published to inform the public on matters of public interest* must be disclosed unless it underwent human review and someone holds editorial responsibility.

Customer notification emails drafted by the C12 workflow and approved by a dispatcher are the interesting case. Arguments exist that human-reviewed drafting is assistive, and the machine-readable marking techniques for *text* are immature. Engineering answer: apply a visible footer ("Drafted with AI assistance, reviewed by Trakia dispatch") plus a machine-readable marker (an email header and a metadata field in the notification record), and document the reasoning. Track the Commission's guidelines and code of practice on marking *(verify current status)*.

### 7. GPAI and the GDPR interplay

**GPAI.** Obligations (technical documentation, copyright policy, training-data summary; systemic-risk duties for the largest models) fall on *model providers* such as OpenAI, Anthropic and Microsoft, and have applied since 2 Aug 2025. Trakia is a *downstream provider* of an AI system and needs the model provider's documentation for its own technical file. Fine-tuning (D1) may, beyond Commission-defined thresholds, make Trakia a provider of a *modified* GPAI model *(verify the current Commission guidelines threshold)*.

**GDPR runs in parallel and usually bites first:**
- **Lawful basis.** Consent is rarely valid in employment. Expect legitimate interests (with a balancing test) or legal obligation (tachograph/driving-time rules), together with national employment law on employee monitoring.
- **DPIA (Art. 35).** Systematic monitoring of employees, evaluation/scoring and innovative technology make a DPIA effectively mandatory for Driver Coaching Insights. Reuse the AI Act risk file to avoid duplicate work, but keep the DPIA as its own document.
- **Art. 22.** Decisions based *solely* on automated processing with legal or similarly significant effects (bonus cuts, dismissal) are restricted. Meaningful human involvement must be real, which ties directly to Art. 14 oversight design.
- **Minimisation and purpose limitation.** Use pseudonymised driver IDs in the AI path, no names in prompts, aggregate where possible, and no repurposing of safety telematics for productivity scoring without a fresh assessment.
- **Logs containing personal data.** AI Act logging (≥6 months for deployers of high-risk systems) meets GDPR storage limitation. Resolve this by logging *structured decision events* (pseudonymous IDs, feature values, model/prompt versions, reviewer, outcome) for the required retention, keeping OTel **content capture off** in production (C15) or redacted, with separate shorter retention for any prompt/response content. Record this in the DPIA and the record of processing.
- **Rights.** Access requests include AI-derived scores and coaching text. Erasure must reach memory stores (C13) and eval datasets built from production traces.
- **Residency.** Data Zone EU deployments (C17).
- **Art. 4a AI Act** allows strictly necessary special-category processing for bias detection with safeguards. It is a narrow door, not a licence to collect ethnicity "for fairness".

### 8. Bulgaria

One law-firm tracker (Jul 2026) names the **Commission for Personal Data Protection (КЗЛД / CPDP)** as Bulgaria's primary AI supervisory authority. It names the Executive Agency for Accreditation for notified-body accreditation and BNB/FSC as sector regulators. **This is unconfirmed by official Bulgarian sources.** Instructors must check the State Gazette (Държавен вестник), the CPDP site and the Ministry of e-Government before each cohort, and present the national picture as "status as of <date>". Employee-monitoring rules under Bulgarian labour law and the role of workers' representatives should be confirmed with Bulgarian counsel; do not improvise them in class.

### 9. Responsible AI beyond compliance

The **Microsoft Responsible AI Standard (v2)** organises goals under six principles: Accountability, Transparency, Fairness, Reliability & Safety, Privacy & Security, Inclusiveness. Its practical artefacts are the **Impact Assessment**, **Transparency Notes** (Microsoft publishes one per service, e.g., for Azure OpenAI and Content Safety, and you write one for your system) and the **HAX Toolkit** guidelines for human-AI interaction *(verify whether the Standard has been revised since v2)*. These are useful precisely where the law is silent: Bulgarian-language quality gaps, inclusiveness for drivers with limited literacy, and the dignity of coaching language.

**Fairness testing for driver scoring:**
- **Define groups you can lawfully use:** depot, experience band, age band, contract type (employee vs subcontractor), primary language. Nationality is a discrimination-sensitive attribute; ethnicity is special category (Art. 4a only).
- **Normalise by exposure:** harsh-braking events per 1,000 km, stratified by **route type** (mountain passes on the Plovdiv–Smolyan routes, Sofia urban, Varna port), vehicle age and weather. Raw disparities without stratification mostly measure the routes a depot drives.
- **Metrics:** flag rate per group (demographic parity ratio), and against expert-labelled ground truth (a sample of events reviewed with dashcam footage) the **false positive rate parity** and FNR parity (equalized-odds style). Report bootstrap 95% CIs; small groups (e.g., 23 subcontractors at Varna) give wide intervals and must be reported as inconclusive, not as "fair".
- **Generated text:** run counterfactual tests on coaching letters. Keep the telemetry identical, vary only non-relevant context, and judge tone and severity with a calibrated binary judge (C14). Better still, keep attributes out of the prompt entirely (minimisation is also a fairness control).
- Fairlearn **[Python]** offers these metrics; the lab provides a C# implementation so the gate runs in `dotnet test`.

### 10. Human oversight that actually oversees (Art. 14)

Oversight persons must be able to understand capacities and limitations, remain aware of **automation bias**, correctly interpret output, decide not to use it or override it, and intervene or stop the system. Design patterns:
- **Evidence-first review:** show the underlying events (time, location on map, speed trace, road type) before the score. Show data-quality flags (GPS gaps, sensor faults).
- **No bulk approve** for adverse outcomes. A free-text rationale is mandatory for any action affecting pay or discipline, and a **second reviewer** is required for disciplinary outcomes.
- **Calibrated uncertainty:** show sample size ("based on 312 km, low confidence") rather than false precision.
- **Stop control:** fleet managers can suspend scoring for a driver or depot (e.g., known sensor fault) with an audit record.
- **Measure oversight:** override rate, review-time distribution and inter-reviewer agreement. **Seed known-incorrect flags ("honeypots")** into the queue at ~2% and measure the detection rate. A reviewer who approves honeypots is rubber-stamping; that is an Art. 14 failure you can prove or disprove with data.

### 11. Frameworks (deep version in A6)

**NIST AI RMF 1.0** is still current (no 2.0). Its functions are Govern, Map, Measure, Manage, with the Generative AI Profile (NIST AI 600-1) and a draft Agentic profile from CSA (Mar 2026). **ISO/IEC 42001** is the certifiable AI management system standard (companions: ISO/IEC 23894 risk, ISO/IEC 42005 impact assessment). For builders, these frameworks organise *the same artefacts* you produce here. A6 builds the governance system around them.

**Misconceptions to unlearn:** "It's internal, so the AI Act doesn't apply." Putting into service for own use counts. "High-risk is delayed, so nothing applies." Art. 50, prohibitions and GDPR apply now. "A human clicks approve, so it's not automated." Not if the human cannot meaningfully disagree. "Fairness = remove the sensitive column." Proxies (depot ↔ ethnicity, route ↔ age) remain.

## Tools & versions (as of Oct 2026)

| Tool / resource | Purpose | Status | Notes |
|---|---|---|---|
| EU AI Act 2024/1689 + Digital Omnibus 2026/1744 | Legal basis | In force (Omnibus since 27 Jul 2026) | Use the consolidated EUR-Lex text when published |
| FPF EU AI Act Timeline 2026 R2 (PDF) | Timeline poster | Published Jul 2026 | Teaching aid, not authoritative |
| `docs/ai-act/` templates (course repo) | Inventory, risk file, DPIA delta, transparency note | Course artefact | Schema-tested |
| MEAI.Evaluation (custom `IEvaluator`) | Fairness and counterfactual judges in `dotnet test` | GA (verify version) | From C5/C14 |
| Fairlearn | Group fairness metrics | OSS | **[Python]**, optional cross-check |
| Foundry continuous evaluation | Post-market monitoring signals | GA (some evaluators preview) | From C15 |
| Microsoft Responsible AI Standard v2, Transparency Notes, HAX Toolkit | RAI practice templates | Published | Verify any revisions |
| NIST AI RMF 1.0 / AI 600-1; ISO/IEC 42001 | Governance frameworks | Current | Deep dive in A6 |

## Labs

### Lab 1 — AI system inventory and classification (≈1h)

- **Goal:** A machine-checkable inventory of Trakia's AI systems with risk class and role.
- **Start state:** tag `c18/lab1-start`; template `docs/ai-act/inventory.yaml`; feature cards for 11 systems (current product, D-track and A-track plans, the dashcam add-on).
- **Steps:**
  1. For each system, record: intended purpose, users, affected persons, data categories, Trakia role(s), risk tier, Annex III point (if any), Art. 6(3) assessment, Art. 50 duties, GDPR lawful basis hypothesis, DPIA needed (y/n), applicable date.
  2. Use your coding agent as a *sparring partner*, not an oracle. Ask it to argue the opposite classification for the three hardest systems, then decide yourself and cite the article.
  3. Mark open legal questions explicitly (`counsel_review: required`).
- **Break it:** The instructor changes one feature card's intended purpose mid-lab ("Fleet Analyst per-driver queries will be used in annual reviews"). Re-classify and list which downstream artefacts must change.
- **Acceptance criteria:** `dotnet test tests/Governance` validates the schema (every system has tier, role, rationale with article reference, date). Agreement with the instructor's hidden key on ≥9/11 tiers; any disagreement must carry a defensible written rationale.
- **Stretch:** Add the A-track scenario (Trakia sells to Romanian and Greek fleets) and list the provider documentation customers will need as deployers.

### Lab 2 — Driver Coaching Insights: two designs, one risk file (≈1.5h)

- **Goal:** Decide between a high-risk design and a legitimately non-high-risk design, then produce the risk file skeleton for the chosen one.
- **Start state:** `c18/lab2-start` with the `DriverCoaching` feature spec from HR.
- **Steps:**
  1. Write `docs/adr/0018-driver-coaching-scope.md` comparing (A) individual scores to managers for bonus/discipline (high-risk 4(b)) with (B) driver-facing coaching plus k-anonymous depot aggregates only. Cover business value, legal exposure, GDPR, worker relations and engineering cost.
  2. Assume management chooses (A). Fill `docs/ai-act/risk-file/` by mapping Arts. 9–15, 17 and 26 to evidence: link existing C14 eval reports, C15 trace schemas, the C16 threat register and ASR report, and create missing items as tracked issues.
  3. Add the **decision log** schema (pseudonymous driver ID, period, features, score, model and prompt versions, reviewer ID, decision, rationale) and its retention (≥6 months, justified against GDPR) to the DPIA delta.
  4. Implement the technical guardrail for design (B) as a test anyway: the API must refuse per-driver output to the `FleetManager` role when the feature flag `coaching.mode=aggregate` is set.
- **Break it:** Turn on OTel content capture in `prod-sim` and show that coaching letters with pseudonymous IDs and event details land in App Insights with 90-day retention. Write the finding as a DPIA risk and fix it (capture off + structured decision log).
- **Acceptance criteria:** ADR approved by peer review; risk-file checklist test passes (every article row has ≥1 linked artefact or an open issue); aggregate-mode test passes; the content-capture regression test fails when capture is enabled in a production configuration.
- **Stretch:** Draft the instructions for use (Art. 13) for a hypothetical customer deploying the feature.

### Lab 3 — Bias test and oversight UI (≈1.25h)

- **Goal:** Measure disparities correctly and build oversight that can detect rubber-stamping.
- **Start state:** `c18/lab3-start` with the synthetic scoring output for 600 drivers and a 400-event expert-labelled sample.
- **Steps:**
  1. Compute raw flag rates by depot, experience band and contract type. Then recompute per 1,000 km stratified by route type. Compare.
  2. Compute FPR parity against the labelled sample with bootstrap 95% CIs; mark groups with n < 30 truly-not-risky labelled events (the FPR denominator) as inconclusive and route them to manual review. They never auto-pass.
  ```csharp
  var byGroup = labelled.GroupBy(e => e.Group).Select(g => new {
      Group = g.Key,
      Fpr = Bootstrap.Ci(g.ToList(), s => s.Count(x => x.Flagged && !x.TrulyRisky) / (double)Math.Max(1, s.Count(x => !x.TrulyRisky)), iterations: 2000)
  });
  // Gate (rule and threshold recorded in the risk file):
  //  - groups with n >= 30: max/min FPR ratio POINT ESTIMATE <= threshold (e.g., 1.25); report the bootstrap 95% CI next to it
  //  - groups with n < 30: status ManualReview; release blocked until a named reviewer signs off in the risk file
  //  - any group whose ratio CI lower bound > threshold: fail outright (disparity is statistically clear)
  ```
  *Why not gate on "CI lower bound below the threshold"?* That rule passes whenever the data are too thin to *prove* a disparity, so the smallest groups (where harm is least visible) would pass by default. Gating on the point estimate with a minimum group size, and sending small groups to a human, puts the burden of proof on showing fairness rather than on showing harm.
  3. Run the counterfactual coaching-letter test (20 pairs) with the calibrated judge from C14.
  4. Complete the scaffolded Blazor review screen (layout and data binding provided in the start tag): evidence first, score second, mandatory rationale for adverse actions, no bulk approve, second reviewer for discipline, a suspend-scoring control. Seed 2% honeypots.
- **Break it:** Simulate a reviewer persona (a script) that approves everything in under 5 seconds. The oversight dashboard must flag the honeypot misses and the review-time anomaly.
- **Acceptance criteria:** Fairness report committed with stratified and unstratified results plus an interpretation paragraph; `FairnessGateTests` pass at the agreed threshold and assert that groups with n < 30 come out as `ManualReview`, never `Pass`; UI component tests assert no bulk-approve path and a required rationale; the rubber-stamp persona is detected.
- **Stretch:** Plot score calibration per depot (reliability diagram) and discuss whether a single threshold is fair across route types.

### Lab 4 — Transparency notices and Transparency Note (≈0.75h)

- **Goal:** Ship the Art. 50 and worker-facing communications.
- **Start state:** `c18/lab4-start`.
- **Steps:**
  1. Chat/Teams/voice disclosure strings in BG and EN, wired into the UI and the Teams welcome card (C17); add a UI test that asserts presence.
  2. Visible footer plus machine-readable marker on AI-drafted customer notifications (header + DB field); add a test.
  3. Worker information notice for Driver Coaching (what, why, data, retention, rights, human review, contact), for workers' representatives and drivers, at a plain-language reading level.
  4. A Microsoft-style Transparency Note for Fleet Ops Copilot: intended uses, out-of-scope uses, capabilities, limitations (incl. Bulgarian Content Safety gaps, groundedness English-only), evaluation results with numbers from C14/C16, human oversight, feedback channel.
- **Break it:** Ask a non-technical colleague (or a role-play persona) to read the worker notice and explain what happens if they disagree with their score. If they cannot, rewrite.
- **Acceptance criteria:** Disclosure UI tests and notification-marker tests pass; Transparency Note cites concrete metric values with dates and model/prompt versions; peer review confirms the readability check.
- **Stretch:** Make the Transparency Note a generated document that pulls the latest eval numbers in CI (ties into C19's docs agent).

## Kata

**"Classify in 20" (20 min, repeat 5×).** Draw a random feature card (e.g., "copilot ranks job applicants for driver vacancies", "chatbot answers customers about delivery delays", "AI allocates weekend shifts by past punctuality", "voice assistant summarises tachograph rules for drivers", "AI drafts LinkedIn posts about Trakia's safety record"). Within 20 minutes: tier, role, articles, today's obligations versus 2 Dec 2027, one design change that would lower the risk tier legitimately (or why none exists), and the single riskiest assumption to send to counsel. Peer scoring uses the instructor key; repeat until 4/5 are correct with sound rationale.

## Product increment — Fleet Ops Copilot

Fleet Ops Copilot now has:
- an AI system inventory and classification;
- ADR-0018 on Driver Coaching scope;
- a high-risk risk-file skeleton linked to real evidence (evals, traces, threat model, ASR);
- a DPIA delta with a log-retention design that reconciles AI Act and GDPR;
- an aggregate-mode technical guardrail;
- a stratified fairness report with a minimum-n gate (point estimate + CI reported; small groups to manual review);
- an oversight UI with honeypot monitoring;
- Art. 50 disclosures in all channels, marked AI-drafted notifications, a worker information notice and a Transparency Note.

## Factory increment — your agentic SDLC

- A `governance-check` job runs on PRs touching `prompts/`, `agents/`, scoring code or telemetry configuration. It validates the inventory schema, fails if a new tool or feature lacks an inventory entry, and fails if production telemetry config enables content capture.
- A docs agent (C19) regenerates the Transparency Note's metrics section from the latest eval artefacts; a human approves wording changes.
- The risk file's "evidence" links are checked for staleness (artefact older than the last model/prompt change → warning).

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Classification & roles | Guesses tiers | Correct tiers for clear cases | Correct incl. grey zones, cites Art. 6(3)/profiling and roles | Anticipates purpose drift; designs purpose-enforcing controls |
| Risk file & GDPR | Checklist copied | Arts. 9–15 mapped | Evidence linked to real artefacts; DPIA log design reconciles retention | Evidence auto-refreshed; residual risks argued; counsel questions sharply framed |
| Fairness | Raw rates only | Group metrics | Exposure-normalised, stratified, CIs, small-n handled | Confounders and proxies analysed; gate threshold justified |
| Human oversight | Approve button | Evidence shown | Anti-automation-bias design, second reviewer | Oversight measured (honeypots, agreement) and acted upon |
| Transparency | Missing | Generic text | Channel-specific, BG/EN, tested | Transparency Note with live metrics; readable by workers |

**Auto-checked:** governance schema tests, aggregate-mode guardrail, content-capture regression, fairness gate, disclosure/marker UI tests. These artefacts form the RAI/compliance section of **Gate G3**.

## Common pitfalls

- Treating "internal tool" or "human in the loop" as automatic exemptions.
- Classifying by technology ("it's just RAG") instead of by *use* and *affected persons*.
- Choosing the non-high-risk design on paper without the technical controls that enforce it.
- Logging everything for "AI Act compliance" and creating a GDPR problem; or logging nothing for "GDPR" and failing Art. 12/26.
- Fairness by raw rates across depots that drive different roads.
- Translating an English disclosure into Bulgarian with the same model you are disclosing, with no human review.
- Teaching the 2 Aug 2026 high-risk date. The Omnibus moved Annex III to 2 Dec 2027.
- Presenting the Bulgarian authority designation as settled.


## References

- Regulation (EU) 2024/1689 (AI Act): https://eur-lex.europa.eu/eli/reg/2024/1689/oj ; explorer: https://artificialintelligenceact.eu
- Digital Omnibus on AI, Regulation (EU) 2026/1744: Cuatrecasas https://www.cuatrecasas.com/en/spain/intellectual-property/art/digital-omnibus-ai-has-been-published ; Addleshaw Goddard https://www.addleshawgoddard.com/en/insights/insights-briefings/2026/technology/eu-ai-act-ai-omnibus-formally-adopted/ ; Netlaw (BG) https://www.netlaw.bg/en/a/the-eus-ai-act-is-already-changing-understanding-the-digital-omnibus-on-ai
- FPF EU AI Act Timeline 2026 R2: https://fpf.org/wp-content/uploads/2026/07/FPF-EU-AI-Act-Timeline-2026-R2.pdf
- Bulgaria tracker (single source, unconfirmed): https://vlolawfirm.com/trackers/ai-regulation-bulgaria ; also https://www.regulation-ai.eu/en/national-implementation/bulgaria/
- Microsoft Responsible AI: https://www.microsoft.com/en-us/ai/responsible-ai
- Azure AI Content Safety overview (language limits): https://learn.microsoft.com/en-gb/azure/ai-services/content-safety/overview
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework ; CSA Agentic NIST AI RMF Profile (draft): https://labs.cloudsecurityalliance.org/agentic/agentic-nist-ai-rmf-profile-v1/
- ISO/IEC 42001: https://www.iso.org/standard/81230.html
- MEAI Evaluation libraries: https://learn.microsoft.com/en-us/dotnet/ai/evaluation/libraries
- Baseline Foundry chat RA (agents-as-code, ops): https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
