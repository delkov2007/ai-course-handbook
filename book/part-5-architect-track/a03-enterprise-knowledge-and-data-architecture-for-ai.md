# A3 — Enterprise knowledge & data architecture for AI

> **Level:** Expert — AI Solution Architect track · **Duration:** 16h (theory 30% / labs 70%) · **Prerequisites:** A2; C6, C7, C10, C13 (vector search, permission-aware RAG, text-to-SQL, Foundry IQ/GraphRAG) · **Volatility:** High (AI Search agentic retrieval, knowledge sources, permission propagation and Purview integration are moving GA/preview lines)

## Why this matters

**What separates an expert architect from a proficient one here:** a proficient architect can build a good RAG pipeline for one application. An expert designs a *knowledge platform*: many sources, many consumers (agents, apps, tenants), one set of guarantees about permissions, freshness, residency and isolation. They know precisely which guarantees are GA, which are preview, and which the application must enforce itself.

In C7 you built permission-aware RAG for Trakia's ~1,500 documents. Enterprise rollout and SaaS change the problem in kind, not just in size:

- **Sources multiply.** SharePoint HR libraries, workshop manuals in blob storage, incident history in SQL, telematics at ~5M rows, and per-customer contracts.
- **Consumers multiply.** The Fleet Assistant, the Fleet Analyst, the incident workflow, Copilot Studio agents and customer fleets' own agents via A2A.
- **Tenants appear.** A SaaS fleet's documents and telematics must *never* reach another fleet's answers, embeddings, caches, memories or eval datasets.

Most production RAG failures are data and retrieval failures, not model failures: stale versions, missing ACL filters, tables destroyed by naive parsing, distractors. In a multi-tenant platform each of these becomes a potential data breach.

Experts make the store choice an ADR backed by a bake-off. They treat ingestion as a product with SLAs. They default to the portable, GA permission pattern (query-time trimming on a filterable groups field) and adopt native ACL propagation only where it is available and tested. They design tenant isolation with *tests that try to break it*. They keep structured data behind governed tools rather than "RAG over rows". And they decide on GraphRAG with a cost model, not on hype.

## Learning outcomes

1. **Design** a layered knowledge platform (sources → ingestion → enrichment → stores → retrieval APIs/knowledge bases → consumers) with explicit freshness, permission, residency and isolation guarantees per layer.
2. **Distinguish** GA from preview in Foundry IQ and Azure AI Search agentic retrieval. **Design** production paths on GA features, with preview features behind flags.
3. **Choose and justify** a vector store (AI Search vs Azure SQL / SQL Server 2025 vs Cosmos DB vs PostgreSQL) using a bake-off with recall, latency and cost at three scale points.
4. **Build** an ingestion pipeline at scale with layout-aware parsing, contextual chunks, dedup, incremental updates and blue/green re-indexing via index aliases.
5. **Implement and test** permission enforcement: query-time trimming (GA pattern) vs native ACL propagation (preview), including group-overage handling and Purview labels.
6. **Design** EU data residency for every place data lands: model processing, indexes, caches, traces, memory and eval datasets.
7. **Decide** when GraphRAG or LazyGraphRAG is warranted, and **govern** structured-data access (semantic layer, read-only text-to-SQL, RLS, query budgets).
8. **Design and verify** multi-tenant data isolation with automated cross-tenant leak tests.

## Concepts

### 1. The knowledge platform as layers with guarantees

| Layer | Trakia components | Guarantees to specify |
|---|---|---|
| Sources | SharePoint (HR, policies), Blob (manuals, scanned notes), SQL `TrakiaOps`, tenant uploads, web (regulation summaries) | Owner, classification, residency, change feed |
| Ingestion & enrichment | Indexers / custom .NET pipeline (MEDI), Content Understanding / Document Layout skills, contextualisation, embeddings | Freshness SLA (e.g., policy change visible ≤ 4h), parse quality, cost per 1k pages |
| Stores | AI Search indexes, SQL VECTOR, Cosmos DB | Isolation model, ACL fields, encryption, backup / rebuild time |
| Retrieval | AI Search knowledge bases (agentic retrieval), Foundry IQ, MAF `TextSearchProvider`, SQL tools | Permission enforcement point, latency p95, budgets |
| Consumers | Agents, Copilot Studio, A2A partners | Which consumer may query which knowledge, under which identity |

The platform owner publishes the guarantees, and each consumer's ADR states which guarantees it relies on. This is how the knowledge platform becomes a product (A4 operating model) instead of five teams each building their own RAG.

