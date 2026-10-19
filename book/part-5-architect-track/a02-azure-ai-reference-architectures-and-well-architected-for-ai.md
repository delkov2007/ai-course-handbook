# A2 — Azure AI reference architectures & Well-Architected for AI

> **Level:** Expert — AI Solution Architect track · **Duration:** 20h (theory 30% / labs 70%) · **Prerequisites:** A1; C16 (threat model), C17 (deployed Fleet Ops Copilot with APIM, private networking, Bicep) · **Volatility:** High (Foundry Agent Service features, AI Landing Zones and Entra Agent ID move quarterly; WAF principles are stable)

## Why this matters

**What separates an expert architect from a proficient one here:** a proficient architect can deploy a reference architecture. An expert knows *why each component is there*, which guarantees it does **not** give, and where it has to be bent for this workload. They can show a review board the gaps between "the reference architecture" and "our production system", with evidence. For Foundry today those gaps are no built-in DR, no native load balancing, no per-user conversation authorization, and single-region standard deployments.

Trakia's C17 deployment works, but it grew one decision at a time. Customer fleets will now send security questionnaires: how is our data isolated, where are prompts processed, which identities do agents run as, what happens when a region fails? "App Service → OpenAI" answers none of that. Architects who never internalised the baseline Foundry chat architecture miss its warning that Agent Service does not enforce per-user conversation ownership (a BOLA hole in a multi-tenant product). They assume Foundry has DR, leave public data planes open "for the portal", and reach for multi-agent designs that Microsoft's own guidance says are often unnecessary.

Experts use the Well-Architected Framework (WAF) AI guidance and the reference architectures as a *checklist of decisions*, not a template to clone. They:

- model AI-specific elements (models, agents, tools, knowledge, guardrails, trust boundaries) in C4;
- land workloads in a governed landing zone;
- pick orchestration patterns from spike evidence;
- can restate the design in AWS or Google terms.

## Learning outcomes

1. **Assess** an existing AI workload against the WAF AI workload guidance (10 design areas, pillar-mapped principles), using the Assessment Review Tool. **Produce** a prioritised findings register.
2. **Explain and adapt** the baseline Microsoft Foundry chat reference architecture, component by component, including its documented limitations, and **justify** each deviation for Trakia.
3. **Deploy** an AI application landing zone from `Azure/AI-Landing-Zones` (preview, Bicep, AVM). **Validate** it with policy and rule-based IaC checks.
4. **Design** hub-spoke private networking for Foundry, AI Search, Cosmos DB and APIM, with private DNS and egress allow-listing, and **diagnose** private-endpoint and egress failures.
5. **Design** the identity architecture: managed identities per component, keyless auth, Entra Agent ID for agents, persona RBAC, OBO for user-context tool calls. **Close** the BOLA gap in code.
6. **Select** an orchestration pattern (single prompt → single agent → workflow → multi-agent) from spike evidence measured with your C14 evals, and **record** the decision.
7. **Model** the system in C4 with an AI profile (models, agents, tools, knowledge, guardrails, trust boundaries, untrusted-content flows), validated as code.
8. **Map** the design onto AWS and Google equivalents and **identify** the portability seams.

## Concepts

### 1. Well-Architected Framework for AI workloads

WAF's AI workload guidance (updated May 2026; verify against current documentation) organises the problem into **10 design areas**:

1. application design;
2. application platform;
3. training data design;
4. grounding data design;
5. data platform;
6. MLOps/GenAIOps;
7. workload operations;
8. testing and evaluation;
9. workload personas;
10. responsible AI.

Design principles are mapped to the five pillars (reliability, security, cost optimisation, operational excellence, performance efficiency). An **Assessment Review Tool** turns this into a production-readiness questionnaire. In this track the tool is your review instrument. Every architecture package you submit from now on includes a WAF AI assessment with findings, severity and an owner.

**What is different about AI workloads under WAF:**

- **Nondeterminism means testing becomes evaluation.** Regression suites, statistical pass rates and LLM judges validated against humans (C14) replace exact-match tests.
- **Data is part of the runtime.** Grounding data has freshness, permission and residency properties that act as availability and security properties.
- **Dependencies have expiry dates.** Model lifecycle policies force planned change (A5).
- **Cost has a new variable axis.** Tokens scale with *behaviour*, not just traffic. Prompts, tool loops, reasoning effort and agent count all move the bill.
- **"Workload personas"** is its own design area. Who is the user, who is the operator, who is the data owner, and which actions can each take?

