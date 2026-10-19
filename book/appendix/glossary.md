# Glossary

Terms as they are used in this course, with the module where each is first taught. Product names, statuses and dates are as of October 2026; where a status is likely to change, verify against current documentation. Course-structure terms point to the handbook chapter that defines them.

## Numbers and symbols

**410 Gone** — The HTTP status a retired Foundry model deployment returns. Retirement turns any hard-coded model name into an outage, which is why code addresses model roles, not model names. (first taught in C0)

## A

**A2A (Agent2Agent) v1.0** — The agent-to-agent protocol (Linux Foundation, stable since 9 April 2026) for calling autonomous agents across trust boundaries via discoverable Agent Cards. Use it when the other side is an agent owned by another team, vendor or tenant; use MCP when it is a tool or data capability. (first taught in C12)

**Acceptance test (human-owned)** — A test written by a human from the requirement before implementation, kept on a protected path that agents may not edit. It is the executable anchor of a spec and the oracle a coding agent must satisfy. (first taught in C4)

**Actionable error** — A tool error message that tells the model what was wrong and how to fix it (for example the expected plate format and a suggested value), so the model can self-correct instead of retrying blindly. (first taught in C3)

**ADR (architecture decision record)** — A short document recording context, at least three options (including "do nothing" where meaningful), the decision, consequences, evidence links and a review date. Course ADRs live in `docs/adr/` and are checked by a linter; A7 adds AI-specific fields such as volatility, reversibility and review triggers. (first taught in C1)

**AG-UI** — An event-based protocol for streaming agent runs (text, tool calls, state, human-in-the-loop requests) to front-ends, originating with CopilotKit. MAF support is preview. (first taught in D4)

**Agent** — An LLM that dynamically directs its own process and tool usage, in contrast to a workflow's predefined code paths. More flexible, less predictable, more expensive and harder to evaluate than a workflow. (first taught in C9)

**Agent registry** — A per-agent record of identity, human sponsor, purpose, autonomy level, risk class, models, tools, knowledge sources, eval and red-team results, status and review date. Course rule: no sponsor, no production. (first taught in A4)

**Agent Skills (SKILL.md)** — An open format for packaging procedural knowledge as a folder with a `SKILL.md` (YAML front matter plus instructions) and optional scripts, loaded by progressive disclosure. (first taught in C4)

**Agentic retrieval** — Retrieval in which an LLM plans subqueries, retrieves in parallel, reranks and merges results. Azure AI Search knowledge bases provide it: extractive retrieval is GA (API 2026-04-01), while query planning and answer synthesis remain preview. (first taught in C7)

**Agents-as-code** — Keeping agent definitions, prompts, tool manifests, guardrail assignments and model bindings in Git and deploying them by pipeline as immutable versions. It is also the basis of disaster recovery by reconstruction. (first taught in C15)

**AGENTS.md** — The open, tool-neutral memory-file format for coding agents. In the course it is the single source of truth; `CLAUDE.md` imports it and `.github/copilot-instructions.md` points to it. (first taught in C4)

**AI Act (EU)** — Regulation (EU) 2024/1689, which regulates AI systems by use-based risk and general-purpose AI models by capability, as amended by the Digital Omnibus, Regulation (EU) 2026/1744. Not legal advice: classification questions go to counsel. (first taught in C18)

**AI gateway** — Azure API Management used as the single policy point for model traffic: token limits and quotas, token metrics for chargeback, semantic caching, backend pools with circuit breaking, content safety, and MCP and A2A governance. (first taught in C15)

**AI management system (AIMS)** — An organisation-wide system of AI policy, roles, risk assessment, impact assessment, controls, audit and continual improvement, as specified by ISO/IEC 42001. (first taught in A6)

**AI Red Teaming Agent** — A Foundry service that wraps PyRIT with 24 attack strategies and reports attack success rate per risk category. Agent-specific risk categories run cloud-only in five regions, and workflow agents, function tools, connected agents and non-Foundry agents are not supported targets. (first taught in C14)

**`allowed_groups` filter** — The GA, portable security-trimming pattern: a filterable field populated at ingestion from the source ACL and filtered at query time with the caller's Entra group IDs. Called `allowedGroups` in some lab code. (first taught in C7)

**Annex III** — The AI Act list of high-risk use cases, including employment and workers management (point 4) and emergency triage (point 5(d)). After the Digital Omnibus, Annex III obligations apply from 2 December 2027. (first taught in C18)

**Approval card** — The UI that presents a pending consequential action for human decision: tool name and raw arguments, effect, reversibility, cost and evidence, with the agent's rationale shown as secondary. Built from typed data, never from the agent's prose. (first taught in D4)

**Art. 50 transparency** — AI Act duties applying from 2 August 2026: tell people they are interacting with an AI system, mark synthetic content in a machine-readable way, and disclose deepfakes. Generative systems already on the market have until 2 December 2026 for marking. (first taught in C18)

**Aspire** — The .NET orchestration stack (13.x) with an AppHost, ServiceDefaults and a dashboard that shows OpenTelemetry traces and marks LLM calls. It is the local trace viewer and the starting point for `azd` deployment. (first taught in C0)

**ASR (attack success rate)** — Successful attacks divided by attempted attacks, reported per risk category and attack strategy. Tracked per release like a regression metric; it trends down with architectural fixes but does not reach zero for classifier-only defences. (first taught in C14)

**Automation bias** — The tendency of human reviewers to accept AI output uncritically. Measured through approval and edit rates, time to decision and seeded "honeypot" items. (first taught in C18)

