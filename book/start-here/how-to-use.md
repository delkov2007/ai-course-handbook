# How to use this handbook and the course

This is the learner edition of the course handbook: the [Course overview](course-overview.md), the module chapters (C0–C19, D1–D7, A1–A7), [Assessment and gates](assessment-gates.md), the [Capstone](../capstone.md), the [Competency matrix](competency-matrix.md), a [Glossary](../appendix/glossary.md) and [Further reading](../appendix/references.md). This page explains how to work through it and the conventions used throughout.

## What is in a module, and how to use each part

Every module uses the same sections in the same order.

| Section | What it gives you | How to use it |
|---|---|---|
| **Why this matters** | The engineering problem and the evidence behind it | Read before the concept session. |
| **Learning outcomes** | What you will be able to do, as verbs | Your end-of-week checklist. |
| **Concepts** | The supportive information: mechanisms, decision rules, misconceptions to unlearn | Read before the concept session; test yourself against the misconceptions. |
| **Tools & versions** | Packages, services and their GA/preview status as of October 2026 | Check it when setting up labs; verify statuses against current documentation. |
| **Labs** (3–5) | Whole tasks on the product, each with Goal, Start state, Steps, Break it, Acceptance criteria and Stretch | Do them in order from the start tag (below). |
| **Kata** | A 20–40 minute drill for a recurrent skill | Three times a week, with variations. |
| **Product increment** | What Fleet Ops Copilot can do after the module | Confirm you reached it; the next module builds on it. |
| **Factory increment** | What your agentic delivery pipeline gained | Commit it; your Factory comes with you into every gate. |
| **Assessment** | A four-level rubric (Novice / Competent / Proficient / Expert) plus the auto-checks run by CI | Self-assess against the rubric before you submit. |
| **Common pitfalls** | The mistakes earlier learners made | Read before the labs and again when stuck. |
| **References** | Primary sources for the module | Follow them when a decision depends on them; see also [Further reading](../appendix/references.md). |

The modules also contain instructor notes for the teaching team. They are not part of this edition.

### Working a lab

1. **Start from the tag.** Each lab names its start state as a Git tag in the `trakia-fleetops` lab repo, in the form `cN/labN-start` for core modules (for example `c4/lab1-start` or `c7/lab2-start`), `dN/labN-start` for the Developer track and `aN/labN-start` for the Architect track. If your product has drifted too far from the reference, ask your mentor about rebasing onto the module's catch-up tag (for example `c7/end`) and carrying your Factory forward.
2. **Follow the steps, but predict first.** Many steps ask you to predict an outcome before you run it. Write it down; the gap between prediction and measurement is where you learn.
3. **Do the "Break it" step.** Every lab induces a failure on purpose: a regression, an injection, an outage, a model swap or a cost spike. Do not skip it: diagnosing failures from evidence is the core skill of the course.
4. **Get the acceptance criteria green in CI.** Acceptance criteria are automated wherever possible (tests, eval thresholds, CI status, policy checks). A lab is done when CI on your fork says so.
5. **Write the explanation.** Each module asks for a written artefact: an ADR, a postmortem or an eval report. **The explanation is graded.** It should say why something broke, why your fix is the right one, and what you chose not to do.
6. **Stretch goals are optional.** Do them when you are ahead or when they map to a competency you want to reach at Expert.

### Katas

A kata is part-task practice for a recurrent skill: tool schemas, eval cases, KQL, APIM policies, ADRs, threat-model deltas, explaining a diff. Do it as **three sessions of about 30 minutes spread across the week**, each with the suggested variation. Some katas are deliberately unaided ("solo-first"); keep them that way, because they protect you from cognitive debt in a codebase you did not type.

### Product and Factory increments

Every module adds to both the product (Fleet Ops Copilot for the fictional Trakia Freight) and your **Factory**, your own agentic delivery system. Keep a clean history: Factory assets (memory files, skills, hooks, custom agents, CI templates, eval helpers) are the only things you may bring into a gate.

## The weekly rhythm

A standard part-time week is 12 hours:

