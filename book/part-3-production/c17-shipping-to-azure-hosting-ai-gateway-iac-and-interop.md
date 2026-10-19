# C17 — Shipping to Azure: hosting, AI gateway, IaC & interop

> **Level:** 3 — Production systems (Advanced) · **Duration:** 16h (theory 25% / labs 75%) · **Prerequisites:** C8 (MCP server), C9 (Fleet Assistant), C12 (incident workflow), C14 (eval gates), C15 (OTel, cost per task), C16 (identities, guardrails, threat register) · **Volatility:** High (hosted-agent GA, incoming A2A, Teams publishing, APIM unified API and Foundry AI gateway are all moving)

## Why this matters

Until now Fleet Ops Copilot has run under Aspire on a laptop, talking to a dev Foundry project over public endpoints with a developer's credentials. Trakia's IT department will not accept that in production. They want everything in a Bicep file they can review. They want no public data-plane endpoints, a single place to cap token spend per depot, survival when the PTU deployment is saturated at 07:00 as 600 drivers start shifts, and an answer to "what happens when the region or the model disappears?" They also want dispatchers to use the copilot inside Teams, and their customer's planning agent to call Trakia's agent over A2A.

Teams without this skill hand-click resources in the portal, hard-code keys "temporarily", and point every client straight at one model deployment. The first 429 storm becomes an outage and the first model retirement a fire drill. Prompt or model changes go to 100% of users at once, so a regression that a canary would have caught in 30 minutes reaches every dispatcher. They also tend to assume Foundry provides DR and per-user conversation isolation. It provides neither.

Experts treat the AI system as an ordinary distributed system with three extra properties. Its behaviour changes when a *configuration* (model, prompt) changes. Its capacity is a *quota* rather than a VM size. Its failures are often *semantically* wrong rather than HTTP 500s. They ship with infrastructure as code and agents-as-code. All model traffic goes through an AI gateway that enforces identity, quotas, metering, failover and safety. Every AI change is released like a risky feature: behind flags, to a canary, promoted on quality signals and not just error rates.

## Learning outcomes

1. **Choose and justify** a hosting model per component (Foundry hosted agent, Container Apps, App Service, Functions) for a given workload, recording the decision as an ADR.
2. **Provision** the full Fleet Ops Copilot stack from an Aspire AppHost with `azd` and Bicep, with keyless auth, managed identities and agents-as-code.
3. **Implement** the security-relevant parts of the baseline Microsoft Foundry chat reference architecture (private endpoints, firewall egress allow-list, WAF ingress, conversation ownership) and **explain** its documented limits (no built-in DR, no native load balancing).
4. **Configure** an APIM AI gateway with token limits keyed on validated identity, token metrics for chargeback, a PTU-first backend pool with circuit breaker, scoped semantic caching and content safety, and **demonstrate** 429 failover under load.
5. **Plan** model capacity and quotas (deployment types, TPM, PTU vs PAYG, spillover, retirement) from C15 telemetry.
6. **Expose** a Trakia agent as an A2A endpoint with an Agent Card and gateway policy, and **publish** the copilot to Teams with the right disclosure and safety posture.
7. **Run** an eval-gated canary release of a model or prompt change, with automatic rollback on quality, cost or latency regression.

## Concepts

### 1. Hosting options and how to choose