### 2. The baseline Microsoft Foundry chat reference architecture

This is the most important reference for the track (Architecture Center, updated Aug 2026, verify against current documentation; implementation `Azure-Samples/microsoft-foundry-baseline`; a landing-zone variant `baseline-microsoft-foundry-landing-zone` exists). Learn it component by component.

**Topology.**

- **Agent runtime:**
  - A Foundry Agent Service **prompt agent** in **standard setup with BYO VNet**.
  - Standard setup means agent state lives in **customer-owned** Cosmos DB (conversations and agent definitions; `enterprise_memory`), Storage and AI Search, all *dedicated* to Agent Service.
- **Front end:**
  - A **zone-redundant App Service** hosts the chat UI.
- **Ingress and egress:**
  - **Application Gateway with WAF** is the *only* ingress. WAF exclusions are needed for the chat body, otherwise prompts trip OWASP rules.
  - **Azure Firewall** handles egress with **FQDN allow-lists**. Agent traffic leaves via a delegated agent subnet and a UDR.
- **Private access:**
  - **Private endpoints** everywhere, with **public data planes blocked**.
  - Portal access goes through **Bastion + jump box**.

**Identity.**
- Separate **system-assigned managed identities** per component.
- Entra ID connections.
- RBAC mapped to personas.
- **Project-level connections only.**
- **One Foundry resource per production workload.**

**Security warning to memorise.** Agent Service does **not** enforce per-user conversation authorization. If your API accepts a conversation or thread ID from the client and passes it to the agent, any authenticated user who obtains another user's ID can read or continue that conversation. This is classic Broken Object Level Authorization (BOLA). The application must store ownership (user, tenant → conversation ID) and check it on every call. In SaaS, the check is user **and** tenant.

**Reliability, as documented.**
- Standard model deployments are single-region. Use **Data Zone provisioned with spillover**, or Global deployments.
- Foundry has **no native load balancing or circuit breaking**, so APIM is the suggested option.
- Agent Service has **no built-in DR**. Recovery is by **reconstruction**: agents-as-code, backups and delete locks.
- **Multi-region is out of scope** of the baseline. You design it in A5.

**Cost, as documented.**
- The largest costs are Cosmos DB, AI Search and DDoS Protection.
- Agents may call tools unnecessarily, so limit tools.
- Use the cheapest model that meets requirements.
- Use PAYG for variable load and PTU for a stable baseline.