| Block | Time | What to do |
|---|---|---|
| Concept session | 1.5 h | Come having read *Why this matters* and *Concepts*. The session adds a live "predict → run → explain" demo. |
| Lab block 1 | 3 h | Labs 1–2 (Do + Break). |
| Lab block 2 | 3 h | Labs 3–4 (Fix + acceptance criteria green in CI). |
| Katas | 1.5 h | 3 × 30 min, spaced across the week, each with a variation. |
| Explain | 1 h | The module's ADR, postmortem or eval report. |
| Peer review | 1 h | Review two peers' PRs or eval reports using the module rubric. |
| Office hours / mentor | 1 h | Group troubleshooting; architecture clinics in the A-track. |

Intensive and bootcamp paces are in the [Course overview](course-overview.md). Whatever the pace, protect the explanation and peer-review hours; they are the first to be squeezed and the ones the gates reward.

## Working through coding agents (from C4 onward)

From C4, all product work goes through your Factory. Coding agents do most of the typing; **you specify, constrain and verify**. You are graded on how you direct agents, not on keystrokes.

- **Specify.** Choose the least ceremony that makes the work verifiable: issue text for a one-line fix, plan mode for a multi-file change, a short `SPEC.md` plus human-written acceptance tests for a feature.
- **Constrain.** Keep memory files short and curated. Put rules that must always hold into hooks, permission settings and CI, not into prose. Run agents in the devcontainer sandbox with deny rules for secrets, pushes and unvetted packages.
- **Verify.** Use the plan → implement → verify loop. "Done" means the build, tests and eval smoke suite are green, enforced by a hook or CI, not the agent's summary.
- **Humans own the assertions.** Acceptance tests and golden-set labels are protected paths. Agents may read them and must keep them green; they may not edit them.
- **Ownership rule.** You must be able to explain, predict and modify every line you merge. In gate orals and the capstone, failing to explain your own code scores Novice on agent direction. Practise the "explain the diff" kata on every agent PR.
- **Keep session evidence.** Export or log your agent sessions; gates require them.

## Gates at a glance

Three practical gates separate the core levels: **G1** after C5, **G2** after C11 and **G3** after C19. Each takes about 6 hours plus an oral.

- **Book a slot.** Gates are scheduled: each cohort gets a gate week, with resit slots 2–3 weeks later. Self-paced learners book gate slots individually.
- **Hidden evals.** Your submission is graded against a hidden eval suite you never see, run three times; safety items must pass all three runs (pass^3).
- **Your own gate is tested.** The grader mutates your system and checks whether your CI eval gate notices.
- **A short no-assistant segment.** Each gate includes a proctored unaided block, such as predicting behaviour from traces or writing a design note.
- **Oral defense.** Assessors pick diff hunks at random; you explain, predict the effect of a change and make one change live.
- **Bring your Factory** (and nothing else from your own product code). G3 also needs an evidence pack submitted 48 hours before the gate.

Full rules, rubrics, hard gates, retakes and appeals are in [Assessment and gates](assessment-gates.md).

## Choosing a track after G3

After G3 the course splits into two expert tracks of about 120 hours each. You declare your intended track at G2 and confirm it after G3 (instructors need the split early to form mixed capstone teams).

- **AI Solution Developer (D1–D7)** goes deeper into engineering: model customization and local models, durable agents, multimodal and realtime agents, agent UX, performance and cost engineering, custom agent tooling and reliability engineering. Choose it if you want to own *how* systems are built and measured. Its track-critical competencies are K1, K2, K4, K5, K7 and K8.
- **AI Solution Architect (A1–A7)** goes broader in judgement: strategy and business cases, reference architectures, knowledge platforms, agent platforms, reliability and FinOps, governance and the architect's craft. Choose it if you want to own *whether and what* gets built and the constraints others build within. Its track-critical competencies are K3, K5, K9, K10, K11 and K12.

Decide from your [Competency matrix](competency-matrix.md) self-assessment and gate feedback. The Developer track order is recommended; the Architect track is effectively sequential. You may take **both tracks** (about 120 extra hours). The capstone needs G3 plus at least four modules of one track.

## Your capstone team