**Axial coding** — The error-analysis step that groups open-coding notes into a taxonomy of failure modes, with counts. An LLM may propose groupings; a human decides. (first taught in C5)

**azd (Azure Developer CLI)** — The command-line tool that provisions and deploys environments (`azd up`, `azd down --purge`). The course's standard deployment path from Aspire to Azure. (first taught in C0)

**Azure SRE Agent** — An Azure service that investigates incidents across Azure Monitor and Application Insights and can automate remediation, with Reader (read-only) and Privileged modes. Course policy is Reader by default. (first taught in C19)

## B

**Backend pool** — An APIM backend of type Pool that balances across model deployments (round-robin, weighted, priority or session-aware). The standard design puts PTU at priority 1 and PAYG at priority 2 for spillover. (first taught in C15)

**Baseline Microsoft Foundry chat reference architecture** — The Azure Architecture Center baseline: Agent Service in standard setup with a customer VNet, Application Gateway with WAF, Azure Firewall egress, private endpoints and per-component managed identities. Its documented gaps are no per-user conversation authorization, no native load balancing or circuit breaking, and no built-in DR. (first taught in C17)

**Benevolent dictator** — The single domain expert who makes quality calls during error analysis, so labels stay consistent. (first taught in C5)

**BM25** — The standard lexical ranking function. It finds identifiers and rare terms (fault codes, policy numbers, plates) that vector search misses. (first taught in C7)

**BOLA (broken object level authorization)** — Access to another user's object by supplying its ID. Foundry Agent Service does not enforce per-user conversation authorization, so the application must store and check conversation ownership (and tenant) on every call. (first taught in C9)

**BPE (byte-pair encoding)** — A subword tokenization scheme in which frequent character sequences become single tokens. Cyrillic Bulgarian typically needs more tokens per word than English, which affects cost, limits and latency. (first taught in C1)

**Break it** — The lab step that induces a failure on purpose (regression, injection, outage, model swap or cost spike) so you can diagnose and fix it from evidence. (first taught in C0)

**Build / buy / extend** — The architect's choice between buying (M365 Copilot), extending (Copilot Studio), building on PaaS (Foundry Agent Service) and building custom (MAF on Container Apps or Functions), starting from the option with the least operational responsibility that meets the requirements. (first taught in A1)

## C

**C4 model** — Context, container and component diagrams kept as code (Structurizr DSL in the course). The course adds an AI profile, a course convention rather than a standard, that tags model deployments, agents, tools, knowledge bases, guardrails, trust boundaries and untrusted-content flows. (first taught in A2)

**Canary release** — Routing a small share of traffic to a new model, prompt or agent version (APIM weighted backends, Container Apps revision weights or feature flags) and promoting or rolling back on pre-registered thresholds. (first taught in C15)

**Cascade** — A routing design in which a cheap model answers first and escalates to a stronger model when a calibrated confidence signal falls below a threshold. (first taught in D5)

**Chaos engineering (for agents)** — Starting from a steady-state hypothesis and injecting one fault class at a time (tool errors, malformed data, slow tools, 429s, model swaps, `410 Gone`, injected instructions), usually as middleware, to test the whole agent loop. (first taught in D7)

**ChatClientBuilder** — The `Microsoft.Extensions.AI` builder that wraps an `IChatClient` in middleware (logging, caching, function invocation, telemetry, cost tracking). The first `Use…` call is the outermost wrapper, so order matters. (first taught in C2)

**Checkpointing** — Persisting workflow state so a run can resume after a crash. MAF checkpoints at superstep boundaries, and pending human-approval requests are saved and re-emitted on restore. (first taught in C12)

**Circuit breaker** — A mechanism that stops sending requests to a failing backend for a period. The APIM backend circuit breaker can honour `Retry-After` to set the trip duration. (first taught in C15)

**Cloud agent (GitHub Copilot)** — The Copilot agent that takes an issue or Azure Boards work item, works in an ephemeral firewalled environment and opens a draft PR on a `copilot/*` branch; Actions on its PRs need human approval. The naming ("cloud agent" vs "coding agent") is not officially confirmed. (first taught in C4)

**Codebase cognitive debt** — A team that is productive with agents but can no longer reason about its own codebase (Thoughtworks Radar: Caution). Countered by "explain the diff" reviews and unaided katas. (first taught in C4)

**Compaction** — Reducing what stays in an agent's context: clearing used tool results, summarising older turns, or restarting from notes. Compaction invalidates the prompt cache from the first changed token, so do it rarely and in large steps. (first taught in C13)

**Confused deputy** — A server that acts with its own broad privileges on behalf of any caller. The fix is per-request authorization against the caller's identity, or on-behalf-of tokens downstream. (first taught in C16)

**Content capture** — Recording prompt and response content in telemetry. It is opt-in in OpenTelemetry, kept off by default in EU production and, where needed, redacted and justified in the DPIA. (first taught in C2)

**Content Safety (Azure AI)** — Microsoft's moderation classifiers, including Prompt Shields. Groundedness detection and protected-material detection are English-only, and Bulgarian is not among the tested languages, so the course calibrates its own Bulgarian judges. (first taught in C3)

**Content Understanding** — An Azure service (GA November 2025) for structured extraction from documents, images, audio and video, with per-field confidence. Its AI Search skill (GA April 2026) produces Markdown with cross-page tables, image descriptions and semantic chunks. (first taught in C7)

**Context engineering** — The discipline of curating the smallest set of tokens the model needs for the next step, organised in the course as write, select, compress and isolate. (first taught in C13)

**Context rot** — Degradation of model performance as inputs grow longer or contain distractors. Chroma's study of 18 models found focused ~300-token inputs beat ~113k-token inputs for every model family. (first taught in C13)