### 2. Foundry IQ and AI Search agentic retrieval: what is GA

- **Foundry IQ knowledge bases are GA.** **Foundry IQ Serverless is preview.** Foundry IQ is built on AI Search agentic retrieval and is described as turning enterprise content into reusable, permission-aware knowledge bases.
- **Agentic retrieval** (knowledge bases orchestrating knowledge sources) is **GA with API `2026-04-01` for extractive retrieval**:
  - GA knowledge sources: search index, blob, OneLake, web (web needs a model reference).
  - Query planning, answer synthesis and reasoning effort remained preview at GA. The `2026-08-01-preview` API adds `retrievalReasoningEffort: "auto"` (escalates to LLM planning only when needed), stored runtime and output budgets, per-source `resultsProcessing: "none"`, `neverQuerySource`, SSE streaming and query hints.
  - **Preview knowledge sources:** File, Azure SQL, Fabric Data Agent/Ontology, **MCP Server**, Work IQ, and remote or indexed SharePoint.
- **Billing.** From `2026-04-01`, semantic ranker and agentic retrieval require separate billing consent (`knowledgeRetrieval=standard`). Model this in A1's cost model.
- **Index features that matter architecturally:**
  - scalar (int8, ~4×) and binary (up to ~28×) quantization with rescoring;
  - Matryoshka truncation;
  - max 4,096 dimensions;
  - **index aliases GA (Apr 2026)**, which enable blue/green re-indexing;
  - multivector fields (preview).
- **AI Search tiers.** Tier choice determines partitions/replicas, storage, the maximum number of indexes per service and SLA eligibility. Tier limits are decisive for "index per tenant" designs. Verify current tier limits and prices before teaching; they are not reproduced here.

