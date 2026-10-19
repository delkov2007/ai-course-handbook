# D1 — Model customization & small/local models

> **Level:** Expert (AI Solution Developer track) · **Duration:** 20h (theory 25% / labs 75%) · **Prerequisites:** Core C0–C19 and Gate G3; especially C1 (mechanics), C5/C14 (evals, judges), C15 (cost per task), C18 (data protection) · **Volatility:** High (fine-tunable model list, preview deployment options, local runtime APIs)

## Why this matters

A proficient practitioner can run a fine-tuning job and serve a local model. An expert decides, with numbers, whether either should happen at all. The expert quantifies the gap a rung of the customization ladder must close, predicts its cost, and builds the before/after eval before touching training data. They know which failure each technique fixes (knowledge, behaviour, format, cost, latency, sovereignty). They catch leakage, forgetting and quantization loss before users do. They also treat a fine-tuned model as a versioned artifact with a retirement date, not as a one-off experiment.

Trakia Freight's depots in Plovdiv, Sofia and Varna triage engine fault codes (DTCs) for ~400 trucks. Today a frontier model answers mechanics' questions in Fleet Ops Copilot. Three things hurt: Varna's connectivity is unreliable, thousands of near-identical classification calls are billed at frontier prices, and a safety-relevant decision ("stop the truck now") depends on a cloud round trip.

"Fine-tune a small model and run it locally" fails in four predictable ways:
- training data leaks across splits, so offline scores are great and production scores are not;
- the student learns the teacher's mistakes;
- INT4 quantization quietly erases the rare-but-critical class;
- the fine-tuned base is retired 12–18 months later with no migration plan.

Experts therefore run customization as an experiment with a pre-registered success criterion. For Trakia: macro-F1 within 2 points of the frontier baseline, `StopNow` recall ≥ 0.97, p95 < 400 ms on depot hardware, and cost per 1,000 triages < 5% of baseline. If the experiment misses the bar, they stop and write down why.

## Learning outcomes

By the end of this module you can:

1. **Choose and justify** a rung on the customization ladder (prompting, few-shot, RAG, SFT, DPO, RFT, distillation, classical ML) for a given failure mode, using an explicit decision record with expected cost and eval delta.
2. **Construct** a leakage-free fine-tuning dataset (grouped splits, dedup, label audit, PII handling) and **diagnose** leakage when offline and online scores diverge.
3. **Design and run** a before/after evaluation matrix that measures target-task quality, safety-critical class recall, format adherence, general-capability regression and cost/latency.
4. **Execute** SFT and teacher-to-student distillation on Microsoft Foundry, and **explain** when DPO or RFT would be the better training signal and what the grader or preference data must look like.
5. **Detect** overfitting and catastrophic forgetting from loss curves and regression suites, and **apply** mitigations (epochs, rank, data mixing, early stopping).
6. **Explain** LoRA/QLoRA/PEFT mechanics well enough to size trainable parameters, pick rank, and decide between merged and hot-swapped adapters.
7. **Size** memory for a local or self-hosted model (weights + KV cache, dense vs MoE) and **measure** the quality cost of INT8/INT4 quantization on the critical class.
8. **Implement** provider-swappable local inference (Foundry Local, ONNX Runtime GenAI, LLamaSharp, Ollama) behind `IChatClient`, with an offline-first fallback chain.
9. **Produce** a cost/latency/accuracy comparison and an ADR that a reviewer can reproduce from pinned artifacts.

## Concepts

### 1. The customization ladder as decision rules, not a staircase

The ladder is a set of tools mapped to failure types. You do not climb it in order. Heuristic: **knowledge → RAG; behaviour/format → fine-tune; cost/latency at volume → distil to a smaller model; gradeable quality with many valid answers → RFT; "better vs worse is easy to judge, hard to demonstrate" → DPO; everything → evals first.** Microsoft's own guidance states the benefit of fine-tuning "isn't guaranteed", that teams must "compare against a baseline with held-out evaluation", and that fine-tuning "doesn't replace retrieval for current information".

Decision rules experts apply:

| Observed failure (from error analysis, C14) | First lever | Escalate to | Do **not** use |
|---|---|---|---|
| Missing or stale facts (new maintenance bulletin) | RAG (C7) | Better chunking/rerank | Fine-tuning (facts go stale, and you cannot cite weights) |
| Wrong output format or schema drift | Structured outputs (C3) | SFT if the schema is complex and the call volume is high | DPO |
| Inconsistent label policy on edge cases | Few-shot with curated hard examples, prompt-cached | SFT on adjudicated labels | RAG |
| Tone or completeness preferences | Prompt + rubric | DPO from preference pairs | SFT on "good" examples alone (it misses the contrast) |
| Correct answer is verifiable by code | Prompt + validator + retry | RFT with a code grader | LLM-judge rewards that can be gamed |
| Frontier quality is fine but cost/latency is not | Smaller model + few-shot; model router (D5) | Distillation into a small model | Bigger prompt |
| Closed label set, high volume, tabular-ish features | **ML.NET classifier** or a "decision model" | Fine-tuned small LM | Any generative model, by default |
| Data must not leave the site, or the site is offline | Local SLM (Foundry Local) | LoRA-tuned local SLM | Cloud-only design |