**Context window** — The single token budget shared by input, output and reasoning tokens. A large window is not an effective window: cost, latency and quality all degrade with length. (first taught in C1)

**Contextual retrieval** — Prepending a 50–100-token LLM-written blurb that situates each chunk in its document before embedding and BM25 indexing. Anthropic measured 35%, 49% and 67% fewer top-20 retrieval failures (with contextual BM25 and a reranker). (first taught in C7)

**Copilot SDK (GitHub)** — `GitHub.Copilot.SDK` and its siblings embed Copilot's agentic engine (planning, tool calls, file edits, streaming, hooks) in your own service, with bring-your-own-key model access. GA since 2 June 2026. (first taught in D6)

**Cost per successful task (CPST)** — Total cost (model tokens, tools, infrastructure, human review) divided by the number of tasks judged successful. Optimisations that cut cost but also cut success can raise it. (first taught in D5)

**Cost per task** — The sum over all model calls in a task of uncached input, cached input and output plus reasoning tokens, each multiplied by its price. A lower per-token price can still mean a higher cost per task. (first taught in C1)

## D

**Data Zone (EU) deployment** — A Foundry deployment type that keeps model processing within the EU data zone. Trakia's default for GDPR residency, in standard (pay-as-you-go) or provisioned form. (first taught in C17)

**Degradation ladder** — A predefined sequence of reduced service levels (cheaper model, retrieval-only mode, cached answers, human handoff) triggered by circuit-breaker state, quota exhaustion or SLO burn. Safety controls are never on the ladder. (first taught in A5)

**Deployer (AI Act)** — The organisation using an AI system under its authority. Deployer duties include use per instructions, competent human oversight, log retention and informing workers before a high-risk system is used at the workplace. (first taught in C18)

**Devcontainer** — A container definition (`.devcontainer/devcontainer.json`) that gives you, Codespaces, CI and coding agents the same environment, so test runs mean the same thing everywhere. (first taught in C0)

**Digital Omnibus on AI** — Regulation (EU) 2026/1744, in force since 27 July 2026. It moved Annex III high-risk obligations to 2 December 2027 and Annex I to 2 August 2028, softened AI literacy, added Art. 4a and a new prohibition from 2 December 2026. (first taught in C18)

**Distillation** — Training a small student model on labels or outputs generated by a larger teacher model, to cut cost and latency at volume. Teacher outputs should be filtered, because teacher errors become student beliefs. (first taught in D1)

**DORA metrics** — Deployment frequency, lead time for changes, change failure rate, failed-deployment recovery time and rework rate. DORA 2025 describes AI as "a mirror and a multiplier" of existing practice. (first taught in C4)

**DPIA (data protection impact assessment)** — The GDPR Art. 35 assessment required for high-risk processing such as systematic monitoring of employees. In the course it covers data flows, lawful basis, minimisation, retention and content capture. (first taught in C18)

**DPO (Direct Preference Optimization)** — A post-training and fine-tuning method that learns directly from preferred and rejected response pairs, without a separate reward model. Use it when quality is easy to judge but hard to demonstrate. (first taught in C1)

**DR by reconstruction** — Disaster recovery for components with no native DR (such as Agent Service): rebuild agent definitions from code, restore data from backups and protect resources with delete locks. A plan is only credible after a timed drill. (first taught in C17)

**Dual LLM pattern** — A prompt-injection design pattern: a privileged LLM plans and calls tools but never sees untrusted text, while a quarantined LLM with no tools reads untrusted text and returns values handled only as symbolic variables. (first taught in C16)

**Durable extension (MAF)** — The prerelease Microsoft Agent Framework extension that hosts agents and orchestrations on Azure Functions or the Durable Task Scheduler, with persisted sessions and human-approval waits that consume no compute or tokens. Requires a GA fallback. (first taught in C12)

## E

**Embedding** — A fixed-length vector that an encoder model produces for a text (or image) so that similar inputs are close. Vectors from different models are incomparable, so changing the embedding model means re-embedding the corpus. (first taught in C6)

**Entra Agent ID** — Microsoft Entra identities for agents (GA), created from agent identity blueprints (wizard in preview), with Conditional Access templates for agents and sponsor lifecycle governance. Verify per-feature status. (first taught in C16)

**Error analysis** — The evals method taught throughout the course: read about 100 real traces, open-code the first failure in each, axial-code the notes into a failure taxonomy, and only then write evaluators for the observed failure modes. (first taught in C5)

**Execution accuracy (EX)** — The core text-to-SQL metric: run generated and golden SQL on a frozen snapshot database and compare result sets, order-insensitively and with numeric tolerance. Exact SQL string match is meaningless. (first taught in C10)

**Explain the diff** — The kata and review practice of explaining every file of an agent-produced PR (what, why, untested behaviour, risk) without asking the agent. It trains the skill tested by the ownership rule. (first taught in C4)

## F

**Factory** — Your own agentic software delivery system (memory files, skills, hooks, custom agents, eval gates, CI agents) grown alongside the product from C0 to C19, D6 and A7. From C4 onward all product work goes through it. (first taught in C0)

**Fairness testing** — Measuring outcome disparities across lawful groups (for example depot, experience band, language), normalised by exposure, with metrics such as flag-rate parity and false-positive-rate parity and bootstrap confidence intervals. Small groups are reported as inconclusive, not as fair. (first taught in C18)

**Few-shot prompting** — Including two to five diverse examples in the prompt to teach format and boundary decisions. Costs tokens on every call and can anchor outputs to example values; measure rather than assume it helps. (first taught in C3)

