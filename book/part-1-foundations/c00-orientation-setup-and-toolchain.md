# C0 — Orientation, setup & toolchain

> **Level:** Part 0 — Orientation · **Duration:** 6h (theory 30% / labs 70%) · **Prerequisites:** Git, HTTP/REST, SQL, one unit-test framework in any language; an Azure subscription where you can create resource groups; a GitHub account · **Volatility:** High (tool versions, portal UX, SDK names)

## Why this matters

Trakia Freight's IT lead gives you a laptop, a GitHub org and an Azure subscription on Monday and expects a working "Ask Fleet Ops" prototype by Friday. Teams that skip setup discipline lose that week in predictable ways: one developer is on .NET 9 and another on .NET 10; someone pastes an API key into `appsettings.json` and pushes it; a forgotten test deployment of a frontier reasoning model runs a load test over the weekend and burns the quarter's budget; a sample copied from a 2025 blog targets the retired Assistants API and a hub-based project that only exists in "Foundry (classic)". None of these are AI problems, but in AI projects they cost more because every call is metered and the platform renamed half of itself in 2025–2026.

This course is long (~475h) and the platform moves monthly. You will rebuild your environment several times (new laptop, Codespaces, a colleague joining your capstone team, a CI runner, a coding agent's sandbox). The only sustainable answer is **environment as code**: a devcontainer, pinned SDKs and packages, configuration-only model selection, keyless authentication, and budget alerts created by script, not by memory. That same environment is what your coding agents (C4) will run in, so its reproducibility directly limits how much you can safely delegate.

Experts also set up *feedback* on day one: a cost alert that fires before damage is done, an Aspire dashboard that shows every model call, and a CI job that builds and tests the empty solution. In this course you are graded on how you direct and verify agents (from C4 on); the factory you start here is the foundation of that grade.

## Learning outcomes

By the end of C0 you can:

1. **Provision** a reproducible dev environment (devcontainer or local) with .NET 10, Aspire 13.x, Node.js LTS and Python, and prove it with a scripted `doctor` check.
2. **Create** a Microsoft Foundry resource and project (new resource/project model, not hub-based), deploy two model roles ("fast small model", "frontier reasoning model") and call them with keyless (Entra ID) authentication.
3. **Configure** Azure cost guardrails: a resource-group budget with actual and forecast alerts, and per-deployment rate limits as a hard ceiling.
4. **Run** a model locally with Foundry Local and explain when local inference is the right lab default.
5. **Explain** the lab repo structure, tagging scheme and version-pinning policy (`global.json`, central package management, `models.json`), and find the start state of any lab.
6. **Read** the C#, Python and Node.js you will meet in this course well enough to modify samples (non-.NET developers: C# crash-course checkpoints passed).
7. **Describe** how mastery gates (G1–G3) work: hidden eval suites, code review, design defense.

## Concepts

### The course workflow: Product + Factory, gated by evals

You grow one product, **Fleet Ops Copilot** for the fictional Plovdiv logistics company **Trakia Freight** (~400 trucks, ~600 drivers, depots in Plovdiv, Sofia and Varna), and in parallel your **Factory** — your own agentic SDLC (memory files, custom agents, hooks, eval gates, CI agents). Every module ends with a product increment and a factory increment. From C4 onward, product work is done *through* the factory: you specify, constrain and verify; agents type.

**Vehicle identifiers (course-wide convention).** Two vehicle identifiers recur in every module and must not be confused: the **fleet/vehicle ID** (`VehicleId`, e.g. `TRK-0471`), assigned by TrakiaOps and stable for the vehicle's life — the key that tools, traces and logs use; and the **registration plate** (`VehicleReg`, canonical form Cyrillic with spaces, e.g. `РВ 4471 АК`), which drivers type in Cyrillic or Latin look-alikes, is normalised to Cyrillic in code (C1, C3), can change over a vehicle's life and is resolved to the fleet ID by lookup. Tools return and accept both, but joins, logs and approvals use the fleet ID.

Each lab follows **Learn → Do → Break → Fix → Explain**: a working baseline, an induced failure, a fix, and a short written explanation (ADR, postmortem or eval report). The explanation is graded.

**Gates.** After Level 1 you sit **Gate G1** (specified separately). Gates use (a) hidden eval suites run against your product branch, (b) a code review against a rubric (correctness, security, observability, cost, eval coverage), and from G2 (c) a design defense. Passing means your evals clear thresholds on cases you have *not* seen, so overfitting prompts to your own golden set does not help. You can resit; feedback is specific.

### Environment as code

- **Devcontainer** (`.devcontainer/devcontainer.json`): the same image runs in VS Code Dev Containers, GitHub Codespaces and the CI runner. Coding agents (Copilot cloud agent, Claude Code in Actions) get an equivalent environment, which is why their test runs mean something.
- **Pinned SDK** (`global.json`) with `rollForward: latestFeature` within .NET 10 — allows patch/feature-band updates, blocks an accidental major jump.
- **Central Package Management** (`Directory.Packages.props`, `ManagePackageVersionsCentrally=true`): one place where every NuGet version is pinned. Nightly CI (run by the course team, and later by you in C19) bumps versions on a branch and runs all lab solutions; that is how the course keeps up with preview churn without breaking you mid-module.
- **Model config, not model code**: labs reference model *roles*. `models.json` / `appsettings.json` maps roles (`chat-fast`, `chat-reasoning`, `embedding`) to deployment names. Model names change monthly (GPT-6 Sol/Luna/Astra and Claude Opus 5.5 all shipped in September 2026); your code must survive that as a config change. Foundry GA models are deprecated at 12 months and retired at 18 (partner models typically 12), with ≥60 days notice, and retired models return `410 Gone` — so hard-coded names are a production defect, not a style issue.

### Microsoft Foundry, as of October 2026

- "Azure AI Foundry" is now **Microsoft Foundry**; "Azure AI Services" is now **Foundry Tools**.
- One **Foundry resource** contains **projects**. Hub-based projects survive only in the "Foundry (classic)" portal. Do not follow tutorials that create a hub.
- Endpoints you will use:
  - Project endpoint: `https://<resource>.services.ai.azure.com/api/projects/<project>` (Responses API, agents, evaluations) via `Azure.AI.Projects` 2.0 GA family.
  - OpenAI v1 endpoint: `https://<resource>.openai.azure.com/openai/v1/` via the plain `OpenAI` .NET package — no dated `api-version` query strings.
- The **Assistants API retired on 26 Aug 2026**; use the Responses API.
- **Do not install** the preview `Azure.AI.Projects.OpenAI` alongside `Azure.AI.Extensions.OpenAI` — Microsoft warns of ambiguous types.

### Keyless authentication from the start

Use **Microsoft Entra ID** (`DefaultAzureCredential` locally via `az login`; managed identity in Azure; OIDC federated credentials in GitHub Actions). Assign yourself the minimal data-plane role on the Foundry resource (the role name for calling models in the new Foundry RBAC model — verify against current documentation; Foundry evaluations require Entra ID and do not accept API keys). API keys are allowed only for Foundry Local / local OpenAI-compatible endpoints. Rule: *no secret ever lands in a tracked file*; `dotnet user-secrets` for anything unavoidable, GitHub secret scanning on.

### Cost guardrails: three layers

1. **Budgets with alerts** (Cost Management) on the course resource group: e.g. €40/month, alerts at 50% actual, 80% actual, 100% forecast. Budgets *alert*; they do not stop spend.
2. **Deployment rate limits** (tokens-per-minute quota per deployment): the only hard ceiling you control at the model layer. Set the frontier model deployment low (a few thousand TPM is plenty for labs).
3. **Habits**: default to the fast small model or Foundry Local; use the frontier role only when a lab says so; delete load-test deployments; MEAI.Evaluation response caching (C5) for repeated eval runs.

Rough numbers to calibrate intuition (list prices from research notes; verify against the Azure pricing page before quoting to learners): a "fast small" class model at ~$0.10/$0.50 per million input/output tokens vs a frontier class at ~$10/$50 is a **100× spread**. A 50-case eval suite × 3 runs × ~2k tokens per case ≈ 300k tokens: cents on the small model, a few dollars on the frontier model, much more with high reasoning effort. Per-token price is not per-task cost (C1).

### Foundry Local

**Foundry Local went GA on 9 Apr 2026**: on-device inference on Windows, macOS (Apple silicon) and Linux x64; ONNX Runtime with automatic GPU/NPU/CPU selection; OpenAI-compatible API including the Responses format; C# SDK `Microsoft.AI.Foundry.Local`; curated models (Phi, Qwen, gpt-oss, Mistral, DeepSeek, Whisper). Use it for offline work, cheap iteration and as the "swap" target that proves your code is provider-agnostic (C2). Caveat: small local models are weaker at tool calling and structured output — that is a lesson, not a bug.

### Why Python and Node.js in a .NET course

Everything is C# except a bounded, declared set marked **[Python]**: PyRIT / AI Red Teaming Agent local scans (C14, C16), Foundry cloud-evaluation authoring samples (`azure-ai-evaluation`), fine-tuning data prep and the interactive-training preview (D1), Agent Framework "Labs" packages, RAGAS. **Node.js** is needed for Playwright test agents (`npx playwright init-agents`, C11), AG-UI/React front-ends (D4), and many MCP servers and CLIs. The certification market also matters: AI-103 (the AI-102 successor) assumes Python, so *reading* fluency is a career asset.

### Misconceptions to unlearn

- "Budgets cap my spend." They alert. Quotas/rate limits and deleting deployments cap spend.
- "A key in user-secrets is safe enough for CI." CI uses OIDC federation; no long-lived secrets.
- "The latest preview package is better." Labs pin versions; you upgrade deliberately, behind a green eval suite.
- "Any Foundry tutorial works." Hub-based, Assistants-API and `api-version`-dated samples are legacy as of 2026.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| .NET 10 SDK, C# | Primary runtime/language | GA (LTS) | Pin in `global.json` |
| Aspire 13.6 | Local orchestration, OTel dashboard | GA | Renamed from ".NET Aspire"; dashboard marks LLM calls when MEAI `UseOpenTelemetry` is on |
| Visual Studio 2026 (v18.x) / VS Code | IDE | GA | VS 2026 has Copilot `@Test` agent (GA v18.3) and "Agent (Preview)" built on the Copilot CLI SDK |
| Dev Containers / GitHub Codespaces | Reproducible env | GA | Same image locally, in Codespaces and CI |
| GitHub + GitHub Actions | Source, CI, agents | GA | Azure DevOps interop covered in C19 |
| Azure CLI, `azd` | Provisioning | GA | Bicep for IaC from C17 |
| Microsoft Foundry (resource + project) | Models, agents, evals, tracing | GA | Hub projects = "Foundry (classic)" only |
| `Azure.AI.Projects` / `.Agents` / `Azure.AI.Extensions.OpenAI` 2.0.0 | Foundry .NET SDK | GA | Don't mix with preview `Azure.AI.Projects.OpenAI` |
| `OpenAI` .NET package | `/openai/v1/` endpoint | GA | Some APIs need `#pragma warning disable OPENAI001` |
| `Azure.Identity` | Entra auth | GA | `DefaultAzureCredential` |
| Foundry Local (`Microsoft.AI.Foundry.Local`) | Local inference | GA (9 Apr 2026) | Learn page carries no GA label — verify against current documentation |
| Foundry Toolkit for VS Code | Model playground, local models | GA | Appears to supersede "AI Toolkit" (rename unconfirmed) |
| Node.js LTS | Playwright agents, MCP servers, front-ends | GA | Pin via `.nvmrc` / devcontainer feature (course choice: current LTS line — verify) |
| Python 3.12+ with `uv` | [Python] red-teaming, cloud evals, fine-tuning prep | GA | Course choice; pinned in `scripts/python/pyproject.toml` |
| GitHub Copilot (agent mode), Claude Code, Codex | Coding agents (C4) | GA | Paid plan needed for some features |

## Labs

### Lab 1 — Environment as code (≈1.25h)

- **Goal:** A devcontainer-based environment that builds and tests the empty Fleet Ops solution, identical on your machine, in Codespaces and in CI.
- **Start state:** lab repo `trakia-fleetops`, tag `c0/lab1-start` (solution skeleton, no devcontainer).
- **Steps:**
  1. Clone and inspect the repo layout:
     ```
     trakia-fleetops/
       .devcontainer/           # you create in this lab
       .github/workflows/       # ci.yml (build+test), nightly.yml (course team)
       data/                    # TrakiaOps SQL scripts, docs corpus (BG+EN), mock API OpenAPI specs
       docs/adr/                # ADRs; template + checklist in README.md (you write from C1)
       evals/                   # golden datasets, error-analysis notes (C5)
       prompts/                 # versioned prompt templates (C3)
       scripts/doctor.sh        # environment check
       scripts/python/          # the only Python in the repo [Python]
       src/FleetOps.AppHost/    # Aspire AppHost
       src/FleetOps.ServiceDefaults/
       src/FleetOps.Core/       # domain + AI services
       src/FleetOps.Api/        # minimal API
       src/FleetOps.Cli/        # console client
       tests/FleetOps.Tests/    # xUnit unit tests
       tests/FleetOps.Evals/    # eval tests (C5)
       global.json  Directory.Packages.props  models.json  AGENTS.md (C4)
     ```
  2. Create `.devcontainer/devcontainer.json`:
     ```jsonc
     {
       "name": "trakia-fleetops",
       "image": "mcr.microsoft.com/devcontainers/dotnet:10.0", // verify current tag
       "features": {
         "ghcr.io/devcontainers/features/node:1": { "version": "lts" },
         "ghcr.io/devcontainers/features/python:1": { "version": "3.12" },
         "ghcr.io/devcontainers/features/azure-cli:1": {},
         "ghcr.io/devcontainers/features/github-cli:1": {},
         "ghcr.io/devcontainers/features/docker-in-docker:2": {}   // Aspire containers, SQL Server
       },
       "postCreateCommand": "dotnet restore && dotnet tool restore && ./scripts/doctor.sh",
       "forwardPorts": [17000, 5080],
       "customizations": { "vscode": { "extensions": ["ms-dotnettools.csdevkit", "GitHub.copilot-chat"] } }
     }
     ```
  3. Pin the SDK and packages:
     ```json
     // global.json
     { "sdk": { "version": "10.0.100", "rollForward": "latestFeature" } }  // set to the course release's SDK
     ```
     ```xml
     <!-- Directory.Packages.props (excerpt) -->
     <Project>
       <PropertyGroup><ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally></PropertyGroup>
       <ItemGroup>
         <PackageVersion Include="Microsoft.Extensions.AI" Version="10.5.0" />  <!-- course release pin; verify -->
         <PackageVersion Include="Azure.Identity" Version="..." />
         <PackageVersion Include="OpenAI" Version="..." />
       </ItemGroup>
     </Project>
     ```
  4. Write `scripts/doctor.sh` that prints and asserts: `dotnet --version` major = 10, `node --version` ≥ pinned LTS major, `python --version` ≥ 3.12, `az account show` succeeds, `aspire --version` or the Aspire templates are installed (verify the current Aspire CLI install path), `docker info` succeeds. Exit non-zero on any failure.
  5. Run `dotnet new` is *not* needed — the skeleton exists. Run `dotnet build` and `dotnet test` inside the container.
  6. Add `.github/workflows/ci.yml` that uses the same devcontainer (e.g. `devcontainers/ci` action) to run `./scripts/doctor.sh --ci && dotnet test`.
- **Break it:** Change `global.json` to `9.0.100` with `rollForward: disable` and rebuild. Then add a package with a floating version (`Version="10.*"`) to a project file directly. Observe the CPM error (`NU1008`-style) and the SDK resolution failure.
- **Acceptance criteria:** `./scripts/doctor.sh` exits 0 in the container; `ci.yml` green on your fork; `Directory.Packages.props` is the only place versions appear (CI step `grep -R "Version=" src tests --include=*.csproj` returns nothing).
- **Stretch:** Open the repo in a Codespace and time from "Create" to green `dotnet test`. Add a prebuild configuration to cut it.

### Lab 2 — Foundry resource, project, two deployments, keyless call (≈1.25h)

- **Goal:** A Foundry resource + project in an EU region with a "fast small" and a "frontier reasoning" deployment, called from C# with Entra ID.
- **Start state:** `c0/lab2-start`.
- **Steps:**
  1. Create a resource group `rg-trakia-<you>` in an EU region that offers your chosen models (check model/region availability; Sweden Central and France Central frequently appear in Microsoft regional lists — verify for the current models).
  2. Create the **Foundry resource** and a **project** in the new portal (ai.azure.com), *not* a hub. Optional IaC path: Bicep `Microsoft.CognitiveServices/accounts` (kind `AIServices`) with project management enabled and a child `projects` resource — verify exact properties against current docs before teaching.
  3. Deploy two models, recording only *roles* in config:
     ```json
     // models.json
     {
       "roles": {
         "chat-fast":      { "provider": "foundry", "deployment": "fleet-fast",      "notes": "cheap/fast class" },
         "chat-reasoning": { "provider": "foundry", "deployment": "fleet-reasoning", "notes": "frontier reasoning class" },
         "chat-local":     { "provider": "foundry-local", "model": "phi-family-alias" }
       }
     }
     ```
     Use Global/Data Zone Standard deployments; set the reasoning deployment's TPM limit low.
  4. Assign your user the data-plane role required to call models (verify role name), then `az login`.
  5. Call the OpenAI v1 endpoint with a bearer token:
     ```csharp
     #pragma warning disable OPENAI001
     using Azure.Identity;
     using OpenAI;
     using System.ClientModel.Primitives;

     var credential = new DefaultAzureCredential();
     var client = new OpenAIClient(
         new BearerTokenPolicy(credential, "https://ai.azure.com/.default"), // token scope: verify against the SDK overview
         new OpenAIClientOptions { Endpoint = new Uri($"https://{resource}.openai.azure.com/openai/v1/") });

     var chat = client.GetChatClient("fleet-fast");
     var result = await chat.CompleteChatAsync("Reply with exactly: Trakia Freight online.");
     Console.WriteLine(result.Value.Content[0].Text);
     Console.WriteLine($"in={result.Value.Usage.InputTokenCount} out={result.Value.Usage.OutputTokenCount}");
     ```
     (C2 wraps this in `IChatClient`; here you only prove connectivity and auth.)
- **Break it:** (a) Remove your role assignment and re-run — read the 401/403 body. (b) Call a deployment name that does not exist — 404. (c) Put a fake key in `appsettings.json`, commit to a branch and push to your fork; observe GitHub secret scanning / push protection (if enabled on your plan) and then *rotate* — the lesson is the rotation, not the detection.
- **Acceptance criteria:** `dotnet run --project src/FleetOps.Cli -- ping --role chat-fast` and `--role chat-reasoning` both print a reply and token usage; `git grep -nE "(api[-_]?key|Ocp-Apim)" -- ':!*.md'` finds nothing; no key-based auth configured on the Foundry resource client path.
- **Stretch:** Disable local (key) auth on the Foundry resource and confirm everything still works.

### Lab 3 — Cost guardrails by script (≈0.5h)

- **Goal:** Budget alerts and rate limits created reproducibly.
- **Start state:** `c0/lab3-start` (contains `scripts/budget.sh` skeleton).
- **Steps:**
  1. Create a monthly resource-group budget with notifications at 50% and 80% *actual* and 100% *forecasted* to your email, via `az consumption budget create` or Bicep (`Microsoft.Consumption/budgets`) — verify current CLI command group; portal fallback documented in the script header.
  2. Tag every resource with `course=trakia`, `owner=<you>`, `module=c0` so Cost Management can group spend by module.
  3. Record deployment TPM limits in `docs/cost-guardrails.md`: what each role costs per 1M tokens (list price, date-stamped), current TPM limit, who may raise it.
  4. Write `scripts/teardown.sh` that deletes load-test deployments and lists anything tagged `ephemeral=true`.
- **Break it:** Compute (on paper, then with a 30-line C# script) what a runaway loop calling the reasoning deployment at its TPM limit would cost in 48 hours at list price. Compare with your budget. This is why the rate limit, not the budget, is the real control.
- **Acceptance criteria:** `az consumption budget list -g rg-trakia-<you>` (or equivalent) shows the budget with three notifications; all resources carry the three tags (checked by `scripts/doctor.sh --azure`); `docs/cost-guardrails.md` exists with a date stamp.
- **Stretch:** Add an Azure Policy assignment that denies resources without the `owner` tag in the course resource group.

### Lab 4 — Foundry Local and the language primers (≈1.25h)

- **Goal:** Run a small model locally behind an OpenAI-compatible endpoint; pass the C#, Python and Node reading checkpoints.
- **Start state:** `c0/lab4-start`.
- **Steps:**
  1. Install Foundry Local (Windows/macOS/Linux x64) and run a small Phi-family or Qwen model from the curated catalog (CLI command names: verify against current Foundry Local docs). Note which execution provider (CPU/GPU/NPU) it picked.
  2. Point the same `OpenAIClient` code from Lab 2 at the local endpoint (local endpoints accept a dummy key). Compare latency and answer quality for the prompt "Summarize in one sentence: Truck РВ 4521 КН reported a coolant leak near Stara Zagora." in English and Bulgarian.
  3. **C# crash-course checkpoints** (for non-.NET developers; ~30 min with the pointers below): records and `init`; nullable reference types; `async`/`await`, `IAsyncEnumerable<T>` and `await foreach`; LINQ; generics; `System.Text.Json` with source generation; dependency injection (`IServiceCollection`, lifetimes); minimal APIs (`app.MapPost`); options pattern (`IOptions<T>`); xUnit `[Fact]`/`[Theory]`. Exercise: make the provided `TripSummaryTests` pass by implementing a record and an async method.
  4. **Python primer [Python]** (~15 min): create the env with `uv sync` in `scripts/python/`, run `hello_eval.py` (reads a JSONL file, prints pass rate). Learn to read: virtual envs, `pyproject.toml`, `async def`, type hints, Pydantic models, pytest.
  5. **Node primer** (~10 min): `npm ci` in `tools/node/`, run `npx playwright --version`; understand `package.json`, `package-lock.json`, `npx`.
- **Break it:** Ask the local model for a JSON object with three fields for 10 different incident sentences. Count invalid JSON outputs. Keep the number — you will reduce it in C3.
- **Acceptance criteria:** `dotnet run --project src/FleetOps.Cli -- ping --role chat-local` succeeds offline (network disabled); `dotnet test --filter Category=C0Primer` green; `scripts/python/hello_eval.py` prints a pass rate.
- **Stretch:** Measure tokens/s locally vs cloud for a 300-token answer; record in `docs/local-vs-cloud.md`.

## Kata

**"Fresh machine in 20 minutes"** (20–30 min, repeat 3×). Start from a clean Codespace (or a teammate's laptop) and reach: devcontainer up, `doctor.sh` green, `ping` succeeding against `chat-fast` and `chat-local`, Aspire dashboard reachable. Variations: (1) a different Azure subscription (forces you to parameterize resource names); (2) no Azure access at all — local-only path; (3) a CI runner — make `ci.yml` do it unattended with OIDC. Track your time; target < 15 min on the third run.

## Product increment — Fleet Ops Copilot

Nothing user-facing yet: the solution skeleton builds, `FleetOps.Cli ping` reaches every model role, and `models.json` defines the roles that every later module uses. The TrakiaOps SQL Server 2025 database and the BG/EN document corpus are restored locally (Aspire runs SQL Server in a container) and verified by `doctor.sh --data`.

## Factory increment — your agentic SDLC

Dev environment as code (devcontainer, pinned SDK and packages), CI building and testing inside the same container, keyless auth for humans and CI, cost alerts and rate limits, a teardown script. This is the sandbox your coding agents inherit in C4 — a coding agent can only verify its work if `dotnet test` behaves identically for it.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Reproducibility | Works only on own machine | Devcontainer builds; manual steps remain | Devcontainer + CI green; versions centrally pinned | Codespace-to-green < 15 min, prebuilds, doctor checks data + Azure |
| Security of credentials | Keys in config | Keys in user-secrets | Entra ID everywhere except local endpoints | Local auth disabled on resource; OIDC in CI; push protection verified |
| Cost control | No alerts | Budget exists | Budget + TPM limits + tags | Budget + limits + tags + policy + teardown script, with a written runaway-cost estimate |
| Platform currency | Uses hub/Assistants samples | New resource/project model | Correct endpoints and SDK families | Can explain why each legacy pattern is legacy and how to detect it in a sample |
| Gate readiness (outcome 7) | Thinks gates re-run the visible tests | Names the three gate components (hidden suite, code review, design defense from G2) | Explains hidden suites, 3-run nondeterminism handling (mean for quality, pass^3 for safety), the unaided segment and the ownership rule | Explains the gate-sensitivity check and why thresholds are relative to the reference plus an absolute floor |

**Auto-checked:** `doctor.sh` (env, Azure, data), CI status on the `c0` branch, absence of secrets (`gitleaks` step), tag compliance, presence of `docs/cost-guardrails.md`.

**Gate-readiness check (10 min, auto-marked quiz, pass 5/6, retake allowed):** six short questions answered from [gates.md](../start-here/assessment-gates.md): (1) what the three G1–G3 assessment components are; (2) why overfitting prompts to your own golden set does not help; (3) how the hidden suite handles nondeterminism (mean of 3 runs vs pass^3 for safety items); (4) what is allowed in the unaided segment; (5) what the ownership rule means for code your agent wrote; (6) what the gate-sensitivity check does to *your* CI eval gate. Misconceptions are revisited in the C5 debrief before G1.

## Common pitfalls

- Creating a **hub-based project** from an old tutorial; it lands in "Foundry (classic)" and later labs' endpoints won't match.
- Choosing a region where your models aren't offered, then scattering deployments across regions.
- Leaving `rollForward` unset and silently picking up a different SDK on the CI runner.
- Assuming the budget will stop spend; it won't.
- Mixing `Azure.AI.Projects.OpenAI` (preview) with `Azure.AI.Extensions.OpenAI` (GA) — ambiguous type compile errors.
- Running Docker-dependent Aspire resources without Docker-in-Docker in the devcontainer.
- On Apple silicon or ARM Windows, assuming an x64-only container image works; check image architectures.


## References

- What is Microsoft Foundry (resource/project model, renames): https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-azure-ai-foundry
- Foundry SDK overview (.NET packages, endpoints, OPENAI001, ambiguous-type warning): https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview
- Assistants API retirement notice: https://learn.microsoft.com/en-us/answers/questions/5790094/will-azure-openai-assistants-api-specifically-be-d
- Foundry model retirements policy: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
- Foundry Local GA: https://devblogs.microsoft.com/foundry/foundry-local-ga/ ; What is Foundry Local: https://learn.microsoft.com/en-us/azure/foundry-local/what-is-foundry-local
- .NET AI ecosystem decision guide: https://learn.microsoft.com/en-us/dotnet/ai/dotnet-ai-ecosystem
- Aspire blog (13.x): https://devblogs.microsoft.com/aspire/
- Models sold directly by Azure (regions, context windows): https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure
- AI-103 credential (Python assumption): https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-apps-and-agents-developer-associate/