Exit criterion for every rung: a pre-registered metric target on a frozen test set. If prompting plus few-shot reaches 95% of the target, the remaining 5% rarely justifies a training pipeline you must then own for 18 months.

**Misconceptions to unlearn:**
- "Fine-tuning teaches the model our latest data." It shifts behaviour. Use retrieval for knowledge.
- "More epochs = better." Small datasets overfit within 2–4 epochs.
- "The fine-tuned model is ours forever." The base model has a retirement date (C15, A5). GA Azure models typically retire at 18 months and partner models at 12. Plan for re-training.
- "Open-weight means free to use." Licences vary (MIT, Apache-2.0, custom). Audit them.

### 2. Managed fine-tuning on Microsoft Foundry (as of Oct 2026)

Foundry offers three managed training signals:
- **SFT**: (prompt, ideal response) demonstrations.
- **DPO**: (prompt, preferred, rejected) pairs. Use it when quality depends on preferences such as tone or completeness.
- **RFT**: prompts plus a **grader** that scores responses. Use it when many answers are valid and quality can be scored reliably. Microsoft says graders "should be tested against correct, incorrect, and adversarial responses", because reward hacking is the default failure.

**Distillation** is SFT on teacher-generated data. **Interactive training** (preview, approval required, **[Python]**) lets you write your own training loop, controlling losses, rewards, rollouts and checkpoints.

Fine-tunable models listed on Learn (page updated 2026-10-08). Treat this list as perishable:

| Model | Methods | Notes |
|---|---|---|
| `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano` | SFT, DPO | The practical cloud student family |
| `gpt-4o` | SFT, DPO | Older |
| `gpt-4o-mini` | SFT | Older |
| `o4-mini` | RFT | Reasoning RFT |
| `gpt-5` | RFT | Invitation only |
| `gpt-oss-20b` | SFT | Open weights |
| `gpt-oss-120b` | SFT, RFT | Preview |
| `Qwen3-32B` | SFT | |
| `Qwen3.6-35B-A3B`, `Qwen3.8-27B` | SFT, RFT | Preview; 35B-A3B is MoE |
| `Muse-Glimmer-30B` (Meta) | SFT, RFT | Preview, Apache-2.0 |
| `Llama-3.3-70B-Instruct` | SFT | |
| `Ministral-3B` | SFT | Smallest listed LLM |
| `MAI-Code-1.1-Flash` | RFT | Preview |

**No GPT-5.x/GPT-6 SFT is listed.** You cannot fine-tune the current frontier tier. You distil from it.

**Training tiers:** Standard (in-region, keeps residency), Data zone (US only; verify against current documentation), Global (cheaper, no residency guarantee), Developer (lowest cost, preemptible, no SLA). Build 2026 also announced a developer tier "with no hosting fees" and "Frontier Tuning", whose scope is undescribed: verify against current documentation. For Trakia's GDPR-bound data, **Global and Data zone are out**. Use Standard in an EU region where the model is trainable (verify per model). Use Developer only on synthetic or fully pseudonymized data, and record that in the DPIA (C18).

**Deployment:** Serverless (the usual OpenAI-family path), Managed compute (preview; base model plus compatible **LoRA adapters**), or Fireworks on Foundry (preview; one merged adapter).

Prices were not collected for this release, so take them from the pricing page on the day you teach. RFT grader types were not verified, so check the RFT how-to before Lab 2's stretch.

### 3. PEFT, LoRA and QLoRA — enough math to make decisions

LoRA freezes a weight matrix W (d_out × d_in) and learns a low-rank update ΔW = B·A, where B is d_out × r and A is r × d_in, scaled by α/r. Trainable parameters per adapted matrix are r·(d_in + d_out).

Worked example: d_in = d_out = 4096 and r = 16 give 131,072 trainable parameters, against 16.8M for the full matrix (0.78%). Adapt Q, K, V and O in 32 layers and the adapter is ~16.8M parameters, about 34 MB in FP16. You can ship that over a depot's slow link. A full 8B checkpoint is ~16 GB.

**Rank choice.** r = 8–16 is the usual starting band for classification or format tasks. Raise r only when the validation loss plateaus high (underfitting). Adapting MLP layers as well as attention layers adds capacity, and with it the risk of forgetting.