**Fine-tuning** — Changing model weights with additional training (SFT, DPO, RFT). It shifts behaviour and format; it does not reliably add current facts, which belong in retrieval. (first taught in D1)

**First-pass acceptance** — The share of agent PRs merged with at most one human revision request; a Factory metric for spec and context quality. (first taught in C4)

**Fitness function** — An objective, automated check that an architectural characteristic holds. For AI systems, evals, pass^k, ASR, isolation tests, cost per task and lifecycle checks all act as fitness functions. (first taught in A7)

**Fleet Analyst** — The product's text-to-SQL agent that answers telematics questions with read-only, row-level-secured, parser-validated SQL. (first taught in C10)

**Fleet Assistant** — The product's Microsoft Agent Framework agent with tools, retrieval and human approval for state-changing actions such as booking maintenance. (first taught in C9)

**Fleet Ops Copilot** — The running product you build for Trakia Freight across the whole course, from a streaming chat in C2 to a governed, multi-tenant system. (first taught in C0)

**Foundry Agent Service** — Microsoft Foundry's managed agent runtime: prompt agents (GA), hosted agents (GA since 9 July 2026) and Toolboxes (GA), with memory and routines in preview. (first taught in C9)

**Foundry IQ** — Foundry's managed knowledge layer, built on Azure AI Search knowledge bases, that agents call for permission-aware retrieval. Knowledge bases are GA; Foundry IQ Serverless is preview. (first taught in C13)

**Foundry Local** — On-device inference (GA 9 April 2026) on Windows, macOS on Apple silicon and Linux, with an OpenAI-compatible API and a C# SDK. It is the "swap" target that proves your code is provider-agnostic. (first taught in C0)

**Foundry resource and project** — The current Microsoft Foundry model: one Foundry resource containing projects, with a project endpoint for agents, evaluations and tracing and an OpenAI v1 endpoint for model calls. Hub-based projects are legacy. (first taught in C0)

## G

**Gate (G1, G2, G3)** — The practical mastery exams after C5, C11 and C19: hidden eval suites, a code review against a rubric and, from G2, a design defense, each with an unaided segment and an oral. (first taught in C0)

**Gate stack** — The ordered CI gates in the automated SDLC, cheapest and most deterministic first: build and locked restore, tests, acceptance tests, mutation, evals, safety, code scanning, architecture drift, governance, AI review (advisory), human approval, canary. Rule zero: agents cannot weaken their own gates. (first taught in C19)

**Gate-sensitivity check** — After submission the grader mutates your system in known ways and reruns your own CI eval gate. A gate that stays green under a breaking mutation signals hollow evals. (first taught in C0)

**GenAI semantic conventions (OpenTelemetry)** — The `gen_ai.*` span, metric and attribute names for model calls, agents and tools. All are at "Development" stability and moved to `semantic-conventions-genai` at v1.42.0, so pin the version your dashboards read. (first taught in C2)

**Golden set** — A versioned, stratified regression dataset of cases for known failure modes and core behaviours, with human-owned labels and dev and held-out splits. Not a benchmark of general intelligence. (first taught in C5)

**GPAI model (general-purpose AI model)** — A model regulated under AI Act Chapter V; obligations fall on model providers such as OpenAI, Anthropic and Microsoft. Building a system on such a model makes you the provider of that system. (first taught in C18)

**GraphRAG** — Retrieval that uses an LLM to extract an entity graph and community summaries, answering global, thematic questions that chunk retrieval cannot. Its cost is front-loaded at indexing. (first taught in C13)

**Groundedness** — The property that every claim in an answer is supported by the provided sources (precision against context). Evaluated per claim with a calibrated judge; Azure's built-in groundedness detection is English-only. (first taught in C7)

**Guardrails (Foundry)** — Named collections of controls at intervention points (user input, output, and for agents tool call and tool response, the latter in preview). An agent's guardrail fully overrides its model's guardrail. Guardrails are a second layer, never the first. (first taught in C16)

## H

**Hallucination** — Output not supported by facts or context: factual fabrication, unfaithfulness to provided context, or invented tools and arguments. Structural, because training rewards guessing over abstaining; mitigated systemically, not by asking the model to be accurate. (first taught in C1)

**Hard gate** — A binary, must-pass gate criterion (for example zero permission leaks across all endpoints, pass^3). Failing any hard gate fails the gate regardless of other scores. (see Assessment and gates)

**Hidden eval suite** — The stratified set of cases the grader runs against your submission three times and never shows you; results come back per stratum and failure category. (first taught in C0)

**HITL (human-in-the-loop) approval** — Enforcing in code that a consequential tool call waits for a human decision on the exact action and arguments. A sentence in the system prompt is not HITL. (first taught in C9)

**Hooks** — Deterministic commands that a coding agent runs at lifecycle events (for example `PreToolUse`, `PostToolUse`, `Stop`). Rules that must always hold belong in hooks, not in memory files. (first taught in C4)

**Hosted agent (Foundry)** — Your containerised agent code (MAF, Copilot SDK, LangGraph, Claude Agent SDK or custom) running per session in a Foundry sandbox, exposed via the Responses API or the Invocations protocol. GA since 9 July 2026; egress controls are preview. (first taught in C9)

**Hybrid retrieval** — Running lexical (BM25) and vector search together and fusing the results, usually with reciprocal rank fusion, then reranking. (first taught in C7)

## I

**IChatClient** — The `Microsoft.Extensions.AI` abstraction for chat models. Your code depends on it, not on a provider SDK, so swapping cloud, Foundry Local or any OpenAI-compatible endpoint is a configuration change plus an eval run. (first taught in C2)