**Operations.**
- **Agents as code** via CI/CD.
- Immutable agent versions.
- Regression suites, because behaviour is nondeterministic.
- MAF (C#/Python) for runtime.
- Azure Policy to disable local auth and require private endpoints.

**The expert move is the gap analysis.** For Trakia the gaps are:

1. SaaS needs tenant isolation, which the baseline does not cover.
2. The C12 workflow needs a code-first runtime, so you deviate to a **hosted agent** or self-hosted MAF.
3. Bulgarian users need a Bulgarian-calibrated groundedness judge, because Content Safety groundedness detection is English-only.
4. EU residency needs Data Zone EU deployments.
5. Customer-facing availability needs multi-region (A5).
6. APIM moves from "optional" to mandatory as the AI gateway (A4).

### 3. AI Landing Zones

The CAF "AI ready" phase places AI workloads into an Azure landing zone. `Azure/AI-Landing-Zones` (GitHub, **preview**, MIT) is an *application* landing zone for AI apps and agents in two parts:

- the **AI Foundry Landing Zone**;
- the **AI Gateway Landing Zone** (APIM).

Both are implemented in **Bicep and Terraform on Azure Verified Modules (AVM)**, with a legacy Bicep branch.

Keep the platform/application split clear:
- The **platform landing zone** (connectivity hub, identity, management, policy, owned by the platform team) provides hub networking, DNS, firewall and central logging.
- The **application landing zone** (owned by the workload team, under platform guardrails) holds Foundry, Search, Cosmos, APIM instances and app compute.

For Trakia's SaaS, decide whether APIM is a *shared* AI gateway (platform-owned, many workloads) or a *workload* gateway (tenant-aware, product-owned). Most products end up with both: a central gateway for model access and quota, and a product gateway for tenant APIs. Record the choice in an ADR.

**Preview means:**
- pin a commit SHA;
- read the changelog before upgrading;
- expect breaking changes;
- keep your own deviations as overlays, never as edits to the upstream module.

### 4. Networking decisions

- **Hub-spoke.** The hub holds Firewall, Bastion and the DNS resolver. Spokes hold the AI app landing zones. Private DNS zones for each private-link service are linked to the hub. Verify the exact zone names for Foundry/AI Services, AI Search, Cosmos DB, Storage and Key Vault against current docs, because Foundry endpoints use several hostnames.
- **Public network access disabled** on Foundry, Search, Cosmos, Storage and Key Vault, enforced by Azure Policy (A6).
- **Egress allow-listing.** List the FQDNs your agents and tools must reach (supplier API, telematics provider, Microsoft endpoints). **Hosted agents' network egress controls are preview.** For self-hosted agents in Container Apps, egress goes through the Firewall via UDR.
- **Service-to-search traffic.** AI Search indexers reaching private data sources need shared private links. Budget for them and test them, because they are a classic silent failure.
- **Developer access.** A jump box or Bastion, or a dev environment in a peered VNet. "Temporarily enabling public access" is how data planes stay open forever.

### 5. Identity architecture

- **Workloads** use **managed identities**, keyless auth to Foundry, Search, Cosmos and Storage, and local auth disabled. Each component gets its own identity so that blast radius and audit trails stay separable.
- **Agents as principals.** **Microsoft Entra Agent ID is GA.**
  - Agents get their own identities, created from **agent identity blueprints** (design guidance is available; the blueprint and identity creation wizard is preview).
  - **Conditional Access templates for agents** can block high-risk agent identities, autonomous agent access and on-behalf-of agent access.
  - Sponsor lifecycle governance gives each agent an accountable human.
  - Registry convergence under **Microsoft Agent 365**.
  - Federation patterns for AWS and GCP, and integrations with Bedrock and n8n.
  - Per-feature GA/preview status is ambiguous on the what's-new page, so verify against current documentation.
- **User context.**
  - Tools that act *as the user*, such as reading the user's calendar or SharePoint, use **OBO**.
  - Tools that act *as the system*, such as creating a work order, use the agent identity with least privilege. The approval is recorded under the user.
  - Never let the model choose which identity to use.
- **Personas → RBAC.** Map Trakia roles (dispatcher, mechanic, fleet manager, HR, auditor; in SaaS also tenant admin and Trakia operator) to data-plane roles and app roles. Auditors get read access to traces and evidence, not to agent configuration.

### 6. Orchestration pattern selection

The Architecture Center's ladder:

1. **Direct model call.**
2. **Single agent with tools.** Often the right enterprise default, with iteration limits.
3. **Multi-agent.** Only for cross-domain problems, **security boundaries** or parallel specialisation.

The patterns are sequential, concurrent, group chat (≤ 3 agents), handoff and Magentic. The listed pitfalls are over-engineering and adding agents without real specialisation.

The evidence is nuanced:

- **For multi-agent:** Anthropic's lead-plus-subagents research system beat a single agent by 90.2% on its internal eval, at ~15× chat tokens. The task was read-heavy and parallel.
- **Against:** Cognition shows that parallel agents with partial context make conflicting decisions on write-heavy, coupled tasks.

**Decision rule:**
- Use a deterministic **workflow** when the process is known (Trakia's incident flow mostly is).
- Use a single agent for open-ended assistance.
- Use multi-agent when there is a real boundary. Example: the Fleet Analyst holds SQL read access that the customer-notification agent must never have.

A security boundary is often the *best* reason for a second agent, and "it's more modular" is the worst.

### 7. C4 modelling for AI systems: the course profile

No authoritative standard exists for C4 extensions for AI, so this is a **course-designer convention**. Use it consistently and say so in reviews. Model with Structurizr DSL (diagrams as code) and use these element tags with mandatory properties:

| Tag | Mandatory properties |
|---|---|
| `Model Deployment` | model role, provider, version, deployment type (Global / Data Zone / Regional Standard, PTU, Batch), region(s), auto-upgrade policy, retirement date |
| `Agent` | kind (prompt / hosted / self-hosted MAF / Copilot Studio), identity (Agent ID), autonomy level (inform / recommend / act-with-approval / act), tools, max iterations and token budget, HITL points, owner/sponsor |
| `Tool` / `MCP Server` | side effect (read / write / irreversible), auth mode (MI / OBO), data classification, first- or third-party, pinned version/hash |
| `Knowledge Base` | sources, ACL mode (query-time filter / native propagation), freshness SLA, residency |
| `Guardrail` | intervention points (input / tool call / tool response / output), risks covered, action |
| `Trust boundary` | a group around elements sharing an identity and network boundary |

Also tag relationships that carry **untrusted content** (web pages, customer emails, uploaded documents, third-party tool output).

**A validation script checks the lethal trifecta per agent.** If an agent has (private data) + (an untrusted-content inbound relationship) + (an external-communication tool), the build fails unless the agent element references a mitigation ADR.

Add a **dynamic diagram** for the incident workflow trajectory and a **deployment diagram** per environment.

### 8. Cloud-agnostic thinking: AWS and Google equivalents

An expert can explain the design without product names: a managed agent runtime, a retrieval service, a gateway, workload identity for agents, and policy enforcement. The mapping below is **indicative and must be verified before teaching**. Only the A2A integration of Bedrock AgentCore and Google ADK's native A2A support were verified in the research for this course.

| Capability | Azure | AWS (verify) | Google Cloud (verify) |
|---|---|---|---|
| Model catalogue / serving | Microsoft Foundry models (multi-vendor; Gemini not sold on Azure) | Amazon Bedrock | Vertex AI (Gemini) |
| Managed agent runtime | Foundry Agent Service (prompt and hosted agents) | Bedrock AgentCore (A2A integrated — verified) | Vertex AI Agent Engine (verify name) |
| Agent framework | MAF (connectors for Bedrock and Gemini too) | Strands / Bedrock Agents (verify) | ADK (native A2A — verified) |
| Retrieval | AI Search / Foundry IQ | Bedrock Knowledge Bases / OpenSearch (verify) | Vertex AI Search (verify) |
| AI gateway | APIM AI gateway | API Gateway + custom (no direct equivalent verified) | Apigee (verify AI features) |
| Agent identity | Entra Agent ID (federates to AWS/GCP) | IAM roles / AgentCore identity (verify) | Service accounts / workload identity |
| Well-architected guidance | WAF AI workload | Well-Architected Generative AI Lens (unverified) | Architecture Center GenAI guidance (unverified) |

**Portability seams** are what keep exit cost low:
- `IChatClient` and MEAI for model access;
- MCP for tools;
- A2A for agents;
- OTel GenAI semantic conventions for telemetry;
- agents-as-code (declarative YAML / MAF code) in Git;
- evals in your own harness.

Anything outside these seams is lock-in you choose deliberately, and that choice should be recorded in an ADR.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| WAF AI workload guidance + Assessment Review Tool | Review instrument | GA (guidance updated 2026-05-07; verify against current documentation) | Use for every architecture package |
| `Azure-Samples/microsoft-foundry-baseline` | Baseline reference implementation | Sample | Compare your C17 deployment |
| `Azure/AI-Landing-Zones` | Foundry LZ + AI Gateway LZ (Bicep/Terraform on AVM) | **Preview** | Pin commit SHA |
| Bicep + Azure Verified Modules | IaC | GA | `az bicep` version pinned in devcontainer |
| `azd` | Environment provisioning | GA | From C17 |
| PSRule for Azure | Rule-based IaC validation incl. WAF rules | OSS | Verify current version and rule coverage for Foundry |
| Azure Policy | Deny public network, require private endpoints, disable local auth | GA | Built-in definitions for AI services exist; verify names |
| Foundry Agent Service (prompt agents, standard setup, BYO VNet) | Agent runtime | GA | No built-in DR; no per-user conversation auth |
| Foundry hosted agents | Code-first agent runtime | **GA** (9 Jul 2026) | Egress controls preview |
| Microsoft Entra Agent ID | Agent identities, CA templates | GA (blueprint wizard preview) | Agent 365 registry convergence |
| MAF 1.0 (`Microsoft.Agents.AI`) | Orchestration spike | GA | Five orchestration patterns |
| Structurizr DSL + CLI/Lite | C4 as code | OSS | Validation script in lab repo |
| Mermaid C4 | Lightweight alternative | Experimental in Mermaid | Use for docs, not as source of truth |
| `Microsoft.Extensions.AI.Evaluation` | Evidence for the pattern ADR | GA (verify versions) | |

## Labs

### Lab 1 — WAF AI assessment of your C17 deployment (≈3.5h)

- **Goal:** Produce an evidence-backed findings register for the current Fleet Ops Copilot.
- **Start state:** branch `a2/start` (your G3 baseline deployed in your sandbox subscription) and `architecture/waf/` templates.
- **Steps:**
  1. Run the WAF AI Assessment Review Tool for the workload and export the results.
  2. For each of the 10 design areas, attach evidence. The evidence types are: a Bicep path, an Azure Resource Graph query result, a KQL query, an eval report, or a screenshot only as a last resort. Example Resource Graph query:
     ```kusto
     resources
     | where type in~ ('microsoft.cognitiveservices/accounts','microsoft.search/searchservices','microsoft.documentdb/databaseaccounts')
     | project name, type, publicNetworkAccess = tostring(properties.publicNetworkAccess),
               disableLocalAuth = tostring(properties.disableLocalAuth)
     ```
  3. Diff your deployment against `microsoft-foundry-baseline`: ingress, egress, private endpoints, identities, standard setup, agents-as-code. List each difference as *intentional* (with an ADR) or a *gap* (with a finding).
  4. Build the findings register (`waf/findings.csv`): ID, design area, pillar, severity (Critical / High / Med / Low), evidence, owner, remediation, target date.
  5. Pick the top 5 findings and estimate remediation in t-shirt sizes with the uncertainty stated (A7 revisits estimation).
- **Break it:** The instructor flips one Cosmos DB account to `publicNetworkAccess: Enabled` and adds a key-based connection in a Foundry project. Your Resource Graph checks must detect both, and the register must classify them as Critical.
- **Acceptance criteria:**
  - All 10 design areas have ≥ 1 evidence item.
  - The register passes the schema check.
  - The injected misconfigurations are detected by your queries (CI job `waf-drift` runs them).
  - Every "intentional deviation" links to an ADR.
- **Stretch:** Turn your Resource Graph queries into PSRule custom rules and run them in CI on the Bicep before deployment, as a shift-left complement to post-deployment detection.

### Lab 2 — C4 with the AI profile, validated as code (≈3.5h)

- **Goal:** A C4 model that a security reviewer, a customer's architect and a coding agent can all read, and that fails the build when the design is unsafe.
- **Start state:** `a2/lab2-start` with `architecture/c4/workspace.dsl` skeleton, tag definitions and `validate-ai-profile` (.NET console).
- **Steps:**
  1. Model the **System Context**: Fleet Ops Copilot, the Trakia user personas, customer fleets (SaaS), the telematics provider, the parts supplier, M365/Teams and model providers through Foundry.
  2. Model the **Containers**: web/Teams front ends, the agent API, the Fleet Assistant, Fleet Analyst and incident workflow agents, the MCP servers (tickets, scheduling, parts), the knowledge bases, model deployments, APIM, Cosmos DB, SQL `TrakiaOps`, and App Insights. Apply the AI profile tags with all mandatory properties.
  3. Draw the trust boundaries: Trakia internal, the per-tenant boundary for SaaS, third-party tools, and model providers.
  4. Mark untrusted-content relationships: customer emails into the incident workflow, supplier API responses, uploaded delivery notes.
  5. Add a **dynamic view** of the incident workflow, from fault event through triage, diagnostics, policy check, booking with approval and customer notification. Add **deployment views** for dev and prod.
  6. Run `validate-ai-profile`. It checks the mandatory properties, finds trifecta agents, flags `Model Deployment` elements whose retirement date falls within 6 months, and flags tools with `irreversible` side effects that lack a HITL point.
- **Break it:** Add a "customer email auto-reply" tool to the Fleet Assistant (which already reads private incident data and ingests customer emails). The validator must fail with a trifecta violation. Fix it with one of two options, each with an ADR: (a) move email drafting to a separate agent with no private-data tools, or (b) require human approval before send.
- **Acceptance criteria:**
  - `structurizr validate` passes and `validate-ai-profile` exits 0.
  - The rendered diagrams are committed.
  - The trifecta break is detected and fixed with an ADR.
  - Every agent element names an Entra Agent ID or managed identity.
- **Stretch:** Make the C4 DSL agent-readable context. Add it to `AGENTS.md` and have your coding agent answer "which agents can write to `TrakiaOps`?" from the model alone. Check the answer against the code.

### Lab 3 — Deploy an AI application landing zone and break its network (≈5h)

- **Goal:** Land Fleet Ops Copilot in a governed landing zone and learn the failure signatures of private networking.
- **Start state:** `a2/lab3-start` contains:
  - a fork reference to `Azure/AI-Landing-Zones` pinned at a course-tested SHA;
  - a platform-hub stub (Firewall, Bastion, DNS resolver, Log Analytics);
  - parameter files for `trakia-prod-weu` (or a course-assigned EU region).
- **Steps:**
  1. Deploy the hub stub, then the **AI Foundry Landing Zone** and the **AI Gateway Landing Zone** with your parameters (EU region, private endpoints on, public access off, standard agent setup, BYO VNet).
  2. Add your overlays as separate Bicep modules, not upstream edits:
     - per-component managed identities;
     - project-level connections only;
     - diagnostic settings to central Log Analytics;
     - delete locks on Cosmos DB and the Foundry resource.
  3. Wire the private DNS zones to the hub resolver. Verify name resolution from the agent subnet and the jump box: `nslookup <search>.search.windows.net` must return a private IP. Verify Foundry hostnames against the docs.
  4. Configure the Firewall application rules: allow-list the supplier API, the telematics provider and the required Microsoft FQDNs (document each with its reason).
  5. Assign the policy initiative: deny public network access, require private endpoints, disable local auth (definitions in `policy/`; A6 extends them).
  6. Redeploy Fleet Ops Copilot into the landing zone via `azd` and run the C14 smoke eval suite through App Gateway.
- **Break it:** Run these three induced faults one at a time and record symptom → diagnosis → fix in `runbooks/network-faults.md`:
  - (a) delete the DNS zone link for AI Search. The agent's retrieval fails with timeouts or name-resolution errors. Find it via the dependency failures in App Insights.
  - (b) remove the supplier FQDN from the Firewall. The parts tool fails with a 403/connection error. Find it in the Firewall logs.
  - (c) attempt to deploy a Storage account with public access. Azure Policy must deny it, and you capture the deny event.
- **Acceptance criteria:**
  - PSRule for Azure passes on the overlays with no Critical findings.
  - The policy compliance scan shows 100% compliance on the AI resources.
  - The smoke eval suite passes through the private path.
  - All three faults are diagnosed in the runbook with the KQL used.
  - `az resource list` shows no AI resource with public access enabled.
- **Stretch:** Run Terraform from the same repo as a parallel deployment in a second resource group. Write a half-page "Bicep vs Terraform for Trakia" ADR that weighs team skills, AVM parity and state management.

### Lab 4 — Identity and the BOLA hole (≈3.5h)

- **Goal:** Prove the per-user conversation authorization gap exists, close it, and move agents to first-class identities.
- **Start state:** `a2/lab4-start`. The agent API accepts `conversationId` from the client (the deliberately naive C9 shape).
- **Steps:**
  1. **Exploit.** As user `mechanic-varna-02`, obtain `conversationId` values: they are logged in a debug header and are guessable from a sequential test fixture. Call the API with another user's ID and read that conversation. Write the exploit as an xUnit security test that *currently passes*.
  2. **Fix.** Add a conversation ownership store (Cosmos container `conversationOwnership`, partition key `/tenantId`, keyed by conversation ID → `{tenantId, userObjectId, createdAt}`). Enforce it in middleware before any agent call. Return 404, not 403, to avoid leaking existence. Use non-guessable IDs.
     ```csharp
     app.Use(async (ctx, next) =>
     {
         if (ctx.Request.RouteValues.TryGetValue("conversationId", out var id))
         {
             var principal = ctx.User; // Entra token: oid + tid (+ app role)
             var owner = await ownership.GetAsync(principal.TenantId(), (string)id!);
             if (owner is null || owner.UserObjectId != principal.ObjectId())
             { ctx.Response.StatusCode = StatusCodes.Status404NotFound; return; }
         }
         await next();
     });
     ```
  3. Flip the exploit test to assert 404. Add a cross-*tenant* variant using the SaaS tenant claim.
  4. **Agent identity.** Register the Fleet Assistant and the incident workflow agents with **Entra Agent ID** (blueprint wizard in preview; scripted path if available, otherwise portal; verify). Grant least-privilege roles (ticket MCP: write; `TrakiaOps`: none for the assistant). Apply a Conditional Access template that blocks high-risk agent identities.
  5. **OBO path.** The "my upcoming shifts" tool calls the scheduling API on behalf of the user. Verify in the logs that the downstream call carries the user's identity and the agent's identity, and that a disabled user cannot be impersonated.
- **Break it:** Grant the Fleet Assistant identity `Contributor` on the resource group "to fix a permission error". Your access review query must flag it. Write the finding and revert.
- **Acceptance criteria:**
  - The BOLA tests (same-tenant and cross-tenant) pass in CI.
  - No agent identity holds roles beyond the least-privilege matrix (`identity/matrix.yaml`, checked by a script that reads role assignments).
  - Sign-in and audit logs show the agent identity for agent actions.
  - The OBO evidence is captured.
- **Stretch:** Register each MCP server as a protected resource with distinct scopes. Show that the incident agent's token cannot call the HR knowledge MCP server.

### Lab 5 — Orchestration pattern spike and portability map (≈4.5h)

- **Goal:** Choose the incident workflow's orchestration pattern from measured evidence, and show the design survives a cloud change on paper.
- **Start state:** `a2/lab5-start` with your C12 multi-agent workflow, the C14 trajectory and outcome eval suite (60 incident scenarios, incl. 10 adversarial customer emails) and the τ-bench-style end-state checks.
- **Steps:**
  1. Implement three variants behind one interface:
     - (A) a **single agent** with all tools and an iteration cap of 12;
     - (B) a **deterministic sequential workflow** (MAF `WorkflowBuilder`) with an LLM step only at triage and drafting;
     - (C) a **handoff multi-agent** design (triage → diagnostics → policy → scheduling → notification) with per-agent tool scopes.
  2. Run the suite 4× per variant (pass^4 for reliability). Collect task success, the trajectory evaluators (tool-call accuracy), tokens and cost per task (A1 model), p95 latency, the injection ASR on the adversarial emails, and the number of identities holding write tools.
  3. Fill the decision matrix and write **ADR-A2-003 "Incident orchestration pattern"**. Expected insight (do not assume it, measure it): (B) usually wins on cost, latency and reliability for a known process, while (C) or a B/C hybrid may be justified *only* by the security boundary around customer-email handling.
  4. **Portability map:** annotate your C4 containers with the AWS and Google equivalents (Concepts §8 table, verified where you can). List every non-portable dependency with an exit cost estimate.
- **Break it:** Add a fourth "group chat with 5 agents" variant because "the business liked the demo". Measure it. Then write the two-sentence answer to the sponsor explaining why it doesn't ship. Microsoft's guidance keeps group chat at ≤ 3 agents.
- **Acceptance criteria:**
  - Eval reports for all variants are committed.
  - The ADR cites the measured pass^4, cost and ASR.
  - The chosen variant meets the G3 thresholds.
  - The portability map lists ≥ 6 dependencies, each with seam/no-seam status.
- **Stretch:** Re-implement variant B's triage step as a Copilot Studio agent that calls the rest via A2A. Measure the added latency and the governance implications.

## Kata

**"Reference architecture gap hunt"** (30 min, repeat with variations).

You get a one-page architecture description and diagram. Within 30 minutes, list the top 7 gaps against the baseline Foundry chat RA and the WAF AI design areas. For each gap, name the risk, the evidence that would confirm it, and the fix.

Variations:
- a public-endpoint RAG app with API keys;
- a multi-tenant agent passing `threadId` from the browser;
- a hosted agent with unrestricted egress and a web-browse tool;
- a "multi-region" design whose second region has no model quota;
- a design on Global Standard deployments for EU personal data;
- a 6-agent group chat for invoice approval.

The score is the share of reference gaps found, plus a bonus for gaps the reference missed and you justified.

## Product increment — Fleet Ops Copilot

Fleet Ops Copilot now runs in an **AI application landing zone** that has:

- private networking;
- Firewall egress allow-listing;
- policy-enforced private endpoints and keyless auth;
- per-component managed identities;
- agents registered with Entra Agent ID;
- the BOLA gap closed for users and tenants.

It is described by a **validated C4 model with the AI profile**, assessed with a **WAF AI findings register**, and the incident workflow's orchestration pattern is chosen by ADR from measured evidence.

## Factory increment — your agentic SDLC

- **Architecture-as-code gates in CI:**
  - `structurizr validate`;
  - `validate-ai-profile` (trifecta, HITL on irreversible tools, model retirement horizon);
  - PSRule on Bicep;
  - `waf-drift` Resource Graph checks after deploy.
- **An "architecture reviewer" custom agent** (`.github/agents/arch-reviewer.agent.md` or a Claude Code subagent). It reads PR diffs plus the C4 DSL and flags drift: a new outbound dependency missing from the model, a tool added without a side-effect tag, a public endpoint. It comments only; humans decide.
- **Security regression tests (BOLA)** in the default test suite.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| WAF AI assessment | Questionnaire answered without evidence | Evidence for some areas | All 10 areas evidenced; prioritised register; deviations vs baseline classified | Plus automated drift detection, and findings tied to business impact and A1 costs |
| Reference architecture fluency | Copies the baseline | Explains components | Explains limits (no DR, no native LB, BOLA, single-region standard) and adapts them with ADRs | Plus anticipates SaaS-specific gaps and designs mitigations before they are asked for |
| Network & identity design | Public endpoints / keys | Private endpoints, some MI | Landing zone, policy-enforced, per-component MI, Agent ID, OBO, BOLA fixed and tested | Plus fault diagnosis runbook, least-privilege matrix enforced by script, cross-tenant tests |
| Orchestration choice | Picks multi-agent by default | Justifies by intuition | Measured spike (pass^k, cost, ASR, latency) and ADR | Plus security-boundary reasoning, hybrid designs, explicit "when to revisit" triggers |
| Architecture communication (C4 + portability) | Boxes and arrows | C4 levels correct | AI profile complete; validated as code; dynamic view | Plus portability seams and exit costs quantified; the model is used by agents and reviewers |

**Auto-checked:**
- Structurizr and AI-profile validation;
- PSRule;
- policy compliance;
- `waf-drift` queries;
- BOLA tests;
- identity matrix script;
- eval reports and thresholds for the spike;
- ADR linter.

## Common pitfalls

- Treating the baseline as complete: **no built-in DR**, **no native load balancing**, multi-region out of scope.
- Passing client-supplied conversation IDs to Agent Service (BOLA), or forgetting the tenant dimension of the check.
- Public access left on "for the portal".
- Private endpoints without DNS: everything deploys, nothing resolves.
- Editing upstream landing-zone modules instead of overlaying, or upgrading a preview repo without pinning.
- One shared identity for all agents.
- Multi-agent for modularity's sake; group chats with more than 3 agents.
- C4 diagrams without models, tools and untrusted-content flows, which is exactly where the AI risks live.
- Unverified AWS/Google equivalence claims.


## References

- WAF AI workloads — get started (10 design areas, Assessment Review Tool): https://learn.microsoft.com/azure/well-architected/ai/get-started
- Baseline Microsoft Foundry chat reference architecture: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
- Implementation: https://github.com/Azure-Samples/microsoft-foundry-baseline
- AI Landing Zones (preview): https://github.com/Azure/AI-Landing-Zones
- CAF AI adoption scenario: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/
- AI agent orchestration patterns: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
- APIM AI gateway capabilities: https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities
- What's new in Entra Agent ID: https://learn.microsoft.com/en-us/entra/agent-id/whats-new-agent-id ; Agent identity blueprints: https://learn.microsoft.com/en-us/entra/agent-id/agent-blueprint
- Foundry Agent Service at Build 2026 (hosted agents, previews): https://devblogs.microsoft.com/foundry/agent-service-build2026/
- What's new in Microsoft Foundry July–August 2026 (hosted agents GA 9 Jul 2026; Toolboxes GA): https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-july-august-2026/
- Foundry guardrails (tool-call/response controls preview; egress controls preview): https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview
- Anthropic, multi-agent research system: https://www.anthropic.com/engineering/multi-agent-research-system ; Cognition, Don't Build Multi-Agents: https://cognition.ai/blog/dont-build-multi-agents
- Simon Willison, the lethal trifecta: https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
- Linux Foundation A2A press release (Bedrock AgentCore, Foundry, Copilot Studio): https://linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year
- Content Safety language/region limits (groundedness English-only): https://learn.microsoft.com/en-gb/azure/ai-services/content-safety/overview
- C4 model: https://c4model.com ; Structurizr DSL: https://docs.structurizr.com/dsl (AI profile is a course convention, not a standard)