The capstone is 80 hours per learner over 6–8 weeks, in teams of 4–5 with **at least two Developer-track and two Architect-track learners**. Instructors form the teams. Everyone commits product code (at least five reviewed, non-trivial PRs), everyone authors at least two ADRs, and everyone takes part in both sides of the red-team swap. Inception starts in the last one or two weeks of the expert track. The client in each brief answers only what you ask, so elicitation is part of the grade. See [Capstone](../capstone.md).

## Cost discipline habits

Spend estimates are in the [Course overview](course-overview.md). Staying inside them is a habit, and the gates assess it.

- **Rate limits are the real ceiling; budgets only alert.** Keep low TPM quotas on your deployments and respect the gateway token quota.
- **Default to the fast-small model role or Foundry Local.** Use the frontier role only where a lab says so, and keep reasoning effort low unless the lab measures it.
- **Cache eval runs.** Use MEAI.Evaluation response caching in CI and run uncached only when you need to measure model variance.
- **Tag everything** (`course`, `owner`, `module`, `expiresOn`) and run the lab's teardown (`azd down --purge` or `scripts/teardown.sh`) as soon as a lab that creates fixed-cost resources is done. `doctor.sh --azure` checks this.
- **Watch the usual offenders:** a paid AI Search tier left running, re-embedding the whole corpus repeatedly, agent loops without budgets, private-networking components left up, content capture in traces, and fine-tuned deployments left hosted.
- **Report cost per task, not per token.** If cost blocks your progress, tell your mentor or the course lead rather than skipping a lab.

## Where to get help

- **Office hours:** weekly group troubleshooting with a mentor (architecture clinics in the A-track). Bring a trace, a failing test or a draft ADR.
- **Your mentor:** PR and eval-report reviews, remediation plans after a gate, weekly capstone check-ins.
- **Peer review:** your two weekly reviews show you what good looks like.
- **The module itself.** *Common pitfalls* and *Misconceptions to unlearn* answer most "why doesn't this work?" questions.
- **No capable hardware?** Every lab has a Codespaces path, and local-model labs list a cloud fallback.

With agent problems, expect to be asked what the agent was told, what it was allowed to do and how you verified its output.

## Conventions used in this handbook

- **[Python]** and **[Node]** mark the bounded parts of the course that use those runtimes (for example red teaming with PyRIT, Playwright test agents, AG-UI front-ends). Everything else is C# on .NET 10.
- **[preview]**, **Preview** and **prerelease** mark dependencies that are not generally available. Each has a GA fallback in the lab.
- **Volatility tags** (Low, Med, High) in each module header tell you how fast the material dates. Concepts are written to last; *Tools & versions* tables are snapshots as of October 2026.
- **"Verify against current documentation"** marks a fact that was correct when written but is likely to change: a price, a status, a region list, a package name or a legal detail. Check the primary source before you rely on it.
- **Lab tags** follow `<module>/lab<N>-start` (for example `c4/lab1-start`, `d2/lab3-start`, `a5/lab2-start`).
- **ADRs** live in `docs/adr/` as `NNNN-short-title.md`, with numbers that mostly follow the core module requiring them (`0001-default-reasoning-effort.md` in C1, `0006-policy-vector-store.md` in C6, `0017-hosting.md` in C17; C13 adds both 0013 and 0014). The G3 evidence pack refers to ADRs by these numbers. Every ADR considers at least three options (including "do nothing" where meaningful), links evidence and sets a review date; a linter enforces this from C1.
- **Model roles, not model names.** Code and labs refer to roles such as `chat-fast`, `chat-reasoning`, `embedding` and `chat-local`, mapped to deployments in `models.json`. A model change is a configuration change followed by an eval run.
- **Vehicle identifiers.** `TRK-0471` is the **fleet/vehicle ID** (`VehicleId`): assigned by TrakiaOps, stable for the vehicle's life, and the key used by tools, traces, logs and approvals. `РВ 4471 АК` is the **registration plate** (`VehicleReg`): canonical in Cyrillic with spaces, typed by drivers in Cyrillic or Latin look-alikes, normalised to Cyrillic in code, able to change over the vehicle's life, and resolved to the fleet ID by lookup. Never join or approve on the plate.
- **Competency codes** K1–K12 refer to the twelve areas of the [Competency matrix](competency-matrix.md).