**Idempotency key** — A deterministic key sent with a side-effecting call so retries and redeliveries do not repeat the effect. The tool layer derives it; the model never invents it. (first taught in C8)

**Index alias** — An Azure AI Search alias (GA April 2026) that points to a concrete index, enabling blue/green re-indexing without changing clients. (first taught in C6)

**Indirect prompt injection** — Instructions planted in content the system retrieves or receives (documents, emails, tool results, memory, web pages) rather than typed by the user. It needs no account and is not solvable at the model level. (first taught in C7)

**Intended purpose** — Under the AI Act, the use a provider defines for its system; it drives classification and must be enforced technically, for example by restricting outputs or audiences. (first taught in C18)

**ISO/IEC 42001** — The certifiable AI management system standard, with companions ISO/IEC 23894 (AI risk management) and ISO/IEC 42005 (AI impact assessment). (first taught in C18)

## J

**Judge (LLM-as-judge)** — An LLM used as an evaluator for a semantic failure mode. Course rules: binary pass/fail, one judge per failure mode, a required reason, and validation against human labels with TPR and TNR before it gates anything. (first taught in C5)

## K

**K1–K12** — The twelve competency areas of the course, from AI foundations (K1) to architecture and business (K12), each defined at four levels. (see Competency matrix)

**Kata** — A 20–40 minute drill for a recurrent skill, repeated three times in the week with variations. (first taught in C0)

**Kill switch** — A tested way to stop an agent immediately: a feature flag checked before every tool call, terminate APIs that trigger compensations, and disabling the agent's identity so downstream calls fail closed. (first taught in D2)

**Knowledge base (Azure AI Search)** — An AI Search resource that orchestrates retrieval over knowledge sources (indexes, blob, OneLake, web and others). Extractive retrieval is GA with API 2026-04-01; LLM query planning and answer synthesis are preview. (first taught in C7)

**KQL (Kusto Query Language)** — The query language of Azure Monitor, Application Insights and Log Analytics, used for latency, error, token and cost analysis and incident diagnosis. (first taught in C15)

**KV cache** — Stored keys and values for earlier tokens during generation. It explains time to first token versus per-token decode latency, memory use for long prompts, and why prompt caching works. (first taught in C1)

## L

**LazyGraphRAG** — A low-cost GraphRAG variant that replaces LLM extraction with NLP noun-phrase extraction, with indexing cost close to vector RAG and a relevance-test budget as a cost/quality dial. Preview in Microsoft Discovery and Azure Local. (first taught in C13)

**Learn → Do → Break → Fix → Explain** — The shape of every lab: a working baseline, an induced failure, a fix, and a graded written explanation. (first taught in C0)

**Least agency** — The principle behind the OWASP agentic list: give an agent the minimum tools, permissions, autonomy and duration needed for the task. (first taught in C16)

**Least operational responsibility** — The Cloud Adoption Framework heuristic: choose the option that meets the requirements with the least operational burden (SaaS, then PaaS; IaaS is not the default). (first taught in C17)

**Lethal trifecta** — Simon Willison's term for the combination of private data, exposure to untrusted content and the ability to communicate externally, which makes a system exfiltration-capable. Remove at least one leg for any session that touched untrusted content. (first taught in C8)

**`llm-token-limit` / `llm-emit-token-metric`** — APIM AI gateway policies: the first enforces tokens-per-minute limits and token quotas per counter key (tenant, depot, agent); the second emits token metrics with custom dimensions for chargeback. (first taught in C15)

**LoRA (low-rank adaptation)** — Parameter-efficient fine-tuning that freezes the base weights and learns a small low-rank update per adapted matrix, producing adapters of megabytes rather than gigabytes. (first taught in D1)

**Lost in the middle** — The finding that models use information in the middle of long contexts less reliably than information at the start or end. (first taught in C1)

## M

**Managed identity** — An Azure-managed credential for a resource, used for keyless authentication to Foundry, Search, SQL and other services. No secret lands in a tracked file. (first taught in C0)

**McNemar's test** — A paired statistical test on discordant pairs (cases that flipped pass→fail or fail→pass), used to compare two versions on the same eval cases. (first taught in C5)

**MCP 2026-07-28** — The current, breaking MCP revision: stateless (no sessions or handshake), mandatory `server/discover`, Multi Round-Trip Requests, Tasks as an extension, `Mcp-Method`/`Mcp-Name` headers for gateways and W3C trace context in `_meta`. Deprecated features keep working until at least 28 July 2027. (first taught in C8)

**MCP (Model Context Protocol)** — The protocol for exposing tools, resources and prompts from servers to hosts and their agents. Hosts own the LLM and policy; one client connects to each server; transports are stdio and Streamable HTTP. (first taught in C8)

**MCP Apps** — An official MCP extension in which a server declares interactive UI as a `ui://` resource that the host renders in a sandboxed iframe. Use it when a tool's UI must travel with the tool to other hosts. (first taught in C8)

**MEAI (Microsoft.Extensions.AI)** — The .NET abstractions (`IChatClient`, `IEmbeddingGenerator`, `ChatClientBuilder`) and middleware for provider-agnostic AI features. (first taught in C2)

**MEAI.Evaluation** — The `Microsoft.Extensions.AI.Evaluation` libraries: evaluators, response caching, reporting and the `dotnet aieval` tool, running inside xUnit or MSTest. (first taught in C5)

**Memory (agent)** — Information an agent keeps beyond the current window: session/episodic, user (semantic) and procedural. Course rules: scope per tenant and user, store provenance and TTL, validate writes, and make "forget" provable. (first taught in C13)