**QLoRA** trains LoRA adapters on top of a base frozen in 4-bit NF4, which lets you fine-tune a 7–8B model on a single GPU. The adapter is trained in higher precision. When you later **merge** the adapter and **re-quantize** for serving, you introduce a second quantization error, so you must evaluate after the final export, not after training.

**Serving adapters.**

| Pattern | When | Trade-off |
|---|---|---|
| Merge into base, then quantize | One task per edge device | Simplest runtime. A new task means a new full model |
| Hot-swap adapters on a shared base (multi-LoRA) | Many tasks or tenants on one GPU (vLLM supports this; Foundry managed compute lists base + compatible LoRA adapters, preview) | Small per-task artifacts. Batching across adapters is engine-specific |
| One merged adapter on a hosted platform (Fireworks on Foundry, preview) | Managed serving of an open model | Vendor-specific limits |

### 4. Data preparation: where most fine-tunes actually fail

- **Format.** Chat-format JSONL with the *same* system prompt and schema used at inference. A prompt mismatch silently kills quality.
- **Grouped splits.** Trakia's work orders repeat (same truck, same DTC, same phrasing), so a random split leaks near-duplicates into test. Split by **vehicle** and report random-split vs grouped-split scores. The gap is your leakage estimate.
- **Dedup.** Exact hash plus near-duplicates (embedding cosine > 0.95 or MinHash).
- **Label audit.** Mechanic-confirmed resolutions are ground truth; teacher labels are not. Have an expert adjudicate 100 labels per class and measure the teacher–expert agreement.
- **Critical tail.** `StopNow` (oil pressure, brakes) may be 4% of rows. Oversample it in training, never in test, and track its recall separately.
- **Quantity.** Hundreds of examples move format and policy. Distilling a 15-class decision wants low thousands. Plot learning curves at 250/500/1,000/2,000.
- **PII.** Scrub names and phone numbers from free-text notes. "Forget a driver" means re-training, not editing weights, so document it in the DPIA.

### 5. Evaluation before and after — the experiment design

Freeze one **test set** (grouped split, never used for prompt tuning or checkpoint selection) and one **dev set** (for epoch and rank choice). Every candidate gets the same matrix:

| Dimension | Metric | Why |
|---|---|---|
| Target task | Macro-F1 (severity), accuracy (subsystem) | Overall quality |
| Safety tail | Recall and precision on `StopNow`, with a 95% Wilson interval | A miss is the expensive error |
| Cost-weighted error | Σ errors × business cost matrix (missed `StopNow` = 100, false `StopNow` = 5) | Turns F1 into money |
| Format adherence | % schema-valid outputs without repair | Small models break schemas |
| General regression | Pass rate on a 100-item "keep" suite (BG/EN fleet Q&A, refusals, the instruction-following checks from C5) | Catastrophic forgetting |
| Calibration | Reliability of the confidence field or logprob threshold | Needed for cascades (D5) |
| Ops | p50/p95 latency on target hardware, € per 1,000 calls, memory footprint | The reason you are here |

Use **paired** comparisons (the same items, models A and B) and McNemar's test for "is the student really worse?". With 600 test items, a 2-point F1 difference is often noise. See D7 for the statistics.

### 6. Overfitting and catastrophic forgetting

