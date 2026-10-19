# C1 — How generative AI works: an engineer's mental model

> **Level:** 1 — Foundations (Beginner) · **Duration:** 10h (theory 30% / labs 70%) · **Prerequisites:** C0 (environment, `chat-fast`/`chat-reasoning`/`chat-local` roles working) · **Volatility:** Low for mechanics; High for the model landscape and prices

## Why this matters

Trakia Freight's CFO asks a simple question: "If 600 drivers each ask the copilot ten questions a day, what does it cost, and can we trust the answers?" An engineer without a mental model of LLMs answers with a per-token price from a vendor page and a demo. Three months later the bill is 4× the estimate (Bulgarian text is token-heavier, the reasoning model spends hidden thinking tokens, the system prompt is resent with every turn), the regression tests are flaky ("but we set temperature to 0"), and a dispatcher acted on a confidently invented regulation.

Every one of those failures follows from mechanics you can learn in a day: text is billed and limited in *tokens*, not words; the model outputs a *probability distribution* and something samples from it; serving infrastructure is *not batch-invariant*, so even greedy decoding varies; *input, output and reasoning tokens share one context budget*; training and benchmarks *reward guessing over abstaining*, so hallucination is structural; and *price per token is not cost per task*. Experts don't memorize transformer math — they predict system behavior from these facts and then measure it.

This module is deliberately "predict → run → explain". For every claim you will first predict the outcome, then measure it against Trakia data with your own .NET harness, then explain the gap. The harness you build becomes the seed of the eval infrastructure in C5.

## Learning outcomes

By the end of C1 you can:

1. **Explain** the pipeline text → tokens → embeddings → attention/MLP (or MoE) layers → next-token distribution → sampling, and predict how each stage affects cost, latency and failure modes.
2. **Measure** token counts for the same content in English and Bulgarian with `Microsoft.ML.Tokenizers` and reconcile them with provider-reported usage.
3. **Demonstrate** nondeterminism at temperature 0 and choose test strategies (schemas, graders, pass rates) that tolerate it.
4. **Compare** reasoning effort levels on accuracy, latency and cost for a Trakia task, and justify a default.
5. **Calculate** cost per task (not per token) for a feature, including system-prompt resend, reasoning tokens and caching.
6. **Describe** pretraining vs post-training (SFT, RLHF, DPO, RLVR) and use that to explain knowledge cutoffs, refusal behavior and why fine-tuning does not teach fresh facts.
7. **Classify** current models by capability class and choose a class (not a name) for a requirement.
8. **Decide** when *not* to use an LLM (classical ML, OCR/document models, rules) and defend the choice with evidence.
9. **Apply** the minimal ML vocabulary (loss, gradient descent, overfitting, train/val/test) to prompt iteration and eval sets.

## Concepts

### 1. Minimal ML you actually need