**Memory poisoning** — Planting instructions or false facts in an agent's memory so they influence later sessions (OWASP ASI06). Mitigated by write-time validation that rejects imperative content and unbacked claims. (first taught in C13)

**MEVD (Microsoft.Extensions.VectorData)** — The .NET abstraction for vector stores (collections, upsert, search), giving portability across stores for common operations. Connector package names are in flux. (first taught in C6)

**Microsoft Agent Framework (MAF)** — `Microsoft.Agents.AI`, the .NET and Python agent framework (1.0 GA, 3 April 2026) built on MEAI: agents, sessions, tools, middleware, context providers, graph workflows and five orchestrations with checkpointing and HITL. Successor to Semantic Kernel agents and AutoGen. (first taught in C9)

**Mixture-of-Experts (MoE)** — An architecture in which a router activates a few expert blocks per token. Memory follows total parameters while compute follows active parameters. (first taught in C1)

**Model lifecycle (Foundry)** — The retirement policy: standard GA models at least 18 months (deprecated at 12), several partner families 12 months, preview models about 90 days, at least 60 days' notice, no extensions, `410 Gone` after retirement, and PTU deployments not auto-upgraded. (first taught in C15)

**Model migration** — Treating a model change as a release: pairwise, per-failure-mode evals on a frozen suite, cost and latency deltas, red-team re-run, a canary with rollback criteria and a go/no-go memo. (first taught in C14)

**Model role** — A named capability slot such as `chat-fast`, `chat-reasoning`, `embedding` or `chat-local`, mapped to a deployment in configuration (`models.json`). Code addresses roles, never model names. (first taught in C0)

**Model router (Foundry)** — A Foundry deployment that routes each prompt across a pool of models in Balanced, Quality or Cost mode. The latest version auto-updates; its effective context window is the smallest in the pool. (first taught in C15)

**Mutation testing** — Making small changes (mutants) to production code and checking that tests fail. Mutation score (killed ÷ killed + survived) measures the fault-detection power of tests, which coverage cannot. Stryker.NET in the course. (first taught in C11)

## N

**nDCG@k** — Normalised discounted cumulative gain: a retrieval metric that rewards relevant results near the top and supports graded relevance. (first taught in C6)

**NIST AI RMF** — The NIST AI Risk Management Framework 1.0 (Govern, Map, Measure, Manage) with its Generative AI Profile (AI 600-1). There is no 2.0; a CSA agentic profile exists as a draft. (first taught in C18)

**Nondeterminism** — Run-to-run variation in model output, present even at temperature 0 in production serving. Tests therefore assert schemas, properties, verdicts and pass rates, never exact strings. (first taught in C1)

## O

**OBO (on-behalf-of)** — An OAuth flow in which a service exchanges the user's token for a downstream token, so downstream APIs enforce the user's own permissions. Never pass the user's inbound token straight through. (first taught in C8)

**Open coding** — The error-analysis step of writing a free-text note on the first (most upstream) failure in each trace. (first taught in C5)

**OpenTelemetry (OTel)** — The vendor-neutral standard for traces, metrics and logs. Traces captured with OTel keep any observability platform replaceable. (first taught in C2)

**OWASP Top 10 for Agentic Applications** — The 2026 list of autonomy risks, ASI01 (agent goal hijack) to ASI10 (rogue agents). Used with the LLM list to map threats and red-team findings. (first taught in C16)

**OWASP Top 10 for LLM Applications (2025)** — The list of application risks around a model, LLM01 (prompt injection) to LLM10 (unbounded consumption). (first taught in C3)

**Ownership rule** — You own what you merge: if you cannot explain code you submitted, the agent-direction criterion scores Novice regardless of eval results. (first taught in C0)

## P

**Pairwise judge** — An LLM judge that compares two outputs and picks the better one with a reason. Positions are swapped and only consistent verdicts count, to cancel position bias. (first taught in C14)

**pass@k** — The probability that at least one of k attempts succeeds; answers "can it ever do this?". (first taught in C5)

**pass^k** — The probability that all k attempts succeed, from τ-bench; the reliability metric for production behaviour. Gate safety items use pass^3. (first taught in C5)

**Plan-then-execute** — A prompt-injection design pattern in which the plan (tools and fixed parameters) is fixed before untrusted data is read, so untrusted data can influence values but not which tools run. (first taught in C16)

**Playwright test agents** — Playwright's planner, generator and healer agents that explore an app, write tests and repair failing ones. A [Node] component of the course. (first taught in C11)

**Procedural memory** — Memory of how to do tasks, such as patterns distilled from successful agent trajectories, stored as skills or instruction items. (first taught in C13)

**Production-readiness review (PRR)** — The capstone milestone that checks reproducible deploy, eval gates, the hidden acceptance suite, load, cost, DR drill, migration rehearsal, security, privacy, the AI Act risk file, the runbook and the Factory. (see Capstone)

**Progressive disclosure** — Loading only skill metadata into context until a skill becomes relevant, then loading its full instructions. (first taught in C4)

**Prompt caching** — Provider reuse of the KV cache for an identical prompt prefix at a discount. Requires a static-first layout: system prompt, tool definitions, examples and stable context before dynamic content, with no timestamps or IDs early. (first taught in C1)

**Prompt injection** — Text that causes a model to follow instructions it should treat as data. Unsolved at the model level, because instructions and data share one token stream; handled by architecture (least privilege, typed outputs, design patterns), with classifiers as a second layer. (first taught in C3)