**Overfitting** shows as validation loss turning up while training loss falls, verbatim reproduction of training phrasings, and dev scores far above grouped-test scores. Mitigate with fewer epochs (start at 2–3), a lower learning-rate multiplier (Foundry's hyperparameter names vary by model, so verify them), more diverse data, and early stopping or checkpoint selection on dev.

**Catastrophic forgetting** is the loss of prior skills: no more refusals, no more Bulgarian, ignored system instructions. The keep suite detects it. Mitigate with LoRA instead of full fine-tuning, a lower rank, 10–20% general instruction data mixed in, and a narrow task. Accept forgetting deliberately only for a single-purpose component behind a router, and say so in the ADR.

### 7. Distillation done properly

Teacher-to-student distillation ("knowledge distillation", Hinton et al.) here means the frontier model labels a large unlabeled pool and the small model is trained on those labels.

**Expert refinements:**
1. **Filter teacher outputs.** Keep items where the teacher matches confirmed outcomes or two teacher runs agree. Teacher errors become student beliefs.
2. **Labels vs rationales.** A short distilled rationale can help on multi-factor cases but costs output tokens, so measure both.
3. **Distil the policy, not the prompt.** The point is to remove the long few-shot prefix from every call.
4. **Verifiable labels → consider RFT.** A code grader (parses, severity equals the confirmed outcome, subsystem consistent with the DTC family) rewards the true objective. Test it against adversaries: "always `StopNow`" must not score well.

### 8. Small models, memory and quantization

**Weight memory** ≈ parameters × bytes per parameter: FP16 = 2, INT8 = 1, INT4 ≈ 0.5 (plus ~5–10% for scales and zero-points).

**KV cache** per sequence ≈ 2 × layers × kv_heads × head_dim × tokens × bytes. GQA shrinks kv_heads, so read it from the model card.

For **MoE**, memory follows **total** parameters and compute follows **active** parameters. A "35B-A3B" model needs ~17–18 GB at INT4 even though each token uses ~3B parameters.

| Model class | FP16 | INT8 | INT4 | Depot fit (16 GB RAM, iGPU/NPU) |
|---|---|---|---|---|
| ~3B dense | 6 GB | 3 GB | ~1.7 GB | Yes |
| ~8B dense | 16 GB | 8 GB | ~4.5 GB | INT4 only |
| ~27B dense | 54 GB | 27 GB | ~15 GB | No (a ternary 27B at 5.9 GB is a vendor claim; verify) |
| 35B-A3B MoE | 70 GB | 35 GB | ~18 GB | No |
| 120B (gpt-oss-120b) | 240 GB | 120 GB | ~60 GB | Server GPU only |

**Formats and methods:**
- **GGUF** is llama.cpp's container. Its quant levels (for example Q8_0, Q4_K_M) are used by LLamaSharp and Ollama.
- **GPTQ** and **AWQ** are post-training weight quantization methods.
- **ONNX INT4** models run on ONNX Runtime GenAI, which Foundry Local wraps.

Quantization loss is **not uniform**. It concentrates on rare tokens and rare classes. Always re-run the safety-tail metric after quantization.

### 9. Local runtimes behind one abstraction

All four .NET local options plug into `Microsoft.Extensions.AI` `IChatClient`, so the application code does not change:

| Runtime | Model format | Hardware | Use when |
|---|---|---|---|
| **Foundry Local** (GA 9 Apr 2026; C# SDK `Microsoft.AI.Foundry.Local`) | ONNX, from a curated catalogue (GPT OSS, Qwen, Whisper, DeepSeek, Mistral, Phi) | Automatic GPU/NPU/CPU EP selection; Windows ML EPs on Windows, Metal on Apple silicon; Linux x64 | Managed path; OpenAI-compatible API incl. Responses; ~20 MB runtime; offline |
| ONNX Runtime GenAI | ONNX | CUDA, OpenVINO, QNN, TensorRT EPs | Maximum control; custom ONNX exports |
| LLamaSharp | GGUF | CPU, CUDA, Metal, Vulkan | Bring-your-own GGUF; quick quant comparisons |
| Ollama | GGUF (external runner) | Varies | Prototyping only |

Foundry Local also runs **on Azure Local (preview)** for on-prem servers. Loading *your own* fine-tuned or converted model into Foundry Local (rather than a catalogue model) was not confirmed in our sources, so verify against current documentation. The lab keeps ONNX Runtime GenAI and LLamaSharp as GA-independent fallbacks.

**vLLM** (self-hosted serving on AKS GPU nodes) introduced three ideas: PagedAttention (KV cache managed like virtual memory), continuous batching, and multi-LoRA serving. It is the reference engine when Trakia sells the product to other fleets and needs one GPU pool serving per-tenant adapters (A-track). Throughput claims depend on the hardware, so measure them with a load test (D5).

**Edge as artifact.** Version an edge model in the registry with a content hash, data snapshot ID and eval report. Roll it out per depot (Varna as canary) and log local decisions to an outbox that syncs when the link returns. Low-confidence inputs go to the cloud when it is reachable, otherwise to a conservative default. For safety triage that default is "escalate to a mechanic", never "continue driving".

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| Microsoft Foundry fine-tuning (SFT, DPO, RFT, distillation) | Managed training | GA (per-model; several models preview) | Learn fine-tuning overview updated 2026-10-08; model list volatile |
| Foundry interactive training | Custom training loops | Preview, approval required | **[Python]** |
| Foundry managed compute with LoRA adapters | Serve base + adapters | Preview | Verify the supported base models |
| Fireworks on Foundry (fine-tuned deploy) | One merged adapter | Preview | Fireworks on Foundry itself GA at Build 2026 |
| `Azure.AI.Projects` 2.0.0, `Azure.AI.Extensions.OpenAI` 2.0.0 | Jobs, deployments, inference from .NET | GA | Do not mix with preview `Azure.AI.Projects.OpenAI` |
| `OpenAI` .NET package against `/openai/v1/` | Files and fine-tuning jobs API | GA | Calls need `#pragma warning disable OPENAI001` |
| Foundry Local + `Microsoft.AI.Foundry.Local` C# SDK | On-device inference | GA (blog, 9 Apr 2026; Learn page carries no label) | NuGet `Microsoft.AI.Foundry.Local.Runtime` 2.0.1 observed |
| `Microsoft.ML.OnnxRuntimeGenAI.Foundry` | ONNX Runtime GenAI | Available (0.15.2 observed) | Verify the exact package for direct ORT GenAI use |
| LLamaSharp | GGUF inference in .NET | Community, active | Pin version; native backends per OS |
| Ollama | Local runner | Stable | Prototyping |
| Hugging Face PEFT / TRL, bitsandbytes | LoRA/QLoRA training | OSS | **[Python]**; run in the scripts devcontainer |
| ML.NET | Classical classifier baseline | GA | AutoML for the baseline |
| `Microsoft.Extensions.AI` 10.x, `.Evaluation` | Abstraction + eval harness | GA | Abstractions 10.5.0 |
| vLLM | Self-hosted serving | OSS | Concepts and stretch lab only |

## Labs

Lab repo: `trakia-fleetops`. All models are referenced by role in `appsettings.json`, for example `Models:Teacher`, `Models:CloudStudent`, `Models:EdgeSlm`. The fault-code dataset is generated from `TrakiaOps.MaintenanceWorkOrders` joined to `TelematicsEvents` (DTC events) with the mechanic-confirmed resolution as ground truth.

### Lab 1 — Baseline matrix and a leakage-proof eval harness (≈2.5h)

- **Goal:** Establish the bar every customized model must beat, and prove the test set does not leak.
- **Start state:** tag `d1/lab1-start`. It contains `FaultTriage` contracts, a 1,400-row labeled export and an empty `Trakia.FaultTriage.Evals` xUnit project.
- **Steps:**
  1. Define the output contract:
     ```csharp
     public enum Severity { Continue, ScheduleWithin7Days, StopNow }
     public sealed record FaultTriage(Severity Severity, string Subsystem, double Confidence, string? Rationale);
     public sealed record FaultCase(string CaseId, string VehicleId, string Dtc, string TelematicsSummary, string MechanicNote, string Lang);
     ```
  2. Build grouped splits by `VehicleId` (60/20/20), with dedup by normalized `(Dtc, MechanicNote)` hash plus embedding similarity > 0.95. Persist `splits.json` with the dataset snapshot hash.
  3. Implement `ITriageModel` over `IChatClient`, using structured output:
     ```csharp
     ChatResponse<FaultTriage> r = await chat.GetResponseAsync<FaultTriage>(
         [new(ChatRole.System, TriagePrompt.V1), new(ChatRole.User, fc.ToPromptText())],
         new ChatOptions { Temperature = 0 }, ct);
     ```
  4. Run four baselines on dev and test: (a) frontier model zero-shot, (b) frontier with 12 curated few-shot examples and a prompt-cache-friendly prefix, (c) the fast small cloud model with few-shot, (d) an **ML.NET** multiclass classifier (text featurizer over DTC + note, plus one-hot DTC family).
  5. Compute the full matrix from Concepts §5 per baseline: macro-F1, `StopNow` recall with a Wilson 95% CI, cost-weighted error, schema validity, p50/p95 latency and € per 1,000 calls (from the usage tokens × prices in config).
  6. Emit `baseline-report.md` and `baseline.json` as CI artifacts.
- **Break it:** Re-run with a *random row* split. Record the inflation in macro-F1 for the ML.NET model and for few-shot. Explain in three sentences why near-duplicate work orders cause it.
- **Acceptance criteria:**
  - `dotnet test --filter Category=Baseline` passes.
  - The report contains all 4 baselines × 7 metrics.
  - A test asserts **zero vehicle overlap** between the train and test splits.
  - The random-vs-grouped gap is reported.
- **Stretch:** Add a "decision model"-style baseline, logprob thresholding on a single severity token, and plot its calibration.

### Lab 2 — Distil a cloud student with Foundry SFT, then overfit it on purpose (≈3.5h)

- **Goal:** Train a small cloud model that removes the few-shot prefix and the frontier price, and observe overfitting and forgetting with your own eyes.
- **Start state:** tag `d1/lab2-start` (Lab 1 solution + 6,000 unlabeled historical work orders).
- **Steps:**
  1. Label the unlabeled pool with the teacher at temperature 0, twice. Keep items where both runs agree **and** (where available) the teacher matches the confirmed resolution. Report the yield and the teacher–expert agreement on a 150-item adjudicated sample.
  2. Write chat-format JSONL with the **short production prompt** (no few-shot). Oversample `StopNow` ×3 in train only. Mix in 10% general instruction items from the keep suite's *training* partition.
  3. Upload the data and create an SFT job on the `Models:CloudStudent` base (for example `gpt-4.1-nano` or `gpt-4.1-mini`) in a Standard EU region. Use the Developer tier only if the pool is fully pseudonymized. Use the `OpenAI` client against `/openai/v1/` or the Foundry project client:
     ```csharp
     #pragma warning disable OPENAI001
     // Shape only — verify exact fine-tuning client/method names against current OpenAI .NET + Foundry docs
     var files = openAi.GetOpenAIFileClient();
     var trainFile = await files.UploadFileAsync("train.jsonl", FileUploadPurpose.FineTune);
     var ft = openAi.GetFineTuningClient();
     var job = await ft.FineTuneAsync(baseModel: cfg["Models:CloudStudent"], trainingFileId: trainFile.Value.Id,
         waitUntilCompleted: false, options: new() { ValidationFile = valFile.Value.Id /* epochs, lr multiplier: verify names */ });
     ```
  4. Deploy the resulting model (serverless) and evaluate it with the Lab 1 harness on the **same** test split. Add it to the matrix.
  5. **Overfit experiment:** train a second job on only 20 examples for many epochs. Plot the training vs validation loss from the job's metrics, and run the keep suite.
- **Break it:** Train a variant with the long few-shot prompt in training but the short one at inference, and measure the drop. Run the keep suite in Bulgarian and record any forgetting.
- **Acceptance criteria:**
  - The student reaches macro-F1 ≥ (frontier few-shot − 2.0) **and** `StopNow` recall ≥ 0.97 on the grouped test, or the lab report explains why not with evidence.
  - The keep-suite pass rate drops by ≤ 3 points.
  - `€/1k calls` ≤ 10% of the frontier few-shot cost.
  - The overfit run's loss plot and keep-suite delta are committed under `reports/d1/`.
- **Stretch:** Write a C# grader (schema valid ∧ severity equals the confirmed outcome ∧ subsystem consistent with the DTC family). Test it against an "always StopNow" adversary and a "copy the mechanic note" adversary. Then sketch an RFT job on an RFT-capable model (verify the grader types first).

### Lab 3 — LoRA/QLoRA an open-weight edge model and measure quantization loss (≈4h) [Python]

- **Goal:** Produce a small open-weight model that can run at a depot, and measure what each compression step costs on the critical class.
- **Start state:** tag `d1/lab3-start`. It contains the `scripts/` devcontainer with pinned Python, PEFT/TRL and the ONNX tooling.
- **Steps:**
  1. Pick `Models:EdgeSlm`, a ≤ 4B-parameter open-weight instruct model whose licence permits commercial fine-tuning. Record the licence in `models/LICENCES.md`.
  2. Run QLoRA (NF4 base, r = 16, α = 32, attention projections only, 2 epochs) on the Lab 2 distilled data. Save the adapter (~tens of MB) and log the loss curves.
  3. Merge the adapter into the base. Export (a) an **ONNX INT4** model for ONNX Runtime GenAI or Foundry Local (verify the current export tooling) and (b) **GGUF Q8_0 and Q4_K_M** for LLamaSharp.
  4. Back in C#, register three `IChatClient`s (ORT GenAI INT4, LLamaSharp Q8, LLamaSharp Q4) by keyed DI and run the Lab 1 harness on each.
  5. Record the quality ladder: base SLM few-shot → LoRA FP16 → INT8/Q8 → INT4/Q4.
- **Break it:** Quantize the model *before* merging (merge an FP16 adapter into an already-INT4 base) and compare `StopNow` recall. Explain the double-quantization effect.
- **Acceptance criteria:**
  - The report shows the quality ladder with `StopNow` recall CIs.
  - The chosen export loses ≤ 1.5 macro-F1 points relative to LoRA FP16 and keeps `StopNow` recall ≥ 0.97.
  - Artifacts are hash-pinned in `models/manifest.json`, alongside the training-data snapshot hash.
- **Stretch:** Serve two adapters (triage + Bulgarian incident summary) on one base with vLLM and compare memory and latency against two merged models.

### Lab 4 — Deploy to the depot edge with Foundry Local and an offline-first fallback chain (≈3.5h)

- **Goal:** Run triage at the Varna depot with no cloud dependency, and degrade safely.
- **Start state:** tag `d1/lab4-start`. It contains the `Trakia.Depot.Edge` .NET 10 Worker Service and an Aspire AppHost that simulates depot and cloud.
- **Steps:**
  1. Start Foundry Local from the C# SDK and wrap it as `IChatClient`:
     ```csharp
     // Shape only — verify exact Microsoft.AI.Foundry.Local API (manager, model load, endpoint) against current docs
     var manager = await FoundryLocalManager.StartModelAsync(aliasOrModelId: cfg["Models:EdgeSlmAlias"]);
     IChatClient edge = new OpenAIClient(new ApiKeyCredential(manager.ApiKey),
             new OpenAIClientOptions { Endpoint = manager.Endpoint })
         .GetChatClient(manager.ModelId).AsIChatClient();
     ```
     If your fine-tuned export cannot be loaded into Foundry Local, register the Lab 3 ORT GenAI client under the same key. The application code must not change.
  2. Build the pipeline with `ChatClientBuilder`: OTel → a schema-validation middleware → a `ConfidenceGate` middleware → the inner client.
  3. Implement `FallbackTriageModel`:
     - edge first;
     - if the confidence is < τ, the output is schema-invalid, or the DTC family was not in the training distribution, call the cloud student when connectivity is up;
     - if the cloud is down, return `Severity.StopNow` with `Subsystem = "escalate-to-mechanic"` and raise a depot alert.
     Tune τ on dev to keep `StopNow` recall ≥ 0.98 end to end.
  4. Write every decision to a local SQLite outbox. A background service syncs the outbox to App Insights with idempotent upserts.
  5. Measure p50/p95 latency on CPU-only and (if present) GPU/NPU, using the course's reference depot spec (16 GB RAM).
- **Break it:**
  - Disconnect the network mid-run (toxiproxy in the AppHost). Verify there is no lost decision and no unsafe default.
  - Then disable the GPU/NPU execution provider and check whether the p95 budget still holds on CPU. Record the result honestly.
- **Acceptance criteria:**
  - The integration test `EdgeOfflineTests` passes: 200 cases with the network down give 0 exceptions, 100% are persisted, and every low-confidence case is escalated.
  - p95 < 400 ms on the reference spec, or a documented exception.
  - Swapping `Models:Provider` from `FoundryLocal` to `Ollama` in config passes the same tests with no code change.
- **Stretch:** Canary roll-out. Ship model v2 to Varna only, compare decision distributions against Plovdiv for drift, and automate rollback on a `StopNow`-rate anomaly.

### Lab 5 — Decision report and ADR (≈1.5h)

- **Goal:** Turn the measurements into a decision another engineer can reproduce and challenge.
- **Start state:** your Lab 1–4 artifacts.
- **Steps:**
  1. Build one table covering frontier zero-shot, frontier few-shot, ML.NET, cloud student, edge SLM base, edge LoRA INT4 and edge + cloud fallback. Columns: macro-F1, `StopNow` recall (CI), cost-weighted error, € per 1,000 calls, p95, data residency and an operational burden score.
  2. Write `docs/adr/ADR-0D1-fault-triage-model.md`. It records the chosen architecture, the rejected options with evidence, the retraining triggers (base model deprecation notice, drift on the DTC mix, new truck models) and the owner.
  3. Add the retirement date of every base model used to the model registry.
- **Break it:** Ask a peer to reproduce one row from your manifest alone. Fix whatever they could not reproduce.
- **Acceptance criteria:** The ADR links every number to a committed artifact, and a CI job re-runs the test-set evaluation for the chosen model nightly.
- **Stretch:** Add a DPO plan. Specify how thumbs-down feedback from mechanics (C15 feedback events) becomes preference pairs, and what minimum volume would justify a run.

## Kata

**"Which rung?" (25 min, repeat 4×).** The instructor hands you a failure cluster from a trace sample, with counts. Variations:
1. Answers cite a superseded maintenance bulletin.
2. Severity is correct but the JSON breaks on Bulgarian notes.
3. Mechanics prefer terser rationales.
4. Classification is correct but costs €0.004 per call at 40k calls/day.

In 25 minutes, write a one-paragraph decision. Name the rung and why the lower rungs do not suffice, the metric and target, the data you need (with volume), the expected cost (training + hosting + inference/month), and the trigger that would make you revisit the decision. The instructor reveals the "expert answer", including the cases where the answer is "don't customize".

## Product increment — Fleet Ops Copilot

The **fault-code triage capability** now runs on a distilled, LoRA-tuned small model at the depots via Foundry Local (or the ORT GenAI fallback). It sits behind the same `IChatClient` contract, with a confidence-gated cloud fallback and a safe offline default. The cloud student serves the central Fleet Assistant (C9) as a cheap first tier, ready for the cascade in D5. The model registry records the dataset snapshot, eval report, licence and base-model retirement date for every model.

## Factory increment — your agentic SDLC

- A `/finetune-experiment` **skill** (Claude Code and Copilot custom agent) scaffolds the dataset card, grouped splits, the eval matrix and an ADR stub from a template. It refuses to submit a training job unless `baseline.json` exists and the success criterion is filled in.
- A **pre-commit hook** blocks commits of JSONL training files that fail the PII scanner or lack a dataset snapshot hash.
- CI gains a nightly `model-eval` workflow for each registered model. It opens an issue when a metric drifts or a base model's retirement is under 120 days away (Models API lifecycle status).
- The coding agent may write data-prep code and eval harnesses. **Humans own** the label adjudication and the success criterion, and this is recorded in `AGENTS.md`.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Ladder decision | Fine-tunes by default | Picks a plausible rung | Justifies the rung with error analysis and a cost estimate | Pre-registers a target; shows when *not* to customize; plans retraining against base-model retirement |
| Data & leakage | Random split, no dedup | Dedup only | Grouped split, PII scrub, label audit | Quantifies leakage (random vs grouped gap) and teacher–expert agreement; dataset card reproducible from a hash |
| Evaluation | Single accuracy number | Macro-F1 on held-out data | Full matrix incl. safety tail and keep suite | Paired significance tests, CIs, cost-weighted error; post-export (quantized) re-eval |
| Edge engineering | Runs a local model in a demo | `IChatClient` swap works | Fallback chain + outbox | Offline-safe defaults proven by tests; per-depot canary with rollback; honest CPU-only numbers |
| Communication | Screenshots | Report with numbers | ADR with rejected options | ADR another engineer reproduces from manifests; clear retraining triggers and owner |

**Auto-checked:**
- the CI test categories `Baseline`, `Student`, `Edge`, `EdgeOffline`;
- the zero-overlap split assertion;
- the threshold gates (macro-F1 delta, `StopNow` recall ≥ 0.97, p95);
- the presence and schema of `models/manifest.json`;
- the nightly `model-eval` workflow status.

## Common pitfalls

- Training with one system prompt and serving with another.
- Random splits on repetitive operational data.
- Trusting teacher labels as ground truth.
- Evaluating the LoRA checkpoint instead of the shipped, quantized artifact.
- Oversampling the rare class in test.
- Ignoring the base model's lifecycle. A fine-tune on a retired base returns `410 Gone` too.
- Global or Data zone training tiers for EU personal data.
- Measuring on a laptop instead of the depot reference spec (CPU-only included).
- An unsafe fallback ("when in doubt, continue driving").
- Skipping the ML.NET baseline, which is often within a point of the LLM at a fraction of the cost.


## References

- Microsoft Learn — Foundry fine-tuning overview (methods, tiers, deployment, interactive training preview): https://learn.microsoft.com/en-us/azure/foundry/fine-tuning/overview
- Microsoft Learn — Models sold directly by Azure (fine-tunable list, context limits): https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure
- Microsoft Learn — Foundry model retirements and lifecycle: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
- Foundry blog — Foundry Local GA (9 Apr 2026): https://devblogs.microsoft.com/foundry/foundry-local-ga/
- Microsoft Learn — What is Foundry Local: https://learn.microsoft.com/en-us/azure/foundry-local/what-is-foundry-local
- Foundry blog — What's new at Build 2026 (developer training tier, Frontier Tuning): https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-build-2026/
- Managed Code — Local LLMs in C#: LLamaSharp vs ONNX vs Foundry Local (Jun 2026, practitioner): https://www.managed-code.com/blog-post/running-local-llms-csharp-llamasharp-vs-onnx-vs-foundry-local
- NuGet — Microsoft.AI.Foundry.Local.Runtime: https://www.nuget.org/packages/Microsoft.AI.Foundry.Local.Runtime/ ; Microsoft.ML.OnnxRuntimeGenAI.Foundry: https://feed.nuget.org/packages/Microsoft.ML.OnnxRuntimeGenAI.Foundry/
- Hu et al., LoRA: https://arxiv.org/abs/2106.09685 · Dettmers et al., QLoRA: https://arxiv.org/abs/2305.14314 · Hinton et al., Distillation: https://arxiv.org/abs/1503.02531
- Rafailov et al., DPO: https://arxiv.org/abs/2305.18290 · DeepSeek-R1 (RL with verifiable rewards): https://arxiv.org/abs/2501.12948
- Frantar et al., GPTQ: https://arxiv.org/abs/2210.17323 · Lin et al., AWQ: https://arxiv.org/abs/2306.00978 · llama.cpp / GGUF: https://github.com/ggml-org/llama.cpp
- Kwon et al., PagedAttention / vLLM: https://arxiv.org/abs/2309.06180 · Fedus et al., Switch Transformers (MoE): https://arxiv.org/abs/2101.03961
- ML.NET: https://dotnet.microsoft.com/apps/ai/ml-dotnet
- Chip Huyen, *AI Engineering* (ch. 7 Finetuning, ch. 8 Dataset engineering): https://github.com/chiphuyen/aie-book
