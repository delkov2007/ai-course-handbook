# C6 — Embeddings & vector search

> **Level:** 2 — Building blocks (Intermediate) · **Duration:** 12h (theory 30% / labs 70%) · **Prerequisites:** C2 (`IChatClient`, provider swap via config), C5 (golden dataset v1, eval tests in CI), working SQL Server 2025 container from C0 · **Volatility:** Med

## Why this matters

Trakia Freight's dispatchers ask questions like "може ли шофьор да кара 10 часа два пъти в седмицата?" ("can a driver drive 10 hours twice a week?") while the authoritative answer sits in an English EU driving-time summary, a Bulgarian internal policy annex, and a 2024 memo that superseded part of both. A keyword search on "10 часа" finds the memo but not the regulation; a naive vector search finds the regulation but ranks a near-duplicate *draft* policy above the approved one. Neither failure shows up in a demo. Both show up on day three of production, when a dispatcher acts on the wrong document.

Embeddings and vector search are the first stage of almost every knowledge feature in this course (RAG in C7, few-shot retrieval for text-to-SQL in C10, memory in C13). Teams that skip the fundamentals make expensive, hard-to-reverse mistakes: they pick an embedding model by leaderboard rank without testing Bulgarian, put a DiskANN index on a table where exact search would be faster and exact, or discover after six months that "upgrading the embedding model" means re-embedding the whole corpus — with no way to roll back.

Experts do three things differently. First, they **measure retrieval separately from generation**, with a labelled query set and recall@k / MRR / nDCG, before any LLM sees a chunk. Second, they treat the vector store as an **architecture decision** (where the source of truth lives, filter semantics, hybrid support, cost model) recorded in an ADR, not a default. Third, they **design for model churn**: the embedding model is versioned data, re-embedding is a planned blue/green operation with a cost estimate, and the code talks to an abstraction (`IEmbeddingGenerator`, `Microsoft.Extensions.VectorData`) so a store or model swap is a configuration change followed by an eval run.

## Learning outcomes

By the end of this module you can:

1. **Explain** how a bi-encoder embedding model maps text to vectors and **predict** when cosine, dot product and Euclidean distance give identical rankings.
2. **Choose and justify** an embedding model (dimensions, max input, languages, modality, price, lifecycle) for a bilingual BG/EN corpus using measured recall, not leaderboard rank.
3. **Implement** a retrieval evaluation harness in C# that computes recall@k, MRR@k and nDCG@k over a labelled query set and runs in CI.
4. **Implement** vector storage and search on SQL Server 2025 (`VECTOR` type, `VECTOR_DISTANCE`, DiskANN index) and on Azure AI Search (HNSW / exhaustive KNN, filters), and **decide** between exact and approximate search from corpus size and filter selectivity.
5. **Apply** compression (int8 scalar, binary quantization, Matryoshka truncation) with oversampling and rescoring, and **quantify** the storage-vs-recall trade-off on Trakia data.
6. **Write** store-agnostic retrieval code with `Microsoft.Extensions.VectorData` and swap stores without changing business logic.
7. **Estimate** the cost and plan the rollout of an embedding-model change (re-embedding tokens, index rebuild, alias cut-over, rollback).
8. **Produce** an ADR comparing SQL Server 2025 vectors and Azure AI Search for the Trakia policy corpus, backed by eval numbers.

## Concepts

### Embeddings as a measurement instrument

An embedding model is an encoder that maps an input (text, and for multimodal models images) to a fixed-length vector so that semantically similar inputs are close. Retrieval models are **bi-encoders**: query and document are encoded independently, which is what makes them indexable — you embed the corpus once and only the query at search time. The price of independence is precision: a bi-encoder never sees query and document together, so it is weak at negation, exact identifiers and fine-grained constraints. That is why C7 adds lexical search (BM25) and a cross-encoder reranker on top. Treat embeddings as a *recall* instrument: their job is to get the right chunk into the top 50, not to put it at rank 1.

What the vector encodes is decided by the model's training data and objective, not by you. Consequences:

- **Vectors from different models are incomparable.** Even two models with 1,536 dimensions live in unrelated spaces. Microsoft's catalogue states plainly that you cannot upgrade between embedding models; switching means re-embedding the corpus.
- **Max input length truncates silently.** Azure OpenAI `text-embedding-3-*` accept up to 8,192 tokens per input and up to 2,048 inputs per call. The research notes record Cohere `embed-v-4-0` on Azure as accepting text "up to 512 tokens" — that is a hard design constraint on chunk size if accurate (verify against current documentation; it may reflect a catalogue-specific limit).
- **Languages matter.** Bulgarian Cyrillic text is token-heavier than English (no published measurement was found; Lab 1 produces Trakia's own number), and multilingual quality varies per model. Cross-lingual retrieval (Bulgarian query, English document) works only if the model was trained for it. You must test it.

### Current models you will meet (Oct 2026)

| Model (Foundry) | Dims | Notes |
|---|---|---|
| `text-embedding-3-large` | 3,072 (reducible via `dimensions`) | 8,192-token input; Matryoshka-style truncation supported |
| `text-embedding-3-small` | 1,536 (reducible) | Cheap default; reduced-dimension output still slightly beats `ada-002` on MTEB per Microsoft |
| `text-embedding-ada-002` | 1,536 | Legacy; do not start new corpora on it |
| Cohere `embed-v-4-0` | 256 / 512 / 1,024 / 1,536 | Multimodal (text + images); relevant for scanned delivery notes |
| Others in the wider market | — | `gemini-embedding-2-preview` (not sold by Azure), Voyage 4, Qwen3-Embedding-8B (open weights) |

Labs refer to the *role* "embedding model" and pin the deployment name in `appsettings.json` (blueprint rule). Never quote MTEB ranks in an ADR — no 2026 snapshot was verified, and your corpus is not MTEB.

### Similarity metrics

- **Cosine similarity**: cos θ = (a·b)/(‖a‖‖b‖). Measures angle; ignores magnitude.
- **Dot product**: a·b. Equal to cosine when both vectors are unit-normalized.
- **Euclidean (L2) distance**: ‖a−b‖. For unit vectors, ‖a−b‖² = 2 − 2·cos θ, so the *ranking* is identical to cosine.

Decision rule: use the metric the model was trained for; if the model outputs normalized vectors (OpenAI and most modern models do — verify per model), cosine, dot and L2 rank identically and dot is cheapest. If you truncate a Matryoshka vector, **re-normalize** before using dot product — truncation breaks unit length. Note that SQL Server's `VECTOR_DISTANCE('cosine', …)` returns a *distance* (lower is better), while many SDKs return a *similarity score* (higher is better); mixing them up produces perfectly inverted rankings that pass a smoke test with one query.

In .NET, `System.Numerics.Tensors.TensorPrimitives.CosineSimilarity(ReadOnlySpan<float>, ReadOnlySpan<float>)` and `TensorPrimitives.Dot` are SIMD-accelerated and are what you use for in-memory experiments and for the in-memory MEVD connector.

### Exact vs approximate nearest neighbour

**Exact kNN** compares the query with every candidate vector: O(n·d). For 15,000 chunks × 1,536 dims that is ~23M multiply-adds — single-digit milliseconds on a modern CPU. Microsoft's SQL guidance recommends exact search (`VECTOR_DISTANCE`) when there are fewer than about **50,000 vectors after predicates are applied**. That last clause is the important one: a filter `WHERE DepotId = 'VAR' AND Lang = 'bg'` can turn a 2M-row table into 8,000 candidates, where exact search is both faster and 100% accurate.

**Approximate (ANN)** indexes trade a little recall for sub-linear search:

- **HNSW** (Malkov & Yashunin): a hierarchical proximity graph. Knobs: `M` (edges per node; memory and recall up), `efConstruction` (build-time beam; build cost and graph quality up), `efSearch` (query-time beam; latency and recall up). Azure AI Search's default vector algorithm.
- **DiskANN**: a graph index (Vamana) designed to keep most of the graph on SSD with a compressed in-memory representation, so very large indexes do not need all vectors in RAM. It is the index behind `CREATE VECTOR INDEX` in SQL Server 2025 / Azure SQL.
- **IVF / product quantization** families exist in other stores; you will not configure them in this course.

**Filtering is where ANN bites.** With *post-filtering*, the index returns top-k neighbours and then the filter removes most of them — you ask for 10, get 2. With *pre-filtering*, the filter restricts the candidate set first; on a graph index this can disconnect the graph and hurt recall or latency. Azure AI Search offers `vectorFilterMode` (`preFilter` default, `postFilter`, and `strictPostFilter` in preview since Aug 2025). In SQL, check the plan: does the optimizer apply your predicate before or after the approximate search? Measure recall per filter bucket, not only globally.

### Compression: quantization and Matryoshka

Vector storage dominates cost in search services sized by storage and memory. Three levers, all GA in Azure AI Search since Sep 2025:

- **Scalar quantization (int8)**: each float32 → 1 byte. ~**4×** smaller index, small recall loss.
- **Binary quantization**: each dimension → 1 bit. "Up to **28×**" smaller (up to 96% reduction). Works best for embeddings with **>1,024 dimensions** that are roughly zero-centred.
- **Matryoshka truncation**: models trained with Matryoshka Representation Learning (Kusupati et al.) put the most information in the leading dimensions, so the first N dimensions form a usable lower-dimensional embedding. Azure AI Search exposes this as `truncationDimension` for `text-embedding-3` models; the Azure OpenAI API exposes the `dimensions` parameter at embedding time.

Compression loses ranking precision, which you recover with **oversampling + rescoring**: retrieve k × oversampling candidates using compressed vectors (default oversampling 4), then rescore them with full-precision vectors and return the top k. In Azure AI Search, rescoring requires HNSW (not exhaustive KNN) and the original vectors must be kept (`enableRescoring: true`, and don't set `discardOriginals` if you want full-precision rescoring — verify the exact interaction in current docs). The decision is economic: binary + rescoring can cut a tier; on a 15k-chunk corpus it changes nothing material and adds a failure mode.

### Where vectors live on Azure (Oct 2026)

**SQL Server 2025 / Azure SQL / Fabric SQL** — the `VECTOR(n)` type (float32 elements) and `VECTOR_DISTANCE` are GA everywhere. `CREATE VECTOR INDEX` (DiskANN) is **GA in Azure SQL Database, Fabric SQL and SQL MI (Always-up-to-date policy) but preview in boxed SQL Server 2025** (and in MI with the SQL Server 2025 policy). Approximate search uses the newer `SELECT TOP (N) WITH APPROXIMATE … ORDER BY VECTOR_DISTANCE(…)` form; the older `VECTOR_SEARCH(… TOP_N …)` parameter is deprecated. `AI_GENERATE_EMBEDDINGS(text USE MODEL <model>)` generates embeddings in T-SQL; how the model object is created (`CREATE EXTERNAL MODEL`) was not confirmed on the fetched page — verify against current documentation. Historically early previews made a table read-only once it had a vector index; verify current behaviour before you put a DiskANN index on a table that receives writes. Strengths: vectors sit next to the rows (no sync pipeline), transactional consistency, row-level security reuse, no new service. Hybrid search must be assembled yourself (full-text + vector, fused in T-SQL or C#; not verified as a native feature).

**Azure AI Search** — vector fields up to 4,096 dims, HNSW or exhaustive KNN, quantization with rescoring, Matryoshka truncation, integrated vectorization and skills, hybrid BM25 + vector with RRF, semantic ranker, subscores, index **aliases (GA Apr 2026)** for blue/green re-indexing, and knowledge bases (C7, C13). Cost is a fixed search-unit tier; semantic ranker and agentic retrieval need separate billing consent since API 2026-04-01.

**Cosmos DB for NoSQL** (vector + BM25 + hybrid RRF, GA May 2025) and **PostgreSQL/pgvector** (portable; 2026 Azure status not re-verified) complete the picture.

### Microsoft.Extensions.VectorData (MEVD)

MEVD (GA May 2025) is to stores what `IChatClient` is to models. Core types: `VectorStore`, `VectorStoreCollection<TKey, TRecord>`, attributes `[VectorStoreKey]`, `[VectorStoreData]`, `[VectorStoreVector(dimensions: N)]`, operations `EnsureCollectionExistsAsync`, `UpsertAsync`, `SearchAsync`. If an `IEmbeddingGenerator` is attached to the store, you can search by text and the store embeds the query. Microsoft Learn (Jul 2026) shows connectors as `CommunityToolkit.VectorData.InMemory` and `CommunityToolkit.VectorData.AzureAISearch`; older `Microsoft.SemanticKernel.Connectors.*` packages also exist (including SQL Server and PgVector). The connector naming is in flux — **pin exact packages in the lab repo and verify against current documentation**. MEVD gives you portability for the 80% case (upsert, top-k, simple filters); store-specific features (quantization config, `WITH APPROXIMATE`, semantic ranker) still need the native SDK or T-SQL.

### Measuring retrieval

You need **qrels**: for each query, the set of relevant chunk/document IDs (optionally graded 0–3). Then:

- **recall@k** = |relevant ∩ top-k| / |relevant|. "Did it get into the window the generator will see?" For RAG this is the primary metric.
- **MRR@k** = mean over queries of 1/rank of the first relevant hit (0 if none in top k). Sensitive to rank 1; good for single-answer lookups.
- **nDCG@k** = DCG@k / IDCG@k with DCG = Σ (2^rel_i − 1)/log₂(i+1). Handles graded relevance and position. Foundry's Document Retrieval evaluator reports nDCG@3, XDCG@3, Fidelity and "holes" (retrieved docs with no label — your qrels are incomplete, not necessarily your retriever bad).

Rules: label at the **document or section level** if chunking is still changing, otherwise every chunking change invalidates qrels; stratify queries (BG, EN, cross-lingual, identifiers such as fault code `P0420`, multi-document, "not in corpus"); report per stratum; and track **holes** — an unlabelled hit is a labelling task, not a metric.

### Misconceptions to unlearn

- "Switching embedding models is a config change." It is a full re-embed and re-index (Lab 5).
- "Higher dimensions are always better." On a small domain corpus, truncated 256-dim vectors may match 3,072 within noise; measure.
- "ANN is always faster." Below ~50k candidates exact search is fast and exact.
- "Cosine 0.83 means 83% relevant." Scores are uncalibrated across queries and models; never threshold raw similarity without calibration.
- "Vector search finds IDs and codes." Bi-encoders blur `P0420` and `P0430` (C7 adds hybrid).
- "Multilingual means good at Bulgarian." Test it on Trakia queries.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| `Microsoft.Extensions.AI` / `.Abstractions` 10.5.x | `IEmbeddingGenerator<string, Embedding<float>>`, `EmbeddingGenerationOptions.Dimensions` | GA | Same abstraction for Foundry, Foundry Local, Ollama |
| `Microsoft.Extensions.AI.OpenAI` + `OpenAI` (against `/openai/v1/`) or `Azure.AI.Extensions.OpenAI` 2.0 | Embedding client for Foundry deployments | GA | Don't mix with preview `Azure.AI.Projects.OpenAI` |
| `Microsoft.Extensions.VectorData.Abstractions` | `VectorStore`, `VectorStoreCollection` | GA (May 2025) | Pin version |
| `CommunityToolkit.VectorData.InMemory`, `.AzureAISearch`; SQL Server connector | MEVD connectors | Package names in flux | Verify exact names/versions before teaching |
| SQL Server 2025 / Azure SQL | `VECTOR`, `VECTOR_DISTANCE`, `AI_GENERATE_EMBEDDINGS`, `CREATE VECTOR INDEX` | Type GA; DiskANN **preview** in SQL Server 2025, GA in Azure SQL DB / MI (Always-up-to-date) / Fabric | Exact search < ~50k vectors after predicates |
| `Microsoft.Data.SqlClient` | Parameterizing vectors | GA | Native vector parameter type in recent versions — verify; fallback: JSON string + `CAST(@q AS VECTOR(n))` |
| `Azure.Search.Documents` | Index definition, vector/hybrid queries | GA (API 2026-04-01) | Quantization, `truncationDimension`, aliases |
| `System.Numerics.Tensors` | `TensorPrimitives.CosineSimilarity`, `Dot` | GA | In-memory experiments |
| `Microsoft.ML.Tokenizers` | Token counting BG vs EN | GA | Cost estimation |
| Foundry embedding deployments | `text-embedding-3-small/large`, Cohere `embed-v-4-0` | GA | Lifecycle: GA models retire ≥18 months (partner models 12) |

## Labs

### Lab 1 — Embeddings on bilingual Trakia text (≈1.5h)

- **Goal:** Build intuition for embedding geometry, metric equivalence, cross-lingual behaviour and token cost on Trakia's own text.
- **Start state:** `c6/lab1-start` — solution `FleetOps.sln` with `FleetOps.Retrieval` project, `data/policies/` (fleet policy handbook, driver code of conduct, EU driving-time summary; BG and EN versions of 40 sections), `appsettings.json` with `Embeddings:Primary` and `Embeddings:Secondary` deployment names.
- **Steps:**
  1. Register two generators by key, driven by config:
     ```csharp
     builder.Services.AddKeyedSingleton<IEmbeddingGenerator<string, Embedding<float>>>("primary", (sp, _) =>
         new OpenAIClient(credentialPolicy, new OpenAIClientOptions { Endpoint = new(cfg["Foundry:OpenAIEndpoint"]!) })
             .GetEmbeddingClient(cfg["Embeddings:Primary"]!)      // e.g. text-embedding-3-large
             .AsIEmbeddingGenerator());                           // verify exact API against current docs
     ```
  2. Embed the 40 parallel BG/EN section pairs with both models. For each pair compute cosine with `TensorPrimitives.CosineSimilarity`. Compute the same for 40 *non-matching* pairs. Plot both distributions (CSV → any chart tool). The gap between distributions is your model's cross-lingual separability.
  3. Verify unit norm (`TensorPrimitives.Norm`) of returned vectors. Rank 20 chunks for 5 queries by cosine, dot and L2; assert rankings are identical. Now request `Dimensions = 256` via `EmbeddingGenerationOptions` and repeat — rankings by dot product diverge unless you re-normalize. Fix it.
  4. Count tokens for all 40 BG and EN sections with `Microsoft.ML.Tokenizers` (tokenizer for the embedding model family — verify which encoding applies). Record the BG/EN token ratio; project the monthly embedding cost for the full 1,500-doc corpus at current price (price from config, not hard-coded).
- **Break it:** Embed the corpus with the primary model and the queries with the secondary model (same dimension count via `Dimensions`). Observe that the code runs, returns results, and is garbage. Add a guard: every stored vector carries `EmbeddingModelId`; the search path throws if the query generator's model ID differs.
- **Acceptance criteria:** `dotnet test --filter Category=C6.Lab1` passes: (a) metric-equivalence test for normalized vectors; (b) model-mismatch guard throws; (c) `reports/c6-lab1.md` contains the BG/EN token ratio and the matched vs non-matched cosine means for both models.
- **Stretch:** Embed 20 scanned delivery-note images with Cohere `embed-v-4-0` and search them with text ("доставка Варна палети") — no OCR.

### Lab 2 — A retrieval eval harness with qrels (≈1.5h)

- **Goal:** Build the instrument every later retrieval decision depends on.
- **Start state:** `c6/lab2-start` — `evals/retrieval-golden.v1.jsonl` with 60 instructor-labelled queries; you add 20 (incl. ≥ 5 cross-lingual and ≥ 3 identifier queries) to reach 80.
- **Steps:**
  1. Extend the golden set to 80 queries, stratified: 25 BG, 25 EN, 15 cross-lingual (BG query → EN source), 10 identifier queries (fault codes, policy numbers like `FP-7.3`), 5 "not in corpus". Each line: `{ "id", "query", "lang", "stratum", "relevant": [{ "docId", "section", "grade": 0-3 }] }`. Label at **section** level so Lab 3–5 chunking changes don't invalidate labels.
  2. Implement the metrics:
     ```csharp
     public static class RetrievalMetrics
     {
         public static double RecallAt(IReadOnlyList<string> ranked, ISet<string> relevant, int k) =>
             relevant.Count == 0 ? double.NaN : ranked.Take(k).Count(relevant.Contains) / (double)relevant.Count;

         public static double ReciprocalRank(IReadOnlyList<string> ranked, ISet<string> relevant, int k)
         {
             for (int i = 0; i < Math.Min(k, ranked.Count); i++)
                 if (relevant.Contains(ranked[i])) return 1.0 / (i + 1);
             return 0;
         }

         public static double NdcgAt(IReadOnlyList<string> ranked, IReadOnlyDictionary<string, int> grades, int k)
         {
             double Dcg(IEnumerable<int> g) => g.Select((rel, i) => (Math.Pow(2, rel) - 1) / Math.Log2(i + 2)).Sum();
             var dcg  = Dcg(ranked.Take(k).Select(id => grades.GetValueOrDefault(id)));
             var idcg = Dcg(grades.Values.OrderByDescending(v => v).Take(k));
             return idcg == 0 ? 0 : dcg / idcg;
         }
     }
     ```
  3. Define `IRetriever { Task<IReadOnlyList<Hit>> SearchAsync(string query, RetrievalFilter filter, int k, CancellationToken ct); }` and map chunk hits back to `docId#section` before scoring (dedupe: first occurrence wins).
  4. Write an xUnit test that runs the harness against the in-memory MEVD baseline and writes `artifacts/retrieval-report.json` (per-stratum recall@5/@10, MRR@10, nDCG@10, holes count). Mark it `[Trait("Category","Eval")]` so CI runs it in the eval job created in C5.
- **Break it:** Swap two labels in the golden set (simulate a labelling error) and observe how much a single wrong label moves MRR on the "identifier" stratum (n=10). Write two sentences in the report about confidence intervals on small strata.
- **Acceptance criteria:** Metric unit tests (hand-computed fixtures) pass; harness produces the JSON report; CI eval job publishes it as an artifact; "not in corpus" queries are excluded from recall and reported separately as "top-1 score distribution".
- **Stretch:** Add bootstrap 95% confidence intervals per stratum (1,000 resamples).

### Lab 3 — SQL Server 2025: exact search, DiskANN and filters (≈2.5h)

- **Goal:** Run vector search where Trakia's operational data already lives and learn when the index helps.
- **Start state:** `c6/lab3-start` — `TrakiaOps` database with `dbo.PolicyChunk` (≈15k chunks, 512-token fixed chunks for now), and a synthetic `dbo.IncidentNoteEmbedding` table (≈600k rows) for scale experiments. Note: DiskANN is **preview** in boxed SQL Server 2025; the lab includes an Azure SQL Database variant (`infra/c6-azuresql.bicep`) where it is GA.
- **Steps:**
  1. Schema:
     ```sql
     ALTER TABLE dbo.PolicyChunk ADD
         Embedding VECTOR(1536) NULL,
         EmbeddingModelId VARCHAR(64) NULL;
     ```
     Populate from C# in batches of ≤2,048 inputs per embedding call (the API limit), using a `SqlBulkCopy` staging table or batched `UPDATE`. Pass vectors either via the native SqlClient vector type (verify) or as a JSON array string with `CAST(@v AS VECTOR(1536))`.
  2. Exact search with a filter:
     ```sql
     DECLARE @q VECTOR(1536) = CAST(@qjson AS VECTOR(1536));
     SELECT TOP (10) ChunkId, DocId, Section,
            VECTOR_DISTANCE('cosine', Embedding, @q) AS Distance
     FROM dbo.PolicyChunk
     WHERE Lang IN ('bg','en') AND Status = 'Approved'
     ORDER BY Distance;            -- distance: lower is better
     ```
     Wire it as `SqlExactRetriever : IRetriever` and run the Lab 2 harness.
  3. Build an index on the large table and compare:
     ```sql
     CREATE VECTOR INDEX vix_IncidentNote ON dbo.IncidentNoteEmbedding(Embedding)
         WITH (METRIC = 'cosine', TYPE = 'diskann');   -- preview on SQL Server 2025; verify options
     SELECT TOP (10) WITH APPROXIMATE NoteId,
            VECTOR_DISTANCE('cosine', Embedding, @q) AS Distance
     FROM dbo.IncidentNoteEmbedding
     ORDER BY Distance;                                 -- verify exact syntax against current docs
     ```
     For 50 random queries, compute ANN recall@10 against exact results (exact = ground truth) and p50/p95 latency for both.
  4. Filter selectivity experiment: add `WHERE DepotId = @depot` with depots of very different sizes (Varna ≈ 8% of rows). Measure ANN recall@10 per depot and inspect execution plans: is the predicate applied before or after the approximate search? Record result-count shortfalls (asked 10, got fewer).
- **Break it:** Run the exact query on the 600k-row table without a filter while the embedding backfill job is writing; observe latency and blocking. Then attempt an `UPDATE` on a row of the indexed table and record the behaviour (read-only restriction or not — this is the "verify against current documentation" fact; your lab report is evidence).
- **Acceptance criteria:** `SqlExactRetriever` reaches the same metrics as the in-memory baseline (±0.01 recall@10) on the golden set; report contains exact-vs-ANN recall@10 (target ≥0.95 unfiltered) and latency table; a decision rule written in your own words with the measured crossover point.
- **Stretch:** Generate query embeddings in-database with `AI_GENERATE_EMBEDDINGS` and compare end-to-end latency and operational trade-offs (credentials, network path, model governance) with app-side embedding.

### Lab 4 — Azure AI Search: HNSW, quantization and Matryoshka (≈1.75h)

- **Goal:** Quantify compression trade-offs and compare with SQL on identical data and labels.
- **Start state:** `c6/lab4-start` — `infra/c6-search.bicep` (Basic tier), `FleetOps.Retrieval.AzureSearch` project.
- **Steps:**
  1. Create four indexes over the same chunks (3,072-dim `text-embedding-3-large` vectors): `pol-full` (HNSW, no compression), `pol-int8` (scalar quantization + rescoring), `pol-bin` (binary quantization + rescoring, oversampling 4 then 10), `pol-trunc256` (`truncationDimension = 256` + int8). Shape:
     ```csharp
     var index = new SearchIndex("pol-int8")
     {
         Fields = {
             new SimpleField("id", SearchFieldDataType.String) { IsKey = true },
             new SearchableField("content") { AnalyzerName = LexicalAnalyzerName.BgMicrosoft }, // verify analyzer name
             new SimpleField("lang", SearchFieldDataType.String) { IsFilterable = true },
             new VectorSearchField("embedding", 3072, "vp-int8")
         },
         VectorSearch = new()
         {
             Algorithms   = { new HnswAlgorithmConfiguration("hnsw") },
             Compressions = { new ScalarQuantizationCompression("sq")
                              { /* RescoringOptions: enable rescoring, oversampling 4 — verify property names */ } },
             Profiles     = { new VectorSearchProfile("vp-int8", "hnsw") { CompressionName = "sq" } }
         }
     };
     ```
  2. Query each index with `VectorizedQuery` (k=50) and also with `Exhaustive = true` on `pol-full` as ground truth; run the Lab 2 harness on all variants.
  3. Read index statistics (vector index size, storage) via `SearchIndexClient.GetIndexStatisticsAsync`. Produce a table: variant · vector storage · recall@10 · nDCG@10 · p95 latency.
  4. Implement `AzureSearchRetriever : IRetriever` once with MEVD (`CommunityToolkit.VectorData.AzureAISearch`) and once with the native SDK; confirm identical metrics and note which settings MEVD cannot express.
- **Break it:** Disable rescoring on `pol-bin` and re-run. Then set `vectorFilterMode = postFilter` with a selective `lang eq 'bg'` filter and k=10; count queries that return fewer than 10 results.
- **Acceptance criteria:** Report table complete for 4 variants; binary+rescoring within 0.03 recall@10 of `pol-full` or an explanation why not (dimensionality, centring); a chosen production configuration for a corpus 20× larger with one-paragraph justification.
- **Stretch:** Repeat with Cohere `embed-v-4-0` at 1,024 dims; compare BG and cross-lingual strata.

### Lab 5 — The embedding model changes: blue/green re-embed and the ADR (≈1.25h)

- **Goal:** Rehearse a model migration with cost estimate, alias cut-over and rollback; write the store ADR.
- **Start state:** `c6/lab5-start` — `pol-v1` index populated with `text-embedding-3-small`; alias `policies` → `pol-v1`.
- **Steps:**
  1. Cost model: total corpus tokens (from Lab 1 counting, BG-adjusted) × price per 1M tokens for the new model + search indexing time + engineer time; plus SQL storage delta for the SQL path (1,536 → 3,072 float32 = +6 KB per chunk). Put it in `docs/cost/c6-reembed.md`.
  2. Build `pol-v2` with `text-embedding-3-large` from the same chunks (store `EmbeddingModelId` and `ChunkerVersion` on each record). Run the harness on both. Write a promotion rule: v2 is promoted only if recall@10 is ≥ v1 on every stratum and overall nDCG@10 improves by ≥0.02.
  3. Cut over by repointing the alias (Index aliases GA Apr 2026); queries use the alias, never index names. Prove rollback by repointing back. Ensure the *query* embedding generator is switched in the same release as the alias (Lab 1 guard catches mistakes).
  4. Write `docs/adr/0006-policy-vector-store.md`: SQL Server 2025 vectors vs Azure AI Search for policies — source of truth, filters/ACL (forward reference to C7), hybrid availability, compression, cost model, operational burden, portability via MEVD, measured metrics from Labs 3–4.
- **Break it:** Repoint the alias to v2 but leave the app's query generator on v1 (simulated partial deploy). Observe the guard; then disable it and observe recall collapse — measured, not imagined.
- **Acceptance criteria:** Migration script idempotent; harness results for v1 and v2 committed; promotion rule implemented as a test that fails when the rule is not met; ADR reviewed by a peer using the ADR checklist in `docs/adr/README.md`.
- **Stretch:** Dual-write during the migration window (new chunks embedded with both models) and measure the extra cost.

## Kata

**Retrieval triage (25 min, repeat 4×).** You get a failing query from the golden set plus the top-20 hits with scores from one retriever variant. In 25 minutes: (1) classify the root cause — vocabulary/identifier mismatch, cross-lingual gap, chunk boundary, filter shortfall, ANN recall loss, compression loss, model mismatch, or wrong label; (2) state the cheapest experiment that would confirm it; (3) run it; (4) write a two-line finding. Variations: rotate the store (SQL exact, SQL DiskANN, AI Search int8, AI Search binary); one round uses a query in Bulgarian with transliterated Latin script ("shofior pochivka"); one round the "failure" is a label error (holes).

## Product increment — Fleet Ops Copilot

"Ask Fleet Ops" gains **semantic policy search**: `GET /api/policies/search?q=&lang=&k=` returns ranked policy sections with document ID, section, language and score, behind `IRetriever`. Two implementations ship behind configuration — `SqlExactRetriever` (default for dev, SQL Server 2025 container) and `AzureSearchRetriever` (Azure) — with the decision and numbers in ADR-0006. Every vector carries `EmbeddingModelId` and `ChunkerVersion`. The golden set grows a retrieval slice (80 queries with qrels) used by C7 onward.

## Factory increment — your agentic SDLC

- Add a **`retrieval-eval` skill** (Claude Code `.claude/skills/retrieval-eval/SKILL.md` and an equivalent Copilot prompt file) that tells the agent how to run the harness, where the report lands and what the promotion rule is. Agents must attach the before/after retrieval report to any PR touching `FleetOps.Retrieval/**`.
- Extend AGENTS.md with two non-guessable rules: "never compare vectors from different `EmbeddingModelId`s" and "SQL `VECTOR_DISTANCE` returns distance (lower is better)".
- Ask your coding agent to generate the Lab 4 index variants from a spec table; review its diff specifically for silent defaults (oversampling, filter mode, analyzer). Record what it got wrong in `docs/factory/agent-log.md` — this log feeds C11 and C19.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Retrieval measurement | Eyeballs results | Computes recall@k on a small set | Stratified qrels, recall/MRR/nDCG, holes tracked, CI artifact | Adds confidence intervals, label-quality checks, and uses the harness to reject a plausible change |
| Store & index choice | Uses defaults | Picks exact vs ANN with a reason | Measured crossover, filter-aware recall, plan inspection | ADR anticipates scale, ACLs (C7) and migration; numbers reproducible from repo |
| Compression & cost | Not considered | Enables quantization | Storage-vs-recall table with rescoring, tier implication | Cost model across tiers/stores incl. re-embedding and BG token ratio |
| Model lifecycle | Model hard-coded | Model in config | Model ID stored per vector, guard, alias cut-over | Rehearsed rollback, promotion rule as test, retirement-date watch |
| Explanation | Cannot explain results | Explains metric meanings | Explains each regression with evidence | Teaches a peer the triage method using own data |

**Auto-checked:** metric unit tests; retrieval harness runs in CI and produces report; `SqlExactRetriever` and `AzureSearchRetriever` meet recall@10 ≥ 0.85 overall and ≥ 0.75 on the cross-lingual stratum on the hidden 40-query set; model-mismatch guard test; promotion-rule test. **Human-reviewed:** ADR-0006 and Lab 5 cost model.

## Common pitfalls

- Sorting `VECTOR_DISTANCE` results descending; dot product on truncated, un-normalized vectors.
- Labelling qrels at chunk level, then "losing" recall on every chunking change.
- DiskANN for 15k rows; exact search on 2M rows without a selective predicate.
- Post-filtering with small k and returning 2 results.
- Oversized embedding batches failing a whole backfill; mixed models during a partial deploy.
- Comparing stores with different chunking, crediting the store for a chunking difference.


## References

- Microsoft Learn — Vectors in SQL Server / Azure SQL (status table, exact < ~50k, `WITH APPROXIMATE`): https://learn.microsoft.com/en-us/sql/sql-server/ai/vectors
- Microsoft Learn — Vector quantization in Azure AI Search (int8 4×, binary up to 28×, rescoring, `truncationDimension`): https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-quantization
- Azure AI Search — What's new (aliases GA Apr 2026, `strictPostFilter` preview, 4,096 dims): https://learn.microsoft.com/en-au/Azure/search/whats-new
- Microsoft Learn — Models sold directly by Azure (embedding models, dims, limits; Cohere embed v4 / rerank v4): https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure
- Microsoft Learn — .NET vector stores overview (MEVD): https://learn.microsoft.com/en-us/dotnet/ai/vector-stores/overview
- Microsoft Learn — .NET AI ecosystem: https://learn.microsoft.com/en-us/dotnet/ai/dotnet-ai-ecosystem
- Foundry RAG evaluators (Document Retrieval: nDCG@3, Fidelity, holes): https://learn.microsoft.com/en-my/Azure/foundry/concepts/evaluation-evaluators/rag-evaluators
- Kusupati et al., Matryoshka Representation Learning: https://arxiv.org/abs/2205.13147
- Malkov & Yashunin, HNSW: https://arxiv.org/abs/1603.09320
- Reimers & Gurevych, Sentence-BERT (bi-encoders): https://arxiv.org/abs/1908.10084
- Cosmos DB hybrid search GA (AZ467425): https://mc.merill.net/message/AZ467425