**Prompts as code** — Treating prompts as versioned artefacts in `prompts/` with an ID, semantic version, hash, owner and target model role, changed only by PR with eval results. (first taught in C3)

**Property-based testing** — Stating properties that must hold for all inputs and letting a framework (FsCheck, CsCheck) generate inputs and shrink failures to minimal counterexamples. (first taught in C11)

**Protected paths** — Repository paths agents may not change without human code-owner approval, such as acceptance tests, golden sets, eval thresholds, workflows and infrastructure. (first taught in C4)

**Provider (AI Act)** — The organisation that develops an AI system and places it on the market or puts it into service under its own name. Trakia is provider and deployer of its internal system, and provider when it sells the product to other fleets. (first taught in C18)

**PTU (provisioned throughput units)** — Reserved model throughput at a fixed hourly cost, giving predictable latency for a stable baseline. PTU deployments are not auto-upgraded, and break-even against PAYG depends on sustained utilisation. (first taught in C15)

**PyRIT** — Microsoft's open-source Python red-teaming toolkit (orchestrators, converters, scorers) pointed at an HTTP target; wrapped by the AI Red Teaming Agent. A [Python] component of the course. (first taught in C14)

## Q

**Qrels** — Relevance judgements: for each query, the set of relevant document or chunk IDs, used to compute retrieval metrics. (first taught in C6)

**Quantization (weights)** — Storing model weights at lower precision (INT8, INT4) to cut memory; formats include GGUF, GPTQ, AWQ and ONNX INT4. Loss concentrates on rare tokens and classes. (first taught in D1)

## R

**RAG (retrieval-augmented generation)** — Retrieving evidence and generating an answer grounded in it, with citations. Retrieval selects the evidence; long context reasons over it. For corpora under roughly 200k tokens, a cached prompt may beat RAG. (first taught in C7)

**Reasoning effort** — The parameter that controls how many hidden reasoning tokens a reasoning model spends. Higher effort helps multi-step reasoning, rarely helps lookup or extraction, and costs tokens, context and latency. (first taught in C1)

**Reasoning tokens** — Hidden tokens a reasoning model generates before answering. They are billed at output price and consume the shared context budget; some are encrypted and cannot be audited. (first taught in C1)

**Recall@k** — The share of relevant items that appear in the top k results; the primary retrieval metric for RAG. (first taught in C6)

**Red teaming** — Adversarial testing of a system with automated scans and manual attacks (in Bulgarian and English), reported as ASR per category, with mitigations ranked architecture-first. (first taught in C14)

**Red-team swap** — The capstone milestone in which each team attacks another team's staging environment for 48 hours under rules of engagement, and triages findings against its own system. (see Capstone)

**Reranker** — A second-stage model (a cross-encoder such as the Azure AI Search semantic ranker or Cohere rerank) that rescores the top hybrid candidates before a few are sent to the model. (first taught in C7)

**Responses API** — The successor to the Assistants API, exposed by both the Foundry project endpoint and the OpenAI v1 endpoint; it can hold conversation state server-side. (first taught in C0)

**RFT (reinforcement fine-tuning)** — Managed fine-tuning with a grader that scores responses; suited to tasks where many answers are valid and quality can be scored reliably. Graders must be tested against adversarial responses. (first taught in C1)

**RLS (row-level security)** — A SQL Server security policy that filters rows by a predicate, in the course driven by `SESSION_CONTEXT` set read-only by the API from the user's token. (first taught in C10)

**RRF (reciprocal rank fusion)** — Fusing ranked lists by summing 1 / (k + rank), with k = 60 in the original paper. Uses ranks only, so lexical and vector scores need no calibration. (first taught in C7)

**Rug pull** — An MCP server changing a tool's definition after you reviewed and approved it. Defended by pinning and hashing tool definitions and blocking on drift. (first taught in C8)

**Rule of Two (Agents)** — Meta's rule that an agent session should combine no more than two of untrustworthy input, sensitive data or systems, and state changes or external communication; with all three, require human approval or redesign. (first taught in C9)

## S

**Saga** — Modelling a long-running plan as steps each with a compensation, run in reverse on failure. Irreversible steps go last and behind approval. (first taught in D2)

**Security trimming** — Applying permissions as a retrieval filter before content reaches the model, never by instructions in the prompt. (first taught in C7)

**Semantic cache** — A cache that returns a stored answer when a new prompt is semantically close to a cached one (APIM `llm-semantic-cache-*`, backed by Azure Managed Redis). Only safe for answers that are not user-, time- or permission-specific, and keyed by tenant, role and language. (first taught in C15)

**Semantic layer** — Curated database views with business names, definitions, units and owners (for example an `analyst` schema) that the text-to-SQL agent queries instead of raw tables. (first taught in C10)

**SFT (supervised fine-tuning)** — Training on prompt and ideal-response demonstrations. (first taught in C1)

**Shadow deployment** — Running a new version on mirrored or sampled traffic without showing its output to users, then comparing offline. No user impact, double cost. (first taught in C15)

**SLO (service level objective)** — A target for a service level indicator over a window. For agents the course separates behavioural SLOs (task success, safety) from infrastructure SLOs (availability, latency). (first taught in C15)

**Slopsquatting** — Registering package names that AI models predictably hallucinate. A USENIX 2025 study found 19.7% of 2.23M AI code samples referenced non-existent packages; defended by allow-lists, lockfiles and package-age rules. (first taught in C4)

**Spec-driven development** — Using written specs to drive agent implementation. The course position is spec-anchored with an executable anchor (human-written acceptance tests and eval cases), and ceremony proportional to the change. (first taught in C4)