| Option | What it is | Strengths | Watch out for | Trakia fit |
|---|---|---|---|---|
| **Foundry Agent Service – prompt agents** | Declarative agent (instructions, tools, knowledge) defined in Foundry | Least code; Foundry guardrails, tracing, evals built in | Logic limited to what the service models; BOLA is your problem | Simple "Ask Fleet Ops" policy Q&A variant |
| **Foundry Agent Service – hosted agents** | Your containerized agent code (MAF, Copilot SDK, LangGraph, Claude Agent SDK, custom). Each session runs in its own sandbox with dedicated compute, memory and filesystem; exposed via the Responses API or a pass-through *Invocations* protocol | Managed scaling, identity and per-session isolation; long-running durable state; Foundry Control Plane tracing/evals | **GA since 9 Jul 2026**; egress controls preview; Toolboxes **GA**, memory and routines preview | Fleet Assistant (MAF) |
| **Azure Container Apps** | Serverless containers with revisions, traffic splitting, KEDA scaling, VNet integration; dynamic sessions for sandboxes | Default `azd` target for Aspire; revision-based canary; scale-to-zero; good for stateless MCP servers | You own agent runtime concerns (checkpoint store, session state) | API, Blazor UI, Trakia MCP server, Fleet Analyst |
| **App Service** | PaaS web hosting; zone-redundant; deployment slots | The baseline RA's UI host; slot swap for blue/green | Less natural for background workers | Alternative UI host |
| **Azure Functions** | Event-driven; Flex Consumption; **MCP extension (C# isolated only)**; **Durable extension for MAF (prerelease)** | HITL waits that consume no compute or tokens; Service Bus triggers | Durable agents prerelease; cold starts | Incident workflow with multi-hour approvals (stretch) |
| AKS | Kubernetes | Full control, GPU self-hosting | Platform team required; not a default | D-track self-hosted models only |

Decision rules: (1) choose the option with the *least operational responsibility* that meets requirements (the CAF heuristic). (2) Stateless MCP servers (spec 2026-07-28 removed sessions) belong behind plain round-robin, so ACA or Functions. (3) Long human waits favour Durable, but prerelease status means you need a GA fallback (ACA + MAF checkpointing from C12). (4) Agents needing per-session filesystem isolation favour hosted agents. Record the choice in `docs/adr/0017-hosting.md`.

### 2. The baseline Microsoft Foundry chat reference architecture

The Architecture Center baseline (implementation: `Azure-Samples/microsoft-foundry-baseline`) is the reference Trakia's architect reviews against:
- Foundry Agent Service in **standard setup with BYO VNet**: conversations and agent definitions in customer-owned **Cosmos DB**, plus Storage and AI Search, dedicated to Agent Service.
- **Application Gateway + WAF** as the only ingress, with WAF exclusions for chat request bodies (natural language trips SQLi/XSS rules).
- **Azure Firewall** egress through a delegated agent subnet and UDR, with FQDN allow-lists.
- **Private endpoints everywhere**, public data plane blocked; Bastion/jump box for portal access.
- **Separate system-assigned managed identities** per component; RBAC mapped to personas; Azure Policy to disable local auth and require private endpoints.
- One Foundry resource per production workload; project-level connections only.
- **Agents-as-code via CI/CD**, immutable agent versions, regression suites (behaviour is nondeterministic).

Its documented limits are the exam questions:
- Agent Service **does not enforce per-user conversation authorization**; the app must (C16).
- Foundry has **no native load balancing or circuit breaking**; APIM is the suggested option.
- Agent Service has **no built-in DR**. Recovery is *by reconstruction* from agents-as-code, Cosmos/Search backups and delete locks.
- Standard model deployments are single-region. Use Data Zone provisioned with spillover, or Global deployments. Multi-region is out of scope (A5).
- The biggest cost lines are Cosmos DB, AI Search and DDoS Protection, so the full baseline is expensive for a lab. The course uses a `dev` profile (public endpoints restricted by IP, no Firewall) and a `prod` profile (full baseline), selected by an `azd` environment parameter.

`Azure/AI-Landing-Zones` (**preview**; Bicep/Terraform on Azure Verified Modules) pairs a Foundry landing zone with an APIM AI gateway landing zone. It is the starting point for A2 and the capstone.

### 3. Infrastructure and agents as code

**Aspire → azd.** The AppHost already models Trakia's topology. `azd init` detects the AppHost; `azd up` provisions and deploys (ACA by default). You can generate Bicep from the app model (`azd infra gen`; older docs say `azd infra synth`, so **verify** for your azd version) and own it from then on. Aspire 13.x also has its own publish/deploy commands; the course standardizes on `azd` because Trakia's pipelines already use it *(verify current Aspire 13.6 deployment guidance)*.

```csharp
// AppHost/Program.cs (Aspire 13.x) — integration method names: verify against your pinned Aspire packages
var builder = DistributedApplication.CreateBuilder(args);

var foundry = builder.AddAzureAIFoundry("foundry");          // Foundry resource + deployments
var sql     = builder.AddAzureSqlServer("sql").AddDatabase("TrakiaOps");
var search  = builder.AddAzureSearch("search");

var mcp = builder.AddProject<Projects.Trakia_Mcp>("trakia-mcp")
                 .WithReference(sql).WithReplicas(3);       // stateless MCP 2026-07-28: prove it

builder.AddProject<Projects.FleetOps_Api>("fleetops-api")
       .WithReference(foundry).WithReference(search).WithReference(sql).WithReference(mcp)
       .WithExternalHttpEndpoints();

builder.Build().Run();
```

**Bicep for Foundry.** The new model is one Foundry resource (`Microsoft.CognitiveServices/accounts`, kind `AIServices`) with child `projects` and `deployments`:

```bicep
// Bicep requires a literal API version in the type string (no interpolation/variables).
// 2025-06-01 is shown as a GA version with Foundry projects; pin the current GA version and verify.
resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: foundryName
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: foundryName
    allowProjectManagement: true        // Foundry resource+project model (verify property name)
    disableLocalAuth: true              // no keys, ever
    publicNetworkAccess: env == 'prod' ? 'Disabled' : 'Enabled'
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: foundry
  name: 'fleet-ops'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {}
}

resource reasoning 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: foundry
  name: 'frontier-reasoning'                         // role name, not model name (blueprint rule)
  sku: { name: 'DataZoneStandard', capacity: reasoningTpmK }   // EU data zone for GDPR residency
  properties: {
    model: { format: 'OpenAI', name: reasoningModel, version: reasoningModelVersion }
    versionUpgradeOption: 'NoAutoUpgrade'           // upgrades are releases (§8); verify enum values
  }
}
```

Role assignments grant each managed identity the least-privileged Foundry data-plane role on the *project* (verify current built-in role names, e.g., "Azure AI User"). SQL access uses contained users created by a post-provision script.

**Agents-as-code.** Prompt agents, hosted-agent definitions, guardrail assignments, tool manifests (C16) and model-deployment bindings live in `agents/` and are deployed by the pipeline through `Azure.AI.Projects.Agents` (or REST). They are never edited in the portal. Every deployment creates a new immutable agent version tagged with the git SHA, which is also your DR story.

**Model lifecycle in IaC.** Standard GA models get at least 18 months (deprecated at 12, retired at 18); Anthropic, DeepSeek, Fireworks and Mistral models 12 months, some Grok models 6; and preview models ~90 days. Notice is at least 60 days, retirement dates cannot be extended, and retired models return `410 Gone`. **PTU deployments are not auto-upgraded.** Pinning `NoAutoUpgrade` plus a nightly lifecycle check (C15) turns retirements into planned canary releases instead of surprises.

### 4. Network and identity in production

- Private endpoints for Foundry, AI Search, SQL, Cosmos, Storage, Key Vault, App Configuration; private DNS zones in IaC.
- Firewall FQDN allow-list *derived from the threat register*. Fleet Assistant needs the Foundry and Search private endpoints and the supplier API FQDN, nothing else; an unexpected egress attempt is a security signal (C16).
- Managed identity from every app to every backend, including APIM → Foundry (`authentication-managed-identity`). Key Vault only for third-party secrets.
- Entra auth on every public entry point: App Gateway → app (Entra ID), APIM (`validate-jwt`), MCP (OAuth per 2026-07-28 auth spec), A2A (security schemes in the Agent Card).

### 5. The APIM AI gateway

Policies (GA unless noted):
- `llm-token-limit`: TPM and token quotas (hour to year) per any counter key; can pre-estimate prompt tokens.
- `llm-emit-token-metric`: token metrics with custom dimensions to Azure Monitor for chargeback.
- `llm-semantic-cache-lookup` / `llm-semantic-cache-store`: embedding-based cache that needs Azure Managed Redis or another RediSearch-compatible cache.
- Backend **pools** (round-robin, weighted, **priority**, session-aware) with a **circuit breaker that honours `Retry-After`**.
- `llm-content-safety`: Content Safety at the gateway.
- **MCP:** expose a REST API as an MCP server, and pass through and govern existing MCP servers.
- **A2A:** import A2A agent APIs.
- **Unified OpenAI-compatible model API** across providers: **preview**. **AI gateway in Microsoft Foundry** (model quotas, agent registration, MCP tool governance): **preview**. Anthropic Messages API support on v2 tiers.

The policy shape for Trakia's chat route:

```xml
<policies>
  <inbound>
    <base />
    <validate-jwt header-name="Authorization" failed-validation-httpcode="401" output-token-variable-name="jwt">
      <openid-config url="https://login.microsoftonline.com/{{tenant-id}}/v2.0/.well-known/openid-configuration" />
      <audiences><audience>api://trakia-fleetops-gateway</audience></audiences>
    </validate-jwt>
    <!-- Key quotas on a VALIDATED claim, never on a client-supplied header -->
    <set-variable name="depot" value="@(((Jwt)context.Variables["jwt"]).Claims.GetValueOrDefault("depot", "unknown"))" />
    <llm-token-limit counter-key="@((string)context.Variables["depot"])"
                     tokens-per-minute="60000" estimate-prompt-tokens="true"
                     remaining-tokens-header-name="x-trakia-remaining-tokens" />
    <llm-emit-token-metric namespace="trakia-ai">
      <dimension name="Depot" value="@((string)context.Variables["depot"])" />
      <dimension name="Feature" value="@(context.Request.Headers.GetValueOrDefault("x-trakia-feature","unknown"))" />
    </llm-emit-token-metric>
    <authentication-managed-identity resource="https://cognitiveservices.azure.com" /> <!-- verify audience for Foundry v1 routes -->
    <set-backend-service backend-id="foundry-reasoning-pool" />
  </inbound>
  <backend><base /></backend>
  <outbound><base /></outbound>
  <on-error><base /></on-error>
</policies>
<!-- Attribute names per the GA policy reference; re-verify on each APIM update. -->
```

The `Feature` dimension comes from a header, which is acceptable for *attribution* and never acceptable for *quota*: know which dimensions an attacker can spoof. The **backend pool** is an APIM backend resource of type `Pool` in Bicep: the PTU deployment at priority 1, a Data Zone Standard PAYG deployment at priority 2, each with a circuit-breaker rule that trips on 429 and accepts `Retry-After` *(verify the backend resource schema)*.

**Semantic caching rules.** Cache only routes whose answers do not depend on user, time or permissions, such as the policy-handbook FAQ with `vary-by` role *and* language. Never cache telematics, schedules or anything security-trimmed: a semantic cache without the right vary-by keys is a cross-user disclosure channel (C16). Measure hit rate *and* a wrong-answer rate on a sampled set; a high hit rate with stale or wrong answers is a regression.

**MCP behind the gateway.** Thanks to the 2026-07-28 `Mcp-Method`/`Mcp-Name` headers, APIM can rate-limit `trakia.maintenance.book_slot` separately from `trakia.parts.search` and enforce the per-agent tool allow-list from C16 without parsing JSON-RPC bodies.

### 6. Quotas, capacity and rate limiting

Model capacity is a quota: TPM per model, deployment type and region per subscription, with RPM derived from TPM. Deployment types: **Global Standard** (highest availability, data processed anywhere), **Data Zone Standard (EU)** (processing kept in the EU data zone, Trakia's default for GDPR), and **Provisioned (PTU)**, either Global or Data Zone, which gives reserved throughput for a stable baseline, with spillover to standard. Batch is ~50% cheaper for non-interactive work such as nightly fleet summaries *(background: verify current discount and data-zone availability)*.

Capacity planning uses C15 telemetry. Take the p95 TPM during the 06:30–08:00 shift start, multiply by the growth factor, and compare PTU break-even with PAYG; PTU suits the stable baseline and PAYG the variable load (baseline RA). Rate limiting is layered: client SDK retries with jitter honouring `Retry-After` → gateway per-depot/per-feature quotas → app-level per-session budgets (C9) → model deployment limits. A 429 at the gateway, raised because a depot exhausted its quota, is a *business* decision and should be surfaced to users as such ("Varna's daily AI budget is used up; contact fleet manager"), not retried forever.

### 7. Interop: A2A endpoints and Teams

**A2A v1.0** (stable since 9 Apr 2026, Linux Foundation) gives peer agents a discoverable **Agent Card** (name, description, endpoint, capabilities, skills, security schemes) and, new in 1.0, **Signed Agent Cards** for cryptographic identity. Options for Trakia:
- MAF A2A hosting. MAF 1.0 said "A2A 1.0 support coming soon", so **verify the current MAF A2A package and API** before the lab.
- Foundry **incoming A2A** (any Foundry agent as an A2A endpoint with an agent card) is **public preview**; outbound A2A (call remote agents as a tool) is available.
- APIM **A2A agent API import** for authentication, quotas and logging.

Trakia exposes a narrow `shipment-eta` skill to a customer's planning agent, *not* the whole Fleet Assistant. Least agency applies across organizations too. The customer's agent is untrusted input (C16 trifecta), so it gets read-only ETA for its own shipments, with the customer ID taken from the authenticated client and never from the request.

```json
{
  "name": "Trakia Shipment ETA Agent",
  "description": "Returns ETA and status for shipments owned by the calling customer.",
  "url": "https://api.trakia-freight.example/a2a/shipment-eta",
  "version": "1.3.0",
  "capabilities": { "streaming": false },
  "skills": [{ "id": "shipment-eta", "name": "Shipment ETA",
               "description": "ETA, last GPS checkpoint, delay reason category.",
               "examples": ["ETA for shipment TF-2026-118842?"] }],
  "securitySchemes": { "entra": { "type": "oauth2" } }
}
```

(Field names follow the v1.0 card shape as commonly published; **verify** against the spec and the `.well-known` path before the lab.)

**Teams / Microsoft 365 Copilot.** Foundry's publishing to Teams and M365 Copilot was announced at Build 2026; its GA status is unverified in our sources (**verify current status** before teaching). Publishing adds a channel, and with it obligations. The AI Act Art. 50 disclosure that users are interacting with an AI (C18) must appear in the channel UX. Adaptive cards and link unfurling are exfiltration-capable rendering surfaces (C16). Conversation ownership must map Teams user identity to your conversation store.

### 8. Releasing AI changes: blue/green, canary, shadow

AI releases include code, *prompt*, *model deployment*, *tool definition*, *retrieval index* and *guardrail* changes. All six can regress quality without a single HTTP error. Mechanisms:
- **Blue/green:** App Service slot swap; ACA revisions with 0/100 traffic; AI Search **index aliases** (GA) for re-indexing.
- **Canary:** ACA revision traffic weights (`az containerapp ingress traffic set --revision-weight …`); APIM weighted backends for *model version* canaries; Azure App Configuration feature flags for *prompt/agent version* canaries per depot.
- **Shadow:** mirror a sample of requests to the candidate and compare offline with pairwise judges (C14). No user impact, double cost.

Promotion criteria for an AI canary combine: the offline eval gate (C14) passed *before* the canary; online signals over a minimum sample (e.g., ≥300 conversations or 24h, whichever is later) covering online eval pass rate (Foundry continuous evaluation or MEAI online scores), thumbs-down rate, tool error rate, p95 latency, TTFT, **cost per task**; and no new guardrail block categories. Rollback is automatic when any signal crosses a pre-registered threshold. Pre-registration matters: deciding thresholds after looking at the data is p-hacking your release.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| Foundry Agent Service – hosted agents | Managed runtime for containerized agents | **GA** (9 Jul 2026) | Responses API / Invocations protocol |
| Foundry incoming A2A | Agent as A2A endpoint | **Preview** | Outbound A2A available |
| Foundry publish to Teams / M365 Copilot | Channel publishing | Announced Build 2026 — **verify current status** | Check tenant admin policies |
| `Azure.AI.Projects` / `.Agents` / `Azure.AI.Extensions.OpenAI` | Agents-as-code deployment, Responses | GA 2.0.0 | Don't mix with preview `Azure.AI.Projects.OpenAI` |
| Aspire | AppHost, local orchestration, deployment model | 13.6 | Integration names: verify per version |
| Azure Developer CLI (`azd`) | Provision + deploy, environments | GA | Bicep generation command: verify |
| Bicep + Azure Verified Modules | IaC | GA | `Azure/AI-Landing-Zones` **preview** |
| Azure Container Apps | Hosting, revisions, traffic split | GA | Dynamic sessions status: verify |
| Azure Functions MCP extension | MCP server hosting | Available, C# isolated only | Streamable HTTP |
| Claude Opus 5 on Foundry | Frontier model option behind the gateway | **GA** (24 Jul 2026) | Check regional/Data Zone availability |
| MAF Durable extension | Durable agents on Functions/DTS | **Prerelease** | GA fallback required |
| APIM AI gateway policies | Token limits/metrics, cache, pools, content safety, MCP, A2A | GA | Unified model API **preview**; Foundry AI gateway **preview** |
| Azure Managed Redis | Semantic cache backing store | GA | RediSearch required |
| Azure App Configuration | Feature flags for prompt/agent canaries | GA | |
| Azure Load Testing | 429/failover drills | GA | |
| A2A .NET SDK / MAF A2A hosting | A2A endpoints | A2A spec v1.0; MAF A2A 1.0 package — **verify** | |

## Labs

### Lab 1 — From AppHost to Azure with azd and Bicep (≈2.5h)

- **Goal:** One command provisions and deploys Fleet Ops Copilot (dev profile) with zero secrets.
- **Start state:** tag `c17/lab1-start` (C16 product increment, Aspire AppHost, `infra/` empty).
- **Steps:**
  1. `azd init` in the repo root; confirm it detects the AppHost; create environments `dev-<initials>` and `prod-sim`.
  2. Generate Bicep, move it to `infra/`, then refactor: a Foundry module (resource, project, three role-named deployments with `NoAutoUpgrade`), SQL, Search, Key Vault, App Configuration, ACA environment, per-app managed identities and role assignments.
  3. Add `agents/fleet-assistant.agent.yaml` (instructions file reference, tool manifest, guardrail name, deployment role) and a `postdeploy` hook that publishes it via `Azure.AI.Projects.Agents`, tagging the agent version with `GITHUB_SHA`.
  4. `azd up`. Run the C14 smoke eval suite against the deployed endpoint.
  5. Ask your coding agent to review `infra/` with the Azure Bicep MCP tools (bicepschema/best practices) and triage its suggestions in the PR.
- **Break it:** Set `disableLocalAuth: false` and add an API key to `appsettings.Production.json`. The policy check and secret scanning must both fail the PR.
- **Acceptance criteria:** `azd up` from a clean clone succeeds in under 25 minutes; `az resource list` shows no Foundry/Search/Storage resource with local auth enabled (scripted check); smoke evals pass at ≥ the C14 threshold; `azd down --purge` leaves nothing behind (scripted check).
- **Stretch:** Run `what-if` in CI and post the diff as a PR comment.

### Lab 2 — Production network and identity baseline (≈2.5h)

- **Goal:** The `prod-sim` profile implements the baseline RA's security controls.
- **Start state:** `c17/lab2-start` (adds `infra/network/` skeleton).
- **Steps:**
  1. VNet with subnets (ACA, private endpoints, agent subnet delegated, firewall, App Gateway).
  2. Private endpoints and private DNS for Foundry, Search, SQL, Key Vault, App Configuration; `publicNetworkAccess: 'Disabled'`.
  3. Azure Firewall with an FQDN allow-list generated from `security/egress-allowlist.yaml` (owned by the threat register from C16); UDR from the ACA and agent subnets.
  4. App Gateway WAF as the only ingress, with targeted WAF exclusions for the chat request body field only.
  5. Azure Policy assignments: deny local auth, require private endpoints for Cognitive Services.
- **Break it:** From the Fleet Analyst container, attempt `GET https://example.org` and a direct call to the Foundry *public* hostname. Both must fail; capture the Firewall log entries.
- **Acceptance criteria:** Scripted reachability tests (from a jump box and from outside) match the expected matrix; Firewall denies appear in Log Analytics; the BOLA test from C16 passes against the deployed environment.
- **Stretch:** Delete locks on Cosmos/Search plus a documented reconstruction runbook: rebuild the agent from `agents/` in a fresh project in under 30 minutes.

### Lab 3 — AI gateway: quotas, chargeback, failover, cache (≈3h)

- **Goal:** All model traffic goes through APIM; failover and per-depot budgets are demonstrable.
- **Start state:** `c17/lab3-start` (APIM instance in IaC, two Foundry deployments: `reasoning-ptu-sim` with a low TPM to simulate saturation, `reasoning-paygo`).
- **Steps:**
  1. Repoint the app's `IChatClient` to the APIM endpoint by configuration only (blueprint rule: provider-swappable).
  2. Apply the policy from Concepts §5. The policy reads a `depot` claim: issue it as an optional/custom claim (directory extension attribute or claims-mapping policy) on test users, or derive it from an app-role value (`roles` claim, e.g. `Depot.Varna`) and adapt the policy expression accordingly.
  3. Create the backend pool (priority 1: PTU-sim; priority 2: PAYG) with circuit-breaker rules on 429 honouring `Retry-After`.
  4. Add a separate `/policy-faq` operation with semantic cache lookup/store, vary-by role + language, threshold tuned on 40 paraphrase pairs from the golden set.
  5. Add `llm-content-safety` on the chat route as a gateway layer in addition to Foundry guardrails (C16).
  6. Build a workbook: tokens per depot per feature per day, cost estimate, cache hit rate, 429s by backend.
  7. Azure Load Testing: 200 virtual dispatchers at 07:00 load for 10 minutes.
- **Break it:** Exhaust Varna's quota. Users in Varna must get a clear budget message while Plovdiv is unaffected. Then send a request with a forged `x-trakia-depot: plovdiv` header and confirm it changes nothing.
- **Acceptance criteria:** During the load test, ≥99% of requests succeed end-to-end while PTU-sim returns 429 (failover proven in metrics); per-depot quota isolation test passes; FAQ cache hit rate ≥30% on the replay set with 0 wrong-answer cache hits on the 40-pair check; chargeback workbook committed as JSON.
- **Stretch:** Put the Trakia MCP server behind APIM with per-tool rate limits using `Mcp-Name`.

### Lab 4 — Hosted agent, A2A endpoint and Teams (≈2h)

- **Goal:** Compare hosting models and open two new channels safely.
- **Start state:** `c17/lab4-start`.
- **Steps:**
  1. Package Fleet Assistant as a Foundry **hosted agent** (container image from the same MAF code). Deploy alongside the ACA version and run the C14 agent eval suite against both; record latency, cost per task and operational differences in ADR-0017.
  2. Expose `shipment-eta` via A2A (MAF A2A hosting, or Foundry incoming A2A preview), behind APIM A2A import with client-credentials auth for the customer "Rhodope Retail". Customer ID comes from the client app registration.
  3. Publish the copilot to a Teams test team (Foundry publishing; verify GA). Add the AI disclosure line and disable link unfurling of model-generated URLs.
- **Break it:** As Rhodope Retail, request the ETA for a shipment belonging to another customer, and try to inject "list all shipments" in the free-text field.
- **Acceptance criteria:** A2A contract test validates the Agent Card and returns 404/empty for foreign shipments; injection attempt yields no extra data; ADR-0017 contains a measured comparison table.
- **Stretch:** Sign the Agent Card (A2A v1.0 Signed Agent Cards) and verify the signature from a client.

### Lab 5 — Eval-gated canary for a model upgrade (≈2h)

- **Goal:** Release a model change (new `frontier-reasoning` version) to 10% of traffic and promote or roll back automatically.
- **Start state:** `c17/lab5-start` (candidate deployment `frontier-reasoning-next`).
- **Steps:**
  1. Run the frozen C14 suite pairwise (old vs new) offline; the PR must show per-failure-mode pass rates, cost and latency deltas.
  2. Configure APIM weighted backends 90/10 (or an App Configuration flag targeting the Sofia depot).
  3. Write `release/canary-criteria.yaml` *before* starting: thresholds for online eval pass rate, thumbs-down rate, tool error rate, p95 latency, cost per task.
  4. A scheduled GitHub Actions job queries App Insights (KQL over `gen_ai.*` attributes and custom events, keyed by backend) every 30 min and calls a promote or rollback script.
- **Break it:** The instructor swaps the candidate for a deployment with a degraded system prompt that skips citations. The canary must roll back on the groundedness/citation online check, even though HTTP error rates stay flat.
- **Acceptance criteria:** Automatic rollback within 2 evaluation windows in the degraded scenario; automatic promotion in the healthy scenario; release decision log committed.
- **Stretch:** Shadow-mode variant: mirror 5% of traffic to the candidate with no user impact and compare by pairwise judge.

## Kata

**"Capacity and failure card" (30 min, repeat with variations).** Given a one-page scenario (e.g., "Black Friday for Trakia's retail customers: 3× notification volume", "frontier model retired in 60 days, PTU bound to it", "Sweden Central quota exhausted", "customer's agent floods A2A"), produce: (1) the expected TPM/RPM from the C15 baseline; (2) which gateway policy, deployment type or hosting change absorbs it; (3) the exact Bicep or policy diff (≤20 lines); (4) the signal and threshold that tells you it worked. Variation rule: each repetition must change one constraint (budget cap, residency, latency SLO).

## Product increment — Fleet Ops Copilot

Fleet Ops Copilot is deployed to Azure in a `prod-sim` environment matching the baseline RA's security controls:
- hosting: ACA for API/UI/MCP; the Fleet Assistant also runs as a Foundry hosted agent for comparison;
- an APIM AI gateway with per-depot quotas, chargeback metrics, PTU-first failover, scoped semantic cache and gateway content safety;
- private networking with firewall egress allow-listing;
- IaC via azd/Bicep and agents-as-code with immutable versions;
- a narrow A2A `shipment-eta` endpoint for customers;
- a Teams channel;
- an eval-gated canary process for model and prompt changes.

## Factory increment — your agentic SDLC

- `infra/` and `agents/` are first-class code: coding agents may propose changes but CODEOWNERS (platform + security) must approve. `what-if` diffs are posted on PRs.
- Azure MCP Server / Bicep schema tools are available to coding agents for IaC authoring. Agents have *read-only* Azure access in dev; they cannot run `azd up` against `prod-sim` (environment protection rules).
- The canary controller is a scheduled workflow whose decisions are logged and auditable; C19 wires it into the end-to-end pipeline.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Hosting & architecture | One option for everything | Reasoned choice per component | ADR with measured comparison (hosted vs ACA) | Trade-offs incl. preview risk, DR-by-reconstruction tested |
| IaC & identity | Portal clicks, keys | azd + Bicep, managed identities | Keyless, policy-enforced, agents-as-code versions | Clean-room rebuild under 30 min; drift detection |
| AI gateway & capacity | Direct model calls | Token limits + metrics | Claim-keyed quotas, failover proven under load, scoped cache | Capacity plan from telemetry, PTU break-even, abuse cases tested |
| Release safety | Big-bang | Manual canary | Pre-registered criteria, automatic rollback | Rolls back on *semantic* regression with flat error rates; shadow mode |
| Interop | None | Endpoint works | A2A least-agency skill, auth, contract tests | Signed cards, injection-tested, Teams render surfaces hardened |

**Auto-checked:** clean `azd up`/`down` scripts, local-auth scan, reachability matrix, load-test success rate, quota isolation test, A2A contract tests, canary rollback scenario. These artefacts are inputs to **Gate G3**.

## Common pitfalls

- Keying `llm-token-limit` on a client header or IP instead of a validated claim.
- A semantic cache on permission-trimmed or user-specific answers.
- Leaving `versionUpgradeOption` at its default and discovering a model change from a user complaint; forgetting PTU is never auto-upgraded.
- Assuming Foundry gives DR or load balancing. It gives neither.
- Editing agents in the portal "just this once", which breaks DR by reconstruction.
- WAF blocking chat because natural language looks like SQLi, then "fixing" it by disabling the rule set instead of a scoped exclusion.
- Canary judged only on HTTP 5xx; AI regressions are semantic.
- Exposing the whole agent over A2A instead of one narrow skill.
- Building a lab with the full baseline (Firewall, DDoS, Bastion) and burning the cohort's credits. Use the dev profile and tear down nightly.


## References

- Baseline Microsoft Foundry chat reference architecture: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat (implementation: Azure-Samples/microsoft-foundry-baseline)
- Azure AI Landing Zones (**preview**): https://github.com/Azure/AI-Landing-Zones
- Foundry Agent Service at Build 2026 (hosted agents, incoming A2A **preview**, Teams publishing): https://devblogs.microsoft.com/foundry/agent-service-build2026/
- What's new in Microsoft Foundry – Build 2026: https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-build-2026/
- What's new in Microsoft Foundry – July–August 2026 (hosted agents GA 9 Jul 2026; Toolboxes GA; hosted agents with Voice Live GA; Claude Opus 5 GA 24 Jul 2026): https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-july-august-2026/
- What is Microsoft Foundry: https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-azure-ai-foundry
- Foundry SDK overview (.NET packages, endpoints): https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview
- APIM AI gateway capabilities (unified API and Foundry AI gateway **preview**): https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities
- Foundry model retirements: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
- Model router: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-router
- Azure Functions MCP bindings: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-mcp
- MAF Durable extension (**prerelease**): https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions
- ACA dynamic sessions: https://learn.microsoft.com/en-us/azure/container-apps/sessions
- A2A v1.0 announcement: https://linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year
- MAF 1.0 (A2A note): https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/
- Aspire blog: https://devblogs.microsoft.com/aspire/
- CAF AI scenario (least operational responsibility): https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/
- AI Search what's new (index aliases): https://learn.microsoft.com/en-au/Azure/search/whats-new