- **Supervised learning loop:** data → model with parameters → **loss** (a scalar measuring error) → **gradient descent** updates parameters to reduce loss → evaluate on **held-out** data. LLM pretraining minimizes next-token **cross-entropy** — self-supervised, labels come from the text itself.
- **Train / validation / test:** fit on train, tune on validation, report once on test. The same discipline governs prompts: if you tweak a prompt until your 50 golden cases pass, those 50 cases are now *training* data; you need a held-out set (Gate G1's hidden suite exists for exactly this reason).
- **Overfitting:** a model (or prompt) that memorizes its training examples and degrades on new ones. In LLM land: a prompt full of special cases for your eval set; a fine-tune on 20 examples that loses general capability.
- **Parameters and memory:** weights are numbers; memory ≈ params × bytes/param (FP16 = 2, INT8 = 1, INT4 ≈ 0.5) plus KV cache. **Fine-tuning changes weights; prompting and RAG do not.** That single distinction drives most architecture decisions.

### 2. Tokens and BPE

LLMs see **token IDs**, produced by subword tokenizers such as **byte-pair encoding (BPE)**: frequent character sequences become single tokens, rare ones split into several. Consequences:

- **Cost and limits are in tokens.** Context windows, rate limits (TPM), prices and max output are all token-denominated.
- **Language skew.** Tokenizer vocabularies are trained on corpora dominated by English; Cyrillic Bulgarian typically needs more tokens per word. No published measurement for current tokenizers was found, so *you* will produce Trakia's number in Lab 1. Expect it to matter for budgets, context limits and latency (output tokens are generated one at a time).
- **Quirks:** spelling, character counting, arithmetic on long numbers, and look-alike characters (Bulgarian licence plates use Cyrillic letters that have Latin homoglyphs: "РВ 4521 КН" in Cyrillic vs "PB 4521 KH" in Latin are different token sequences and different strings to your database).
- Different model families use different tokenizers; a local count is an *estimate*. The provider's reported `usage` is the bill.

### 3. Embeddings, attention, layers — at practitioner depth

- **Embeddings:** each token ID maps to a learned vector; geometry encodes meaning. Embedding *models* (C6) produce one vector per text for search.
- **Self-attention:** each position computes queries, keys and values; output = softmax(QKᵀ/√d)·V, i.e. every token mixes information from previous tokens weighted by relevance. Many heads, many layers, interleaved with feed-forward (MLP) blocks.
- **Position:** rotary position embeddings (RoPE) encode order; context-extension tricks build on them, which is one reason quality degrades unevenly over very long contexts.
- **Practical consequences:** attention cost grows with context length (FlashAttention and grouped-query attention make long contexts affordable, not free); prompt *order* matters; information in the **middle of long contexts is used less reliably** ("lost in the middle"); one irrelevant distractor measurably hurts (context rot — C13).

### 4. Context window and KV cache

- **One budget.** On Azure, current GPT-5.x/GPT-6 models have a 1,050,000-token window (922,000 input, 128,000 output). Microsoft: "Input tokens, generated output tokens, and reasoning tokens share the available context budget"; max output is "an upper limit, not a guaranteed output size." Claude 5.5-generation models: 1M context, 128K max output.
- **KV cache:** during generation the model stores keys/values for prior tokens so it doesn't recompute them. This explains **TTFT** (time to first token: processing the whole prompt, "prefill") vs **inter-token latency** (decode, roughly constant per token), why long prompts cost memory, and why **prompt caching** works: providers reuse the KV cache of an identical prefix at a discount. Example (Claude Opus 5.5 list): base input $4/MTok, cache read $0.20/MTok, cache write $5/MTok (5-min TTL), minimum cacheable prompt 512 tokens (cache-write price, TTL and minimum: verify against current documentation); Batch API −50%. Consequence for design: **static content first** (system prompt, tool schemas, policies), dynamic content last (C3).
- **"1M context" ≠ "use 1M".** Cost scales linearly, latency grows, and quality on long inputs degrades; focused ~300-token inputs beat ~113k-token inputs for every model family in Chroma's 2025 study.

### 5. Pretraining vs post-training

- **Pretraining:** next-token prediction on huge corpora → a *base* model that continues text. Knowledge is frozen at the **cutoff**.
- **Post-training** turns it into an assistant:
  - **SFT** — supervised fine-tuning on (prompt, ideal response) demonstrations.
  - **RLHF** — reward model trained on human rankings, then RL (InstructGPT). **RLAIF/Constitutional AI** replaces much human labeling with AI feedback against written principles.
  - **DPO** — optimize directly on preferred/rejected pairs, no separate reward model.
  - **RLVR** — RL with *verifiable* rewards (unit tests, math checkers); DeepSeek-R1 showed long chain-of-thought reasoning emerging from it.
- These are now *your* tools too: Foundry offers managed **SFT, DPO and RFT** (reinforcement fine-tuning with a grader) — D1. Microsoft's own guidance: fine-tuning benefit "isn't guaranteed" (compare against a baseline with held-out evaluation) and it "doesn't replace retrieval for current information."

### 6. Reasoning models and test-time compute

As of October 2026, effectively every frontier model is a **reasoning model**: it spends extra (often hidden) **reasoning tokens** before answering, and you control depth with an **effort** parameter. Claude 5.5-generation models use adaptive thinking with `effort` (Opus 5.5 default `medium`); Azure GPT models expose `reasoning_effort`, except `gpt-chat-latest`, which uses a fixed level you cannot set. `MAI-Thinking-1` (preview) ships **encrypted** chain-of-thought — billed, not readable. Test-time compute can substitute for model size on some tasks, but:

- reasoning tokens are **billed** and **consume the context budget**;
- they inflate **latency** (and TTFT perceived by users);
- higher effort helps multi-step reasoning, rarely helps lookup or extraction;
- many reasoning endpoints restrict or ignore sampling knobs (temperature/top-p) — your abstraction layer must tolerate provider-specific parameters (C2).

### 7. Mixture-of-Experts and multimodality

- **MoE:** a router activates a few expert feed-forward blocks per token. **Memory follows total parameters; compute follows active parameters.** A "35B-A3B" model needs memory for 35B weights but computes like ~3B per token — vital when sizing local or self-hosted models (D1). Reported 2026 extremes: ~2.8T total / ~104B active (Kimi K3, aggregator figure).
- **Multimodality:** text+image input is standard at the frontier; Azure's catalog adds realtime speech-to-speech, transcription with diarization, TTS, image generation and (unstable) video. Each has distinct latency/cost profiles (D3).

### 8. Sampling

The model outputs **logits** → softmax → a probability distribution over the vocabulary. Then:

- **Temperature** rescales logits: low = peaked (near-greedy), high = flatter. Low for extraction/classification, higher for ideation; it is not a "creativity dial for facts".
- **Top-p (nucleus)** samples from the smallest set whose cumulative probability ≥ p; **top-k** keeps the k most likely. Tune temperature *or* top-p, not both.
- **Max output tokens, stop sequences, penalties.** A truncated answer reports `finish_reason = length`; unhandled truncation is a common production incident (half a JSON object).
- **Seed:** best-effort reproducibility only.

### 9. Nondeterminism even at temperature 0

Temperature 0 is *not* deterministic in production serving. Thinking Machines Lab showed the main cause is that inference kernels are not **batch-invariant**: your request's numerics depend on what else is in the batch (server load), not merely "GPU floating-point randomness". Batch-invariant kernels can fix it at a performance cost, but you don't control the provider's kernels. **Engineering rule #1 of this course: never assert exact strings.** Assert schemas, properties, grader verdicts, and statistical pass rates over N runs (C5).

### 10. Why models hallucinate

Hallucinations are **structural**: next-token training and accuracy-only benchmarks reward guessing over "I don't know" (OpenAI, 2025). Types: *factual fabrication*, *unfaithfulness* to provided context (including lost-in-the-middle), and *tool-call hallucination* (invented tools or arguments). Mitigations are systemic: grounding/RAG with citations (C7), structured outputs and validation (C3), explicit permission and incentive to abstain, verification steps, and evals that *reward* abstention.

### 11. Token economics: price per token ≠ cost per task

Cost per task = Σ over calls of (input tokens × input price + cached input × cache price + (output + reasoning) tokens × output price). It depends on:

- **Prompt overhead resent every turn** (system prompt + tool schemas + history).
- **Reasoning tokens** (hidden, billed at output price).
- **Verbosity** — a newer model at the same token price can cost more per task (Gemini 3.8 Flash vs 3.7 Flash) because it uses more tokens; vendor "per-task" savings claims are estimates.
- **Language** (token inflation), **retries**, **tool loops** (each iteration resends context), **caching hit rate**, **Batch** discounts.

Illustrative list prices (research notes, Oct 2026; aggregator-sourced except Anthropic; verify against Azure pricing before teaching): GPT-6 Luna $0.10/$0.50; Claude Haiku 5.5 from $0.10/$0.50; GPT-6 Sol and Claude Sonnet 5.5 $2/$10; Claude Opus 5.5 $4/$20; GPT-6 Astra and Claude Fable 5.1 $10/$50; DeepSeek V4.1 Flash $0.30/$1.20.

### 12. The model landscape by capability class (Oct 2026)

Teach and design by **class**; names churn monthly.

| Class | Examples (Oct 2026) | On Microsoft Foundry? |
|---|---|---|
| Frontier reasoning | GPT-6 Astra, Claude Fable 5.1, Gemini 4 Argon | GPT-6 yes; Opus 5.5 confirmed; Fable unverified; Gemini no |
| Balanced workhorse | GPT-6/6.1 Sol, Claude Opus 5.5 / Sonnet 5.5, Grok 4.7 | GPT, Opus 5.5, Grok yes |
| Cheap/fast high volume | GPT-6 Luna, Claude Haiku 5.5, GPT-5.4-nano | GPT yes; Haiku unverified |
| Open-weight large | DeepSeek V4/V4.1, Kimi K3, Qwen3.8, Mistral Large 3, gpt-oss-120b | DeepSeek V4, Kimi K2.x, Mistral Large 3, gpt-oss yes |
| SLM / on-device | Phi family, Qwen3.8-27B, gpt-oss-20b, Ministral-3B | Via Foundry Local / catalog |
| Specialists | coding (GPT-5.x-codex), realtime voice (gpt-realtime-2.1), embeddings/rerank (text-embedding-3-*, Cohere v4), document/OCR (mistral-ocr-4-0, Cohere-parse-v5) | Yes |

Also: Microsoft Foundry is the most multi-vendor catalog; **tool calling and JSON output are not universal** (e.g., `Llama-3.3-70B-Instruct`, `Llama-4-Maverick`, `mistral-medium-3-5` listed without tool calling); benchmarks are saturating and mostly vendor-run — your own eval set (C5) is the only benchmark that matters; "open-weight" ≠ "open-source" ≠ "free for any use" (licences range from MIT/Apache-2.0 to custom).

### 13. When NOT to use an LLM

| Need | Prefer non-LLM when… | Prefer LLM when… |
|---|---|---|
| Tabular prediction (e.g., Trakia breakdown risk from maintenance history) | Almost always: gradient-boosted trees / ML.NET AutoML — cheaper, explainable | Narrating the model's output |
| Telematics anomaly detection / fuel forecasting | Numeric, streaming, seasonal (ML.NET SSA, rules) | Explaining anomalies, hypotheses |
| Fixed-layout extraction (delivery notes, invoices) | High volume, need per-field confidence/bounding boxes: Document Intelligence / Content Understanding | Variable layouts, reasoning over content |
| High-volume text classification | Fine-tuned small model or typed "decision model"; ms latency | Low volume, changing labels, zero-shot |
| Deterministic rules (EU driving-time limits) | Encode rules in code; they are law, not vibes | Explaining a violation in plain language |
| Batch speech transcription | Azure Speech | Conversational realtime agents |

Decide per task on **accuracy, cost, latency, explainability** evidence — not on fashion. The tachograph rule check is the canonical Trakia example: the LLM explains, code decides.

### Misconceptions to unlearn

"Tokens are words." "Temperature 0 is deterministic." "1M context means I can use 1M." "If it's in context the model uses it." "Fine-tuning teaches our latest facts." "The model executes tools" (it emits a structured request; *your code* executes — C3). "Cheaper per token = cheaper." "Benchmarks tell me which model is best for my app." "I can audit the chain of thought" (it may be hidden or encrypted). "MoE needs memory only for active params."

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| `Microsoft.ML.Tokenizers` (+ data packages, e.g. o200k encoding) | Local token counting | GA | Local counts are estimates for non-matching tokenizers; reconcile with API `usage` |
| `Microsoft.Extensions.AI` 10.x | Provider-agnostic calls (`IChatClient`) | GA | Full treatment in C2; used here via a provided harness |
| `OpenAI` .NET package → `/openai/v1/` | Raw access incl. logprobs where supported | GA | Logprob support varies by model — verify per deployment |
| Foundry deployments: fast, reasoning | Experiments | GA | Roles from `models.json` |
| Foundry Local | Local model comparisons | GA | Small models; CPU/GPU/NPU auto |
| ML.NET (+ AutoML) | Classical ML baseline | GA | "When not to use an LLM" lab |
| Polyglot Notebooks / `dotnet run` scripts | Plotting results | — | Or export CSV to Excel |
| nanoGPT / micrograd [Python] | Optional deep-dive | — | Side reading only; not required |

## Labs

### Lab 1 — Tokens in two languages (≈1.5h)

- **Goal:** Produce Trakia's own number: tokens per word and per character for Bulgarian vs English, and its monthly cost impact.
- **Start state:** `c1/lab1-start` (`src/FleetOps.Lab.Tokens`, corpus sample: 20 paired BG/EN paragraphs from the fleet policy handbook and driver code of conduct).
- **Steps:**
  1. Count locally:
     ```csharp
     using Microsoft.ML.Tokenizers;
     Tokenizer tok = TiktokenTokenizer.CreateForModel("gpt-4o"); // o200k proxy; verify encoding for your deployment
     foreach (var (id, bg, en) in pairs)
     {
         int bgT = tok.CountTokens(bg), enT = tok.CountTokens(en);
         rows.Add(new(id, bgT, enT, Words(bg), Words(en), (double)bgT / enT));
     }
     ```
  2. Reconcile: send each paragraph to `chat-fast` with a trivial instruction and record `usage.InputTokenCount`. Subtract the fixed overhead (send an empty-content message to measure it). Compute the error of the local estimate.
  3. Repeat for `chat-local` (different tokenizer) using its reported usage.
  4. Plate-number homoglyphs: tokenize "РВ 4521 КН" (Cyrillic) and "PB 4521 KH" (Latin); write a 10-line normalizer and a unit test.
  5. Cost projection: 600 drivers × 10 questions/day × 22 workdays; average question + answer sizes from the corpus; system prompt 1,200 tokens resent each call. Produce a table: EN-only vs BG-only, fast vs reasoning class, with and without prompt caching.
- **Break it:** Prepend the full 3,000-word driver code of conduct to every request "for context". Recompute monthly cost and measure TTFT.
- **Acceptance criteria:** `dotnet test --filter Lab=C1.Tokens` green (normalizer tests, reconciliation error < 5% for the matching tokenizer); `docs/c1/token-report.md` contains the BG/EN ratio with method, the reconciliation table and the cost projection.
- **Stretch:** Add Bulgarian Latin transliteration ("шльокавица") inputs — how do token counts and answer quality change?

### Lab 2 — Sampling and nondeterminism (≈2h)

- **Goal:** Observe output distributions and design tests that survive them.
- **Start state:** `c1/lab2-start` (`SamplingHarness` that runs a prompt N times and stores outputs as JSONL).
- **Steps:**
  1. Prompt: classify a Trakia incident note ("Шофьорът съобщава за силен шум от предната лява гума на АМ Тракия, км 142") into one of `{tyre, brakes, engine, cargo, accident, other}`; answer with the label only.
  2. Run 20× each at temperature 0, 0.7 and 1.2 on `chat-fast` (where temperature is supported). Record distinct outputs, label distribution and invalid-label rate.
  3. Run 20× at temperature 0 with a long free-text summary prompt. Count distinct outputs (string-exact) and semantically different outputs (compare extracted fields).
  4. Try the same on `chat-reasoning`; record which parameters are rejected or ignored.
  5. Force truncation with `MaxOutputTokens = 20` on a summary; detect `finish_reason = length` and handle it (retry with higher limit or return a typed "truncated" result).
  6. Optional (if the deployment returns logprobs): turn the classifier into a thresholded classifier — accept only if top-label probability ≥ 0.8, else route to a human.
- **Break it:** Write an xUnit test that asserts the exact summary string. Run it 10 times in CI. Then rewrite it to assert (a) the label ∈ allowed set, (b) the summary mentions the km marker and the tyre, (c) pass rate ≥ 9/10.
- **Acceptance criteria:** `docs/c1/sampling-report.md` with the three distributions and your explanation referencing batch invariance; the exact-string test is deleted; the property-based test passes in 3 consecutive CI runs; truncation handler has a unit test.
- **Stretch:** Plot answer diversity (distinct outputs) vs temperature for 5 prompts.

### Lab 3 — Reasoning effort and context budget (≈2h)

- **Goal:** Quantify accuracy vs latency vs cost across effort levels and context sizes.
- **Start state:** `c1/lab3-start` (12 driving-time questions with ground-truth answers computed by a deterministic C# rule engine from the EU driving-time summary; plus a "needle" document set).
- **Steps:**
  1. For each question, call `chat-reasoning` at effort low/medium/high (provider-specific option passed via the harness — verify the exact parameter name and its MEAI mapping for your deployment). Record correctness (compare to rule engine), latency, input/output/reasoning tokens, cost.
  2. Compare with `chat-fast` (no or minimal reasoning).
  3. Needle test: hide one fact ("Depot Varna's tyre supplier changed to Balkan Tyres on 3 Sept") at the start, middle and end of padded contexts of 2k, 20k and 100k tokens of policy text. Ask for it 5× per cell.
- **Break it:** Set `MaxOutputTokens` low on high effort. Observe empty or truncated answers because reasoning consumed the budget.
- **Acceptance criteria:** `docs/c1/effort-report.md` with an accuracy/latency/cost table per effort level and a one-paragraph recommended default *for this task*; needle grid (position × size) with recall; an ADR (`docs/adr/0001-default-reasoning-effort.md`) that cites your numbers. This is your first ADR: use the course template and checklist in `docs/adr/README.md` — context, **≥ 3 options considered (incl. "do nothing / status quo" where meaningful)**, decision, consequences, evidence links and a review date (the ADR linter enforces this from here on; here the options are effort levels plus the status-quo default).
- **Stretch:** Replace the LLM for the driving-time questions with the rule engine plus an LLM that only explains the engine's output. Compare accuracy and cost.

### Lab 4 — Cost calculator and local vs cloud (≈1.5h)

- **Goal:** A reusable cost-per-task calculator and an evidence-based local-vs-cloud comparison.
- **Start state:** `c1/lab4-start` (`pricing.json` with date-stamped list prices per role).
- **Steps:**
  1. Implement `CostCalculator.ForCall(UsageDetails usage, ModelPrice price)` including cached-input and reasoning tokens (reasoning billed as output); unit-test it with hand-computed cases.
  2. Run the incident-classification task (Lab 2) over 40 labeled incident notes on `chat-fast`, `chat-reasoning` and `chat-local`. Record accuracy, p50/p95 latency, cost per 1,000 tasks (local = €0 marginal; note hardware and energy as a footnote).
  3. Train an **ML.NET** text classifier on 400 labeled historical incident notes (provided) and evaluate on the same 40. Build a confusion matrix for each approach.
- **Break it:** Swap `chat-fast` for a model in the catalog listed *without* tool calling / JSON support and request JSON-mode output — record the failure.
- **Acceptance criteria:** Calculator tests green; `docs/c1/model-bakeoff.md` with a 4-row table (fast, reasoning, local, ML.NET) × (accuracy, p95 latency, cost/1k, explainability) and a recommendation; `pricing.json` carries a "retrieved on" date.
- **Stretch:** Model a cascade: ML.NET first, LLM only when classifier confidence < threshold; compute blended cost and accuracy.

## Kata

**"Predict, run, explain"** (25–30 min, repeat with a new myth each time). Pick one misconception card (tokens = words; T=0 deterministic; 1M context usable; in-context = used; cheaper per token = cheaper; fine-tune = new facts; model executes tools). (1) Write your prediction and a falsifiable test in 3 sentences. (2) Run it with the harness on Trakia data (≤10 min). (3) Write a 5-sentence explanation citing the mechanism. Variation: switch model role or language (BG/EN) and predict whether the result changes.

## Product increment — Fleet Ops Copilot

No new user feature. The product gains its **economic and behavioral baseline**: the token report (BG/EN ratio), the effort ADR, the cost calculator and `pricing.json` (consumed by C2's cost logging middleware), and the incident-classification labeled set that seeds the golden dataset in C5.

## Factory increment — your agentic SDLC

The `SamplingHarness` (run N times, store JSONL, compute pass rates) and the cost calculator become shared factory tools in `tools/`, used by eval tests from C5 on. Rule recorded in the repo's conventions for later agents: *no exact-string assertions on model output*.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Mechanistic explanation | Repeats definitions | Explains tokens, sampling, context correctly | Predicts outcomes of experiments before running them | Explains surprises (e.g., reasoning budget truncation, batch variance) and their engineering consequences |
| Measurement rigor | Single runs, anecdotes | Repeated runs, basic tables | N runs, distributions, reconciled with provider usage | Confidence intervals, controlled variables, documented method others can rerun |
| Cost reasoning | Quotes per-token price | Computes per-call cost | Cost per task incl. overhead, reasoning, caching | Cost model with sensitivity analysis (language mix, effort, cache hit rate) feeding an ADR |
| Tool selection | LLM for everything | Knows alternatives exist | Uses evidence to pick LLM vs ML.NET vs rules | Designs hybrids/cascades and justifies on accuracy/cost/latency/explainability |

**Auto-checked:** lab test filters (`Lab=C1.*`), presence and structure of the four reports and ADR-0001 (required headings, numeric tables), no exact-string assertions on model output (analyzer rule in `tests/`).

## Common pitfalls

- Counting tokens with a tokenizer that doesn't match the deployment and treating it as truth.
- Forgetting the system prompt and tool schemas in cost estimates — they are resent every call.
- Comparing effort levels on a lookup task where reasoning can't help, and concluding "reasoning is useless".
- Setting both temperature and top-p, or setting them on a reasoning endpoint that ignores them, then drawing conclusions.
- Treating a single run as a measurement.
- Quoting aggregator prices as facts; always date-stamp and cite.


## References

- Vaswani et al., Attention Is All You Need: https://arxiv.org/abs/1706.03762 ; Illustrated Transformer: https://jalammar.github.io/illustrated-transformer/
- Sennrich et al., BPE: https://arxiv.org/abs/1508.07909 ; RoPE: https://arxiv.org/abs/2104.09864 ; GQA: https://arxiv.org/abs/2305.13245 ; FlashAttention: https://arxiv.org/abs/2205.14135 ; PagedAttention: https://arxiv.org/abs/2309.06180
- Liu et al., Lost in the Middle: https://arxiv.org/abs/2307.03172 ; Chroma, Context Rot: https://trychroma.com/research/context-rot
- Switch Transformers (MoE): https://arxiv.org/abs/2101.03961
- InstructGPT (RLHF): https://arxiv.org/abs/2203.02155 ; Constitutional AI: https://arxiv.org/abs/2212.08073 ; DPO: https://arxiv.org/abs/2305.18290 ; DeepSeek-R1 (RLVR): https://arxiv.org/abs/2501.12948 ; Test-time compute: https://arxiv.org/abs/2408.03314
- Holtzman et al., nucleus sampling: https://arxiv.org/abs/1904.09751
- Thinking Machines Lab, Defeating Nondeterminism in LLM Inference: https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
- OpenAI, Why language models hallucinate: https://openai.com/index/why-language-models-hallucinate/
- Models sold directly by Azure (context windows, tool-calling support, reasoning_effort): https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure
- Claude models overview / Opus 5.5 pricing and caching: https://platform.claude.com/docs/en/models/overview ; https://platform.claude.com/docs/en/models/opus-5-5/overview
- Foundry fine-tuning overview (SFT/DPO/RFT): https://learn.microsoft.com/en-us/azure/foundry/fine-tuning/overview
- Aggregators (orientation only, verify): FutureAGI https://futureagi.com/blog/best-llms-september-2026/ ; Digital Applied https://www.digitalapplied.com/blog/ai-model-releases-september-2026-tracker
- ML.NET: https://dotnet.microsoft.com/apps/ai/ml-dotnet ; nanoGPT: https://github.com/karpathy/nanoGPT ; CS336: https://cs336.stanford.edu/