**Spotlighting** — Marking untrusted input so the model can tell it is data (delimiting, datamarking or encoding). It lowers attack success cheaply but is never the only control. (first taught in C3)

**STRIDE** — The threat-modelling categories Spoofing, Tampering, Repudiation, Information disclosure, Denial of service and Elevation of privilege, applied per element of an AI system's data-flow diagram. (first taught in C16)

**Structured outputs** — Schema-constrained generation (JSON Schema, constrained decoding) that guarantees the output conforms to a schema, but not that its values are correct. Make unknowns representable and validate in code anyway. (first taught in C3)

**Sub-agent** — A separate agent session with its own context, tools and permissions, used for isolation (for example a diagnostics sub-agent returning a short finding) or for specialist work in coding agents. (first taught in C4)

**Synthetic data (dimension tuples)** — Generating test cases by defining dimensions, hand-writing about 20 tuples, generating more, then turning each tuple into natural language in a separate step. Synthetic data shows coverage, not production frequency. (first taught in C5)

**System card** — A per-system document of what the system does and does not do, models, evaluation summary, limitations, oversight, data handling and contact, written for non-technical readers. (first taught in A6)

## T

**Tau-bench (τ-bench)** — A benchmark of tool-agent-user interaction with simulated users, domain policies and database end-state checks, which introduced pass^k; τ²-bench adds dual control. (first taught in C5)

**Temperature** — A sampling parameter that rescales logits: low is near-greedy, high is flatter. Not a creativity dial for facts; reasoning models often ignore it. (first taught in C1)

**Text-to-SQL** — Generating SQL from a natural-language question. In the course it is a read-only, validated tool over a semantic layer, with parser validation, row-level security, row caps and execution-accuracy evals. (first taught in C10)

**Threat register** — The output of threat modelling: per threat, the element, STRIDE class, OWASP mapping, trifecta flag, mitigation, the test that proves it, and residual risk with an owner. (first taught in C16)

**Token** — The unit models read, generate and bill. Context windows, rate limits, prices and output limits are all in tokens; the provider's reported usage is the bill. (first taught in C1)

**Tool calling** — The model returning a structured request to call a tool, which your code validates and executes before returning the result. The model never executes anything. (first taught in C3)

**Tool definition pinning** — Hashing each MCP tool's name, description and schema at approval time and blocking or alerting when a live definition changes. (first taught in C8)

**Tool poisoning** — Malicious instructions hidden in a tool's description, visible to the model but usually not to the user. (first taught in C8)

**Top-p (nucleus sampling)** — Sampling from the smallest set of tokens whose cumulative probability reaches p. Tune temperature or top-p, not both. (first taught in C1)

**TPM (tokens per minute)** — The rate limit on a model deployment and the hard ceiling on model spend you control; budgets only alert. (first taught in C0)

**TPR / TNR** — True positive rate and true negative rate of an LLM judge against human labels. Course convention: Pass is the positive class, so TNR is the "catches failures" number. Reported separately because classes are imbalanced. (first taught in C5)

**Track-critical area** — A competency area in which a track requires Expert level at graduation (marked ● in the competency matrix). (see Competency matrix)

**Trajectory eval** — Evaluating an agent's path (right tools, valid arguments, order, forbidden actions, efficiency) from its spans, preferably by asserting invariants rather than exact paths. (first taught in C9)

**Trakia Freight** — The fictional Plovdiv logistics company (about 400 trucks, 600 drivers, depots in Plovdiv, Sofia and Varna) for which you build Fleet Ops Copilot. All data is synthetic. (first taught in C0)

**TrakiaBench** — The internal coding-agent benchmark you build in D6 from your own repository's history, with hidden tests, contamination control and pass^k. (first taught in D6)

**TrakiaOps** — The product's SQL Server 2025 database of vehicles, pseudonymised drivers, trips, telematics events, work orders, customers and shipments. (first taught in C0)

**TrakiaSim** — The τ-bench-style simulation harness (simulated users, policies, resettable environment, end-state graders) you build in D7 to measure agent reliability. (first taught in D7)

**Transparency Note** — A document explaining a system's capabilities, limitations and appropriate use, in the style Microsoft publishes for its services; you write one for your own system. (first taught in C18)

**TTFT (time to first token)** — The delay before the first output token, driven by network, prefill of uncached input and provider queueing. Streaming improves perceived latency, not total time or cost. (first taught in C1)

## U

**Unaided segment** — The short, proctored part of each gate done without AI assistance, such as predicting behaviour from traces or writing a design note. (see Assessment and gates)

## V

**VECTOR type (SQL Server 2025)** — The SQL vector data type and `VECTOR_DISTANCE` function, GA, keeping vectors next to rows with transactional consistency and row-level security. Exact search is recommended below about 50k vectors after predicates. (first taught in C6)

**Voice Live** — Azure's managed voice orchestration (speech recognition, turn detection, interruption, speech synthesis) around a model or agent; Voice Live prompt agents and hosted agents with Voice Live are GA. (first taught in D3)

**Volatility tag** — The Low, Med or High tag in each module header indicating how quickly its content dates. (see Course overview)

## W

**WAF for AI workloads** — The Azure Well-Architected Framework's AI guidance, with ten design areas mapped to the five pillars and an Assessment Review Tool used as the review instrument for every architecture package. (first taught in A2)

**Workflow** — LLMs and tools orchestrated through predefined code paths (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer). The default for known processes, with autonomy confined to bounded nodes. (first taught in C9)

**Worktree** — A separate Git working directory on its own branch, used to run parallel coding agents on independent tasks without interfering. (first taught in C4)