**Design rule:** build production retrieval on the GA extractive path. Put planning and synthesis behind a feature flag and admit them only when your C14 retrieval evals (recall@k, nDCG, the Foundry Document Retrieval evaluator's Fidelity/holes) show a gain that is worth the latency and cost.

### 3. Vector store selection

| Criterion | Azure AI Search | Azure SQL DB / SQL Server 2025 | Cosmos DB for NoSQL | Azure Database for PostgreSQL (pgvector) |
|---|---|---|---|---|
| Status | GA (vector, hybrid, semantic ranker, KBs) | `VECTOR` type GA everywhere; **DiskANN index GA in Azure SQL DB / MI / Fabric, preview in SQL Server 2025** | Vector + BM25 + hybrid RRF GA (May 2025) | Not verified in course research — verify |
| Retrieval sophistication | Highest: hybrid, semantic rerank, agentic retrieval, skills, connectors | Exact kNN (`VECTOR_DISTANCE`) recommended < ~50k vectors after predicates; ANN via `SELECT TOP (N) WITH APPROXIMATE`; hybrid = full-text + vector composed manually (verify) | Hybrid RRF native | Rich ecosystem; hybrid via tsvector/extensions |
| Source of truth | Copy (sync pipeline) | Vectors next to rows; transactional; RLS reuse | Next to documents/state | Next to rows |
| Permissions | Filter fields (GA); native ACL propagation (preview) | **RLS** (mature) | Partition / filter | RLS |
| Cost model | Fixed SU tiers | Rides on existing DB capacity | RU/s | vCore |
| Portability | Azure-specific API (MEVD connector) | T-SQL, MEVD | MEVD | Highest |

**Decision heuristics for Trakia:**

- **Policy, manual and contract corpus** (unstructured, multi-source, BG/EN, semantic rerank needed, SharePoint ACLs) → AI Search / Foundry IQ.
- **Incident history narratives** that already live in `TrakiaOps` and must respect the same row-level security as the Fleet Analyst → **SQL vectors next to the rows**. No sync pipeline, one permission model.
- **Agent memory and conversation-adjacent semantic lookups** → Cosmos DB, which already holds standard-setup state.
- Use `Microsoft.Extensions.VectorData` (MEVD) so the bake-off runs the same code against each store. The connectors now ship under the `CommunityToolkit.VectorData.*` package names (verify per store).

**Misconception to unlearn: "one vector database for everything".** Multiple stores are fine *if* each has a clear reason, a single owner and evals. What you must not have is the same content in two stores with different permission models.

### 4. Ingestion pipelines at scale

- **Parsing.**
  - The **Document Layout skill is GA** (Sep 2025).
  - The **Content Understanding skill is GA** (Apr 2026): Markdown output, cross-page tables, image descriptions, semantic chunking. Content Understanding SDKs are GA including .NET.
  - The GenAI Prompt skill for image verbalisation is GA (Apr 2026).
  - For Trakia's maintenance manuals (tables, diagrams) and scanned delivery notes, naive text extraction is the leading root cause of wrong answers. Measure it in C7/C13 terms before scaling.
- **Contextual chunks.** Prepending 50–100 tokens of LLM-written document context per chunk cut top-20 retrieval failures by 35% (embeddings), 49% (+ contextual BM25) and 67% (+ reranker) in Anthropic's study, at ~$1.02 per million document tokens with prompt caching. Run it as a **Batch** job: Batch is ~50% cheaper, but verify the current Azure Batch discount and turnaround.
- **Dedup.** No managed Azure feature was found. Use content hashing plus near-duplicate detection (MinHash or embedding similarity) in pipeline code. Duplicates and stale versions are the "distractors" that Chroma shows degrade answers.
- **Freshness.** Use change feeds and incremental indexing. Freshness-aware retrieval and per-run incremental SharePoint ACL sync are preview. State a **freshness SLO** per source and monitor indexer lag.
- **Embedding model changes require full re-embedding.** With index aliases (GA), you build `manuals-v2` in parallel, run the retrieval eval suite against it, then switch the alias. One practitioner estimate puts re-embedding and re-indexing at ~20% of monthly inference spend (unverified). Calculate yours.
- **Scale arithmetic.** Use it to sanity-check the design. For SaaS year 3, assume 40 tenants × ~3,000 documents × ~25 chunks ≈ 3M chunks, at 1,536 dimensions × 4 bytes ≈ 18 GB of raw vectors before quantization. Binary quantization brings that toward ~0.7 GB plus the full-precision copy if you keep originals for rescoring. This arithmetic decides tiers and whether `discardOriginals` is acceptable.

### 5. Permissions: query-time trimming vs native propagation

**GA, portable pattern: query-time trimming.**
- Store a filterable `allowed_groups` (and `tenant_id`) collection on every chunk at ingestion.
- At query time, the API derives the groups from the caller's Entra token and applies `search.in` filters.
- Enforcement happens in **your** code path, which needs tests on every path (agents, tools, Copilot Studio via MCP, A2A).

**Native propagation (preview).**
- ADLS Gen2 permissions with identity-based query filtering, the SharePoint indexer with ACLs (extended Jun 2026 to pages, lists, site groups and incremental sync), and blob/OneLake `ingestionPermissionOptions`. All are **preview**.
- Elevated read for admin ACL debugging is preview.
- Work IQ uses OBO with a customer-owned Entra app.
- Benefit: no duplicated ACL logic.
- Costs: preview SLAs, sync lag, and the need to verify behaviour per source.

**Sharp edges you must design for:**

- **Group overage.** When a user belongs to many groups, the token may not carry them all (Entra overage behaviour; verify the current thresholds). Your trimming code must resolve groups through Graph and cache them with a TTL.
- **Revocation latency.** A permission removed in SharePoint becomes effective in your index only after the next sync. You measured this in A1 Lab 4. State it as a guarantee ("≤ 1h") or design around it, e.g., re-check at citation time for sensitive collections.
- **Purview sensitivity labels.** Label indexing is preview, and labels are returned in knowledge-base retrieve responses (`sensitivityLabelInfo`, preview). Use labels to *exclude* "Highly Confidential" content from agent-accessible indexes altogether, which is safer than trimming per query.
- **Never trim in the prompt.** "Only use documents the user may see" in a system prompt is not access control.

### 6. Data residency in the EU

Residency must be designed for every place data *lands* or is *processed*. Index storage is only one of them:

- **Model inference.** Global Standard deployments may process prompts in any region. **Data Zone (EU) Standard/Provisioned** keeps processing within the EU data zone. The model router runs on Global Standard and Data Zone Standard. Verify per model and region availability.
- **Indexes, Cosmos DB, SQL, Storage**: in the EU region pair you chose (A5 for DR).
- **Semantic cache** (Redis in the APIM gateway, A4): this is prompt and response content. It needs the same residency and tenant scoping.
- **Traces.** OTel content capture is opt-in. Keep it off by default in EU production, redact in the Collector, and document the setting in the DPIA (A6).
- **Agent memory** (Foundry memory is preview; MAF `MemoryFileStore`): per-user and per-tenant scope, TTL and "forget".
- **Eval datasets and red-team logs** contain real questions. Classify them like production data.
- **Safety services.** Content Safety groundedness detection is English-only and available only in some regions (France Central, Sweden Central, UK South among them). The AI Red Teaming Agent's agent-specific risk categories run cloud-only in 5 regions (incl. France Central, Sweden Central, Switzerland West). Region choice constrains which safety tooling you can use.

### 7. GraphRAG and LazyGraphRAG

- **GraphRAG** extracts entities and relations with an LLM, builds community summaries, and answers global, "sensemaking" questions ("what are the recurring themes across 3 years of incident reports?").
- **LazyGraphRAG** defers the LLM work:
  - indexing cost ≈ vector RAG (~0.1% of full GraphRAG);
  - matched GraphRAG Global Search quality at >700× lower query cost;
  - a relevance-test budget acts as an explicit cost/quality dial;
  - available in Microsoft Discovery and Azure Local (preview); open-source availability not stated, so verify.
- **MAF** exposes graph retrieval through a **Neo4j GraphRAG provider**.

**Decision rule:**
- Use graph retrieval only for global/thematic or multi-hop entity questions that hybrid + rerank demonstrably fails on your eval set.
- For Trakia that is "patterns across incidents by route, vehicle model and supplier part" for fleet managers and the SaaS analytics tier. It is *not* "what does policy 4.2 say".

### 8. Structured data: semantic layer and text-to-SQL governance

The Fleet Analyst (C10) answers questions over `TrakiaOps`. At enterprise and SaaS scale:

- **Semantic layer.** Business metrics ("fuel efficiency", "unplanned downtime day", "on-time delivery") are defined *once*, as governed views or functions with descriptions, units and owners. The agent is grounded on the semantic layer's metadata, not on raw schema. Two analysts must get the same "downtime" number. This is a data-architecture deliverable, not a prompt.
- **Text-to-SQL is a tool, not RAG over rows:**
  - read-only login;
  - an allow-listed schema (views only);
  - **RLS** with `SESSION_CONTEXT` carrying tenant and role, set by the tool host and never by the model;
  - parse and validate the SQL (single SELECT, no cross-tenant objects);
  - query timeout and row cap;
  - cost guard;
  - full audit (who, question, SQL, rows returned).
- **Evaluate with SQL metrics.** RAGAS ships execution-based Datacompy and SQL-equivalence metrics. Your C10 golden queries become regression tests for every semantic-layer change.
- AI Search's Azure SQL and Fabric knowledge sources are **preview**. That reinforces the tool approach for transactional data.

### 9. Multi-tenancy data isolation

**Isolation models for the SaaS product:**

| Model | Index | SQL | Cosmos | When |
|---|---|---|---|---|
| Pooled | Shared index, mandatory `tenant_id` filter | Shared DB + RLS on `TenantId` | Shared container, partition key = tenant | Standard tier, many small fleets |
| Bridge | Index per tenant on shared service | Database per tenant (elastic pool) | Container per tenant or hierarchical partition keys (verify) | Mid-size fleets, per-tenant re-index and delete |
| Silo | Dedicated Search service | Dedicated server | Dedicated account | Enterprise fleets with contractual isolation or residency demands |

Microsoft's multitenant AI/ML guidance adds the model dimension:

- **Model tenancy options:** tenant-specific, shared pre-trained, shared tenant-trained (needs consent and de-identification), and tuned shared per tenant.
- **Rule:** treat models with the same sensitivity as their training data.
- **Noisy neighbours:** per-resource limits may force scale-out across resources.
- The page does not cover per-tenant grounding indexes or token quotas. Those come from your design and APIM (A4).

**Isolation must extend to:**
- embeddings, which are derived personal and business data;
- semantic cache keys;
- memory stores;
- trace content;
- eval sets.

Tenant deletion must be complete and provable ("offboarding certificate"). This is easiest in bridge/silo designs.

**Prove isolation with tests, not diagrams.** Seed each test tenant with **canary documents** containing unique marker strings. Run every retrieval path (agent, tool, A2A, Copilot Studio via MCP, cache) as tenant B. Fail the build if any tenant-A marker appears in results, answers, cached responses or traces visible to B.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| Azure AI Search, API `2026-04-01` | Indexes, hybrid, KBs (extractive) | GA | Billing consent for semantic ranker / agentic retrieval |
| Azure AI Search, API `2026-08-01-preview` | Query planning, `auto` reasoning effort, budgets, streaming | **Preview** | Feature-flag only |
| Foundry IQ knowledge bases | Managed knowledge layer for agents | GA; Serverless **preview** | New knowledge sources preview |
| Document Layout skill / Content Understanding skill | Layout-aware parsing | GA (Sep 2025 / Apr 2026) | CU SDKs GA incl. .NET |
| SharePoint / ADLS / blob / OneLake ACL ingestion | Native permission propagation | **Preview** | Teach as "preferred where available" |
| Purview sensitivity-label indexing, `sensitivityLabelInfo` | Label-aware retrieval | **Preview** | |
| Index aliases | Blue/green re-indexing | GA (Apr 2026) | |
| SQL Server 2025 / Azure SQL `VECTOR`, `VECTOR_DISTANCE`, `AI_GENERATE_EMBEDDINGS` | Vectors next to rows | GA | DiskANN: GA Azure SQL DB / MI / Fabric; **preview SQL Server 2025** |
| Cosmos DB for NoSQL vector + full-text + hybrid RRF | Memory / state-adjacent retrieval | GA | |
| `Microsoft.Extensions.VectorData` + `CommunityToolkit.VectorData.*` | Store-agnostic code | GA (abstractions) | Verify connector package names / versions |
| MEDI (`Microsoft.Extensions.DataIngestion`) | .NET ingestion pipeline | Status unverified — verify | Fallback: plain pipeline code |
| MAF `TextSearchProvider`, Neo4j GraphRAG provider | Agent retrieval integration | GA (MAF 1.0); provider status verify | |
| LazyGraphRAG | Low-cost graph retrieval | Preview (Microsoft Discovery, Azure Local) | OSS status: verify |
| RAGAS | SQL & RAG metrics **[Python]** | OSS | Datacompy, SQL equivalence |
| Foundry Document Retrieval evaluator | Fidelity, nDCG@3, holes | Available (verify GA/preview per evaluator) | |

## Labs

### Lab 1 — Vector store bake-off and knowledge platform ADR (≈4h)

- **Goal:** Choose stores per knowledge domain with measured recall, latency and cost at three scale points.
- **Start state:** branch `a3/start`. Contains the C7 golden retrieval set (200 questions with qrels, stratified: factoid, table, multi-hop, BG, EN, abstention, permission-restricted), the MEVD harness and `scale-gen` (synthetic tenant corpora).
- **Steps:**
  1. Implement one `IRetriever` over MEVD with three backends:
     - AI Search (hybrid + semantic ranker);
     - Azure SQL (`VECTOR` + DiskANN, full-text composed);
     - Cosmos DB (hybrid RRF).
     ```csharp
     // Same record type, three stores (verify connector package names).
     public sealed class ChunkRecord
     {
         [VectorStoreKey] public string Id { get; set; } = default!;
         [VectorStoreData(IsIndexed = true)] public string TenantId { get; set; } = default!;
         [VectorStoreData(IsIndexed = true)] public string[] AllowedGroups { get; set; } = [];
         [VectorStoreData(IsFullTextIndexed = true)] public string Text { get; set; } = default!;
         [VectorStoreVector(Dimensions: 1536)] public ReadOnlyMemory<float> Embedding { get; set; }
     }
     ```
  2. Load three scale points: Trakia (~1,500 docs), SaaS year 1 (5 tenants), SaaS year 3 (40 tenants, ≈ 3M chunks via `scale-gen`). Use quantization where the store supports it.
  3. Measure recall@10, nDCG@10, p50/p95 latency at 20 concurrent queries, and the monthly cost from the A1 cost model (fixed tier vs capacity-based).
  4. Write **ADR-A3-001 "Knowledge stores per domain"**: policies, manuals and contracts; incident narratives; memory. Include the "one content, one permission model" rule.
- **Break it:** At year-3 scale, disable rescoring on binary-quantized vectors. Record the recall drop and decide whether `discardOriginals` is acceptable per domain.
- **Acceptance criteria:**
  - Bake-off report generated by `dotnet run -- report` with all metrics per store × scale.
  - The chosen design meets recall@10 ≥ 0.90 on the policy domain.
  - The ADR passes the linter and cites the report.
  - The cost figures reconcile with the A1 model (± 10%).
- **Stretch:** Add a knowledge base (agentic retrieval, GA extractive) over the AI Search index. Compare against plain hybrid. Then flip to `auto` reasoning effort (preview API) behind a flag and record the latency and cost deltas.

### Lab 2 — Ingestion at scale with blue/green re-indexing (≈3.5h)

- **Goal:** Make ingestion a product with an SLA: parse quality, freshness and safe model changes.
- **Start state:** `a3/lab2-start`. Contains 300 maintenance-manual PDFs (tables, diagrams), 200 scanned delivery notes and the policy library with versions.
- **Steps:**
  1. Build the pipeline: Content Understanding (Markdown, cross-page tables) → chunk → contextualise (Batch job, small model) → dedup (hash + embedding similarity) → embed → upsert into `manuals-v1` behind alias `manuals`.
  2. Add freshness metadata (`sourceModified`, `ingestedAt`, `version`) and an indexer-lag metric to App Insights. Define the SLO: policy change visible ≤ 4h.
  3. Run the table-heavy subset of the golden set: naive extraction vs Content Understanding vs + contextual chunks.
  4. Change the embedding model, which requires a full re-embed. Build `manuals-v2` in parallel, run the retrieval eval gate, then switch the alias atomically. Keep v1 for rollback.
- **Break it:** Change the embedding model *in place* (same index, new model for new chunks only). Observe the dimension mismatch, or worse, silently mixed vector spaces if the dimensions match. Your eval gate must catch the recall collapse before the alias switch.
- **Acceptance criteria:**
  - Table-question recall improves ≥ 15 points over naive extraction.
  - The alias switch is gated by CI on retrieval evals (fails below threshold).
  - Rollback works in < 5 minutes (timed).
  - The freshness dashboard shows the SLO.
  - Cost per 1k pages is computed and added to the A1 model.
- **Stretch:** Process the scanned delivery notes with a Content Understanding prebuilt analyser into structured fields stored in SQL rather than the vector index. Justify why that is the right home for them.

### Lab 3 — Permission enforcement and revocation (≈3h)

- **Goal:** Prove that permissions hold on every retrieval path and that revocation latency is known.
- **Start state:** `a3/lab3-start`. Contains an Entra test tenant with role groups (dispatcher, mechanic, HR, auditor), a user with 250+ groups (overage) and a SharePoint HR site.
- **Steps:**
  1. Implement query-time trimming: groups from the token, falling back to a Graph lookup on overage, cached with a 15-min TTL. Apply the filter in the retriever and assert that it cannot be bypassed: the filter is built server-side and the model never supplies it.
  2. In parallel, configure the SharePoint knowledge source with ACL ingestion (preview) on a copy of the index.
  3. Write a **permission test matrix** (role × document class × path: Fleet Assistant, MCP knowledge tool, Copilot Studio via MCP). Expect 0 leaks.
  4. Revoke a user's access to an HR document. Measure the time until each path stops returning it: trimming path (your group-cache TTL) vs native ACL path (sync interval).
  5. Exclude Purview "Highly Confidential" documents from agent indexes at ingestion (label indexing is preview; fallback: metadata from the SharePoint column).
- **Break it:** The instructor adds a new "search_all_documents" diagnostic tool that calls the retriever without the trimming wrapper. Your matrix must fail. Then refactor so that the unfiltered retriever is not injectable outside the admin assembly (architecture test with NetArchTest/ArchUnitNET).
- **Acceptance criteria:**
  - The permission matrix passes with 0 leaks.
  - The overage user is resolved correctly.
  - Revocation latency per path is documented as a platform guarantee.
  - The architecture test prevents unfiltered retriever use.
- **Stretch:** Compare answer quality between the two permission approaches on the HR subset. Write the go/no-go criteria for moving to native ACL when it reaches GA.

### Lab 4 — Multi-tenant isolation with canary leak tests (≈3h)

- **Goal:** Implement pooled and bridge isolation for SaaS and *prove* isolation across all data surfaces.
- **Start state:** `a3/lab4-start`. Two synthetic tenants, `rhodope-haulage` and `danube-logistics`, each with documents, telematics and canary markers (`CANARY-RH-7f3a…`).
- **Steps:**
  1. **Pooled:** shared index with a mandatory `tenant_id` filter injected by the tenant-context middleware (from token `tid` → tenant registry), plus SQL RLS on `TenantId`:
     ```sql
     CREATE FUNCTION sec.fn_tenant(@TenantId uniqueidentifier)
     RETURNS TABLE WITH SCHEMABINDING AS
     RETURN SELECT 1 AS ok WHERE @TenantId = CAST(SESSION_CONTEXT(N'TenantId') AS uniqueidentifier);
     CREATE SECURITY POLICY sec.TenantPolicy
       ADD FILTER PREDICATE sec.fn_tenant(TenantId) ON dbo.Incidents,
       ADD BLOCK PREDICATE  sec.fn_tenant(TenantId) ON dbo.Incidents
       WITH (STATE = ON);
     ```
     The tool host sets `SESSION_CONTEXT` from the validated tenant claim, read-only, before running model-generated SQL.
  2. **Bridge:** index per tenant for a "Premium" tenant. The tenant registry maps tenant → index name, and the retriever resolves the index from the registry, never from input.
  3. Extend isolation to the APIM semantic cache key (tenant-scoped), memory store partition and trace content.
  4. Build `isolation-tests`: for every path (retrieval, Fleet Analyst SQL, cache, memory, A2A endpoint), run the canary queries as the other tenant and assert that no foreign marker appears anywhere, including in the trace attributes visible to that tenant.
  5. Implement tenant offboarding: delete the index or documents, SQL rows, cache entries, memory, eval data. Produce an **offboarding certificate** (JSON with counts before/after per store).
- **Break it:** Remove the `tenant_id` filter from one code path, the "similar incidents" helper. Isolation tests must fail. Then make the pooled filter structurally unavoidable: tenant-scoped retriever factory plus architecture test.
- **Acceptance criteria:**
  - Isolation tests pass on all paths and run in CI on every PR.
  - The offboarding certificate shows zero residual records.
  - The ADR "Tenant isolation tiers" maps pooled/bridge/silo to SaaS plans with costs from A1.
- **Stretch:** Add a "silo" deployment via the A2 landing-zone parameters for an enterprise tenant demanding contractual isolation. Estimate the cost to serve it.

### Lab 5 — Graph and structured knowledge decisions (≈2.5h)

- **Goal:** Decide on GraphRAG for global incident questions, and govern metric definitions for the Fleet Analyst.
- **Start state:** `a3/lab5-start`. Contains 3 years of incident narratives (~9k) and the C10 analyst with raw-schema grounding.
- **Steps:**
  1. Build 30 "global" questions ("top recurring failure themes on the Plovdiv–Kulata route by vehicle model") with SME reference answers.
  2. Compare hybrid + rerank vs graph retrieval: the MAF Neo4j provider, or LazyGraphRAG if available to you (verify access). Measure answer quality (rubric judge), indexing cost and query cost.
  3. Write **ADR-A3-004 "Graph retrieval for incident analytics"** with explicit "revisit when" triggers.
  4. Define a semantic layer: views and functions for `DowntimeDays`, `FuelPer100Km` and `OnTimeDeliveryRate`, with descriptions, units and owner. Re-ground the analyst on the semantic-layer metadata. Re-run the C10 golden queries plus 20 new metric questions.
- **Break it:** Two analysts ask "downtime last quarter for Sofia depot" in different words. Before the semantic layer, show the divergent SQL and numbers. After it, show consistent results.
- **Acceptance criteria:**
  - The graph decision is backed by measured cost and quality.
  - Semantic-layer metric questions reach ≥ 95% execution-match on the golden set.
  - The text-to-SQL tool enforces read-only access, allow-listed views, timeout, row cap and RLS (security tests pass).
- **Stretch:** Expose the semantic layer to Copilot Studio through the C8 MCP server for a "fleet manager self-service" agent, inheriting the same RLS.

## Kata

**"Where does this byte live?"** (25 min, repeat with variations).

Given one user interaction, trace every place the data lands or is processed. Example: a Danube Logistics dispatcher asks the Fleet Assistant about a late shipment, attaching a customer email. For each location, state:

- region and residency;
- tenant scoping;
- retention;
- permission enforcement point;
- deletion mechanism on offboarding.

Locations to cover: gateway logs, semantic cache, prompt to model (deployment type), retrieved chunks, tool calls, SQL, Cosmos conversation, memory, traces, eval sampling, red-team corpus.

Variations:
- a Copilot Studio agent calling via MCP;
- an A2A call from the customer's own agent;
- a Bulgarian-language query with groundedness evaluation (English-only service, so what is your fallback?);
- a user exercising GDPR erasure;
- an embedding-model migration.

The score is locations found out of the reference list, plus correct enforcement points.

## Product increment — Fleet Ops Copilot

The product now sits on a **knowledge platform**:

- stores chosen per domain by ADR;
- a Content Understanding ingestion pipeline with freshness SLOs and blue/green index aliases;
- permission enforcement tested on every path, with known revocation latency;
- EU residency mapped for every data surface;
- a governed semantic layer for the Fleet Analyst;
- a graph-retrieval decision for incident analytics;
- **pooled and bridge tenant isolation** proven by canary leak tests and a provable offboarding process.

## Factory increment — your agentic SDLC

- **Retrieval eval gate on index changes:** any change to chunking, embedding model, analyser or alias target runs the retrieval suite (recall@k, nDCG, Document Retrieval evaluator) before the alias switch.
- **Isolation and permission suites** run on every PR. They are non-negotiable gates and cannot be skipped by agents. A hook blocks PRs that modify the test filters without a CODEOWNERS approval.
- **Architecture tests** (NetArchTest/ArchUnitNET) prevent unfiltered retrievers and tenant-unscoped data access from compiling into product assemblies.
- **A data-classification skill** for coding agents: when an agent adds a new store, cache or log field, the skill prompts for tenant scope, residency, retention and deletion path, and updates the "where does this byte live" register.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Platform design & GA/preview judgement | Single RAG app | Layers named | Layers with guarantees; production on GA, preview behind flags | Plus published platform guarantees consumed by ADRs; upgrade criteria for preview features |
| Store selection | Preference | Feature comparison | Bake-off at 3 scale points with recall, latency, cost; per-domain ADR | Plus quantization trade-offs measured, "one content, one permission model" enforced |
| Ingestion | Naive chunks | Layout-aware parsing | Contextual chunks, dedup, freshness SLO, blue/green aliases gated by evals | Plus cost per 1k pages in the business model; rollback timed |
| Permissions & residency | Prompt-based trimming | Filter on one path | Matrix on all paths, overage handled, revocation latency measured, residency map | Plus labels excluded at ingestion, architecture tests, region constraints on safety tooling handled |
| Tenant isolation & structured data | Shared everything | Tenant filter | Pooled/bridge designs, canary leak tests across cache/memory/traces, offboarding certificate, governed semantic layer | Plus isolation tiers priced in SaaS plans, graph retrieval decided by cost/quality evidence |

**Auto-checked:**
- bake-off report;
- retrieval eval thresholds and alias gate;
- permission matrix;
- isolation tests;
- architecture tests;
- offboarding certificate;
- SQL tool security tests;
- semantic-layer execution-match;
- ADR linter.

## Common pitfalls

- Building the SaaS on preview-only features (planning, synthesis, native ACLs) without a GA fallback.
- Trimming in the prompt, or building filters from model-supplied parameters.
- Forgetting group overage and revocation latency.
- Re-embedding in place without aliases, which mixes vector spaces.
- Duplicated content across stores with different permission models.
- Residency designed for indexes only, while caches, traces, memory and eval sets leak elsewhere. Using Global deployments for EU personal data without a decision.
- Tenant filters "everywhere except one helper". Prove isolation with canaries and architecture tests.
- GraphRAG because it is fashionable. Without global questions, hybrid + rerank wins on cost.
- Text-to-SQL on raw schema with model-chosen tenant context.


## References

- Azure AI Search — What's new (knowledge bases GA 2026-04-01, preview features, ACLs, Purview, aliases, quantization): https://learn.microsoft.com/en-au/Azure/search/whats-new
- Agentic retrieval overview: https://learn.microsoft.com/azure/search/agentic-retrieval-overview
- What's new in Microsoft Foundry — Build 2026 (Foundry IQ GA, Serverless preview, permission sync preview): https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-build-2026/
- Vectors in SQL Server / Azure SQL (status table, exact kNN < ~50k, `WITH APPROXIMATE`): https://learn.microsoft.com/en-us/sql/sql-server/ai/vectors
- Cosmos DB hybrid search GA (AZ467425): https://mc.merill.net/message/AZ467425
- .NET vector stores (MEVD): https://learn.microsoft.com/en-us/dotnet/ai/vector-stores/overview
- Anthropic, Contextual Retrieval: https://www.anthropic.com/news/contextual-retrieval
- Chroma, Context Rot: https://trychroma.com/research/context-rot
- Microsoft Research, LazyGraphRAG: https://www.microsoft.com/en-us/research/blog/lazygraphrag/ ; GraphRAG paper: https://arxiv.org/abs/2404.16130
- Agent Framework RAG (TextSearchProvider, Neo4j provider): https://learn.microsoft.com/agent-framework/agents/rag
- Multitenant AI/ML approaches: https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/ai-machine-learning
- Foundry RAG evaluators (Document Retrieval: Fidelity, nDCG@3, holes): https://learn.microsoft.com/en-my/Azure/foundry/concepts/evaluation-evaluators/rag-evaluators
- RAGAS metrics (incl. SQL): https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
- Content Understanding at Build 2026: https://devblogs.microsoft.com/foundry/whats-new-in-azure-content-understanding-at-build-2026/
- Content Safety overview (language/region limits): https://learn.microsoft.com/en-gb/azure/ai-services/content-safety/overview
- AI Red Teaming Agent (regions): https://learn.microsoft.com/azure/ai-foundry/concepts/ai-red-teaming-agent
