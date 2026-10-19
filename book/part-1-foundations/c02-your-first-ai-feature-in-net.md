# C2 — Your first AI feature in .NET

> **Level:** 1 — Foundations (Beginner) · **Duration:** 12h (theory 25% / labs 75%) · **Prerequisites:** C0 (env, Foundry project, model roles), C1 (tokens, sampling, cost per task) · **Volatility:** Med (MEAI 10.x is GA and stable; OpenAI/Foundry SDK surface and Responses adapters move quarterly)

## Why this matters

Trakia's first copilot prototype was written in an afternoon: an `HttpClient` posting JSON to a model endpoint, a hard-coded model name, an API key in `appsettings.json`, string concatenation for the conversation, and no logging. It demoed well. Then the model was deprecated (60-day notice, `410 Gone` after retirement), the security review rejected the key, the first load test produced a wall of `429 Too Many Requests` that the code treated as fatal, and nobody could answer "what did that conversation cost?" because token usage was never captured.

The fix is not "more code" but the right abstraction. **Microsoft.Extensions.AI (MEAI)** gives .NET a provider-agnostic `IChatClient` with a composable **middleware pipeline** — the same shape ASP.NET Core developers know from HTTP middleware. Logging, OpenTelemetry, caching, tool invocation, cost accounting and guardrails become decorators you add in DI, and the provider (Foundry cloud model, Foundry Local, any OpenAI-compatible endpoint) becomes configuration. Microsoft Agent Framework (C9) and the MCP SDK (C8) are built on these same abstractions, so everything you learn here carries forward.

Experts ship the *boring* parts on day one: keyless auth, retries that honor `Retry-After`, cancellation, streaming with back-pressure, usage capture per call, and traces that show every model call in the Aspire dashboard. That is what makes the later modules — evals, cost dashboards, model migrations — possible at all.

## Learning outcomes

By the end of C2 you can:

1. **Implement** a chat feature on `IChatClient` with conversation state, `ChatOptions` and streaming (`GetStreamingResponseAsync`) in a console app and an ASP.NET Core minimal API.
2. **Connect** to Foundry via the OpenAI v1 endpoint and via the Foundry project endpoint (Responses API), and **justify** which path to use.
3. **Compose** a middleware pipeline with `ChatClientBuilder`: logging, OpenTelemetry, distributed caching, function invocation, plus a custom cost-logging/budget middleware.
4. **Register** chat clients in DI (including keyed clients per model role) and orchestrate the app with Aspire, seeing GenAI spans in the dashboard.
5. **Swap** providers (Foundry ↔ Foundry Local ↔ OpenAI-compatible local runner) by configuration only, and **detect** capability differences between them.
6. **Configure** keyless authentication (Entra ID locally, managed identity in Azure) and keep secrets out of source.
7. **Handle** 429s, timeouts and transient faults with bounded retries that honor `Retry-After`, plus cancellation and concurrency limits.
8. **Log** token usage and cost per call and per conversation using the C1 cost calculator.

## Concepts

### The .NET AI stack, layered

Microsoft's .NET AI decision guide: **MEAI** (`IChatClient`, `IEmbeddingGenerator`, `ChatClientBuilder`) for AI behavior; **MEVD/MEDI** for your own data (C6–C7); **MCP SDK** to share capabilities (C8); **MAF** or the **Copilot SDK** for agents (C9); **Foundry / Foundry Local / Aspire** for hosting. `IChatClient` and `IEmbeddingGenerator<,>` were extracted from Semantic Kernel into MEAI; `Microsoft.Extensions.AI.Abstractions` is at 10.5.0 (version-aligned with .NET 10).

### `IChatClient` in one screen

```csharp
public interface IChatClient : IDisposable
{
    Task<ChatResponse> GetResponseAsync(IEnumerable<ChatMessage> messages,
        ChatOptions? options = null, CancellationToken cancellationToken = default);
    IAsyncEnumerable<ChatResponseUpdate> GetStreamingResponseAsync(IEnumerable<ChatMessage> messages,
        ChatOptions? options = null, CancellationToken cancellationToken = default);
    object? GetService(Type serviceType, object? serviceKey = null);
}
```

- **Messages** carry a role (`System`, `User`, `Assistant`, `Tool`) and a list of `AIContent` items: `TextContent`, `DataContent` (images/audio bytes), `UriContent`, `FunctionCallContent`/`FunctionResultContent` (C3), and approval-request content for human-in-the-loop (C9).
- **`ChatOptions`**: `ModelId`, `Temperature`, `TopP`, `MaxOutputTokens`, `StopSequences`, `Seed`, `ResponseFormat`, `Tools`, `ToolMode`, plus an escape hatch for provider-specific options (e.g. reasoning effort) via `AdditionalProperties` or a raw-representation factory — verify the current mechanism for effort on your provider adapter before teaching.
- **`ChatResponse`**: `Messages`, `Text`, `FinishReason`, `ModelId`, **`Usage`** (`InputTokenCount`, `OutputTokenCount`, `TotalTokenCount`, plus provider extras in `AdditionalCounts`, where reasoning/cached tokens may appear — inspect per provider), `RawRepresentation` (the provider's object, for debugging).
- **Streaming** yields `ChatResponseUpdate`s; `updates.ToChatResponse()` reassembles a full response (including usage, if the provider sends it at the end).
- **Statelessness:** with Chat Completions you send the whole history every call (and pay for it — C1). The Responses API can hold conversation state server-side; MEAI surfaces this via a conversation/response ID on options/response (verify property names in your MEAI version). Server-side state cuts payload size but couples you to the provider and its retention policy — a GDPR question (C18).

### Two endpoint paths to Foundry

| | OpenAI v1 endpoint | Foundry project endpoint |
|---|---|---|
| URL | `https://<res>.openai.azure.com/openai/v1/` | `https://<res>.services.ai.azure.com/api/projects/<project>` |
| .NET package | `OpenAI` + `Microsoft.Extensions.AI.OpenAI` adapter | `Azure.AI.Projects` 2.0 / `Azure.AI.Extensions.OpenAI` 2.0 (GA) |
| Auth | `BearerTokenPolicy(cred, "https://ai.azure.com/.default")` (token scope per the SDK overview at release time — some docs still use `https://cognitiveservices.azure.com/.default`; verify against current documentation) | `DefaultAzureCredential` |
| Use when | Plain model calls; maximum portability (same code hits any OpenAI-compatible server incl. Foundry Local) | You need project-scoped features: agents, connections, evaluations, tracing in the Foundry Control Plane |

Both expose the **Responses API** (the successor to the Assistants API, retired 26 Aug 2026). Some OpenAI-package APIs require `#pragma warning disable OPENAI001`. Never mix the preview `Azure.AI.Projects.OpenAI` with GA `Azure.AI.Extensions.OpenAI`.

### The middleware pipeline

`ChatClientBuilder` wraps an inner client in delegating clients; order matters (outermost first in the builder chain):

```csharp
IChatClient client = new ChatClientBuilder(innerClient)
    .UseLogging(loggerFactory)                 // outermost: sees every request incl. cache hits
    .UseDistributedCache(cache)                // identical requests served from cache (non-personal prompts only)
    .UseFunctionInvocation()                   // runs tool loops (C3); everything below sees each iteration
    .UseOpenTelemetry(sourceName: "FleetOps.AI", configure: o => o.EnableSensitiveData = false) // one span per model call
    .Use(inner => new CostTrackingChatClient(inner, pricing, costSink))  // custom; closest to the provider
    .Build(services);
```

Design rules (the first `Use…` call is the *outermost* wrapper; each wrapper only sees calls that pass through it):

- **Logging outside the cache** if you want to observe cache hits; **cost tracking inside the cache** so cached responses cost €0.
- **Function invocation outside (above) per-call telemetry and cost tracking**, so each tool-loop iteration is individually traced and costed. If you place `UseFunctionInvocation()` innermost, the outer middleware sees one aggregated call per user request ("tool loops show only one span" — kata below). Caching *outside* function invocation caches the final answer of a tool loop; never do that for answers built from live data (vehicle status).
- **Sensitive data** (prompt/response content) is off by default in OTel; content capture in EU production must be justified in the DPIA. Turn it on in dev only.
- **Custom middleware** subclasses `DelegatingChatClient` and overrides both the non-streaming and streaming methods — forgetting the streaming override is the most common bug.
- Caching LLM responses is safe for deterministic, non-personal prompts (evals, static lookups). **Never** cache user- or time-specific answers across users (leakage).

### Observability with Aspire

Aspire's AppHost starts the API, SQL Server container and any local resources; ServiceDefaults wire OpenTelemetry. Register your MEAI source name with the tracer/meter providers, and model calls appear as GenAI spans (the dashboard marks LLM calls with a "sparkles" indicator). Span/attribute names follow the **OpenTelemetry GenAI semantic conventions**, which are still entirely at "Development" stability and moved to `open-telemetry/semantic-conventions-genai` in v1.42.0 — attribute names can change (`gen_ai.system` → `gen_ai.provider.name` already did). Pin package versions and don't build dashboards on attribute names you haven't verified (C15 goes deep).

### Provider swap and capability drift

Foundry Local, Ollama, LLamaSharp and ONNX Runtime GenAI all plug into `IChatClient` (Foundry Local and Ollama via OpenAI-compatible endpoints or dedicated adapters). The *code* swaps by config; the *behavior* does not: small local models may lack tool calling, honor JSON schemas less reliably, ignore some options, report usage differently and have far smaller context windows. A provider swap without an eval run (C5) is an untested deployment. Use `GetService<ChatClientMetadata>()` to log provider and model identity on every call.

### Keyless auth and secrets

- Local: `az login` + `DefaultAzureCredential` (or `AzureCliCredential` for faster startup and fewer surprises).
- Azure: **managed identity** of the hosting resource (Container Apps/App Service, C17) with a data-plane role on the Foundry resource.
- CI: OIDC federated credential (C5).
- Local OpenAI-compatible runners: dummy key from config; never a real key.
- Config hierarchy: `appsettings.json` (non-secret), environment/Aspire parameters, user-secrets in dev; Key Vault references only for truly unavoidable secrets.

### Rate limits, 429s and retries

- Deployments have **TPM** (tokens per minute) and request-rate limits. Exceeding them returns **429** with a `Retry-After` header (Azure also returns remaining-quota headers — verify names before teaching).
- The `OpenAI`/Azure SDK client pipeline retries transient failures (429, 5xx, timeouts) with exponential backoff by default; configure `OpenAIClientOptions.RetryPolicy` and `NetworkTimeout` explicitly rather than trusting defaults (verify default retry count for your package version).
- **Do not stack retry layers** (SDK retries × your Polly retries × gateway retries = retry storms).
- Retries are not free: a retried long prompt is re-billed for input; a streaming response that fails mid-way can't be resumed transparently.
- Concurrency control: a `SemaphoreSlim`/`System.Threading.RateLimiting` limiter in front of the client keeps you under TPM rather than reacting to 429s.
- Long-term fixes are architectural: APIM AI gateway with token limits and priority backends (C15, C17), Batch for offline work, smaller models for bulk.

### Misconceptions to unlearn

- "The SDK is the abstraction." The SDK is a provider; `IChatClient` is the abstraction your code depends on.
- "Streaming makes it faster." It improves *perceived* latency (TTFT); total time and cost are unchanged.
- "A provider swap is a config change." It's a config change *plus an eval run*.
- "Retries fix 429s." Retries smooth bursts; sustained 429s mean capacity planning.

## Tools & versions (as of Oct 2026)

| Tool / package | Purpose | Status | Notes |
|---|---|---|---|
| `Microsoft.Extensions.AI` / `.Abstractions` 10.5.0 | `IChatClient`, builder, middleware | GA | Pin centrally |
| `Microsoft.Extensions.AI.OpenAI` | Adapter: OpenAI chat & responses clients → `IChatClient` | Verify GA/preview of the Responses adapter for your version | `AsIChatClient()` extension |
| `OpenAI` (.NET) | Client for `/openai/v1/` and local OpenAI-compatible servers | GA | `#pragma warning disable OPENAI001` for some APIs |
| `Azure.AI.Projects`, `Azure.AI.Extensions.OpenAI` 2.0.0 | Foundry project endpoint | GA | Don't mix with preview `Azure.AI.Projects.OpenAI` |
| `Azure.Identity` | Entra ID / managed identity | GA | |
| Aspire 13.6 (AppHost, ServiceDefaults, dashboard) | Orchestration, OTel | GA | Foundry/Azure OpenAI hosting integrations: verify package names |
| `Microsoft.Extensions.Caching.*` (memory/Redis) | `UseDistributedCache` backing store | GA | |
| Foundry Local / `Microsoft.AI.Foundry.Local` | Local provider | GA | |
| `OllamaSharp` (optional) | Ollama `IChatClient` | Community | Alternative local runner |
| GitHub Copilot / Claude Code | First AI-assistant use (factory) | GA | Explain/scaffold only in C2; full workflow in C4 |

## Labs

### Lab 1 — "Ask Fleet Ops" console on `IChatClient` (≈2.5h)

- **Goal:** A streaming console chat over `chat-fast` with conversation history, usage display and both endpoint paths.
- **Start state:** `c2/lab1-start` (`src/FleetOps.Cli`, `src/FleetOps.Core/AI/ChatClientFactory.cs` stub, `models.json`).
- **Steps:**
  1. Implement the factory for the v1 endpoint:
     ```csharp
     #pragma warning disable OPENAI001
     public static IChatClient CreateFoundryV1(ModelRole role, TokenCredential cred)
     {
         var openAi = new OpenAIClient(
             new BearerTokenPolicy(cred, "https://ai.azure.com/.default"),
             new OpenAIClientOptions
             {
                 Endpoint = new Uri(role.Endpoint),               // .../openai/v1/
                 RetryPolicy = new ClientRetryPolicy(maxRetries: 3),
                 NetworkTimeout = TimeSpan.FromSeconds(100),
             });
         return role.Api switch
         {
             "chat"      => openAi.GetChatClient(role.Deployment).AsIChatClient(),
             "responses" => openAi.GetOpenAIResponseClient(role.Deployment).AsIChatClient(), // verify method name in your OpenAI SDK version
             _ => throw new NotSupportedException(role.Api)
         };
     }
     ```
  2. Implement the chat loop with a Trakia system prompt (loaded from `prompts/ask-fleet-ops.system.md`, introduced properly in C3):
     ```csharp
     List<ChatMessage> history = [new(ChatRole.System, systemPrompt)];
     while (Console.ReadLine() is { Length: > 0 } input)
     {
         history.Add(new(ChatRole.User, input));
         List<ChatResponseUpdate> updates = [];
         await foreach (var u in chat.GetStreamingResponseAsync(history, options, ct))
         {
             Console.Write(u.Text);
             updates.Add(u);
         }
         var response = updates.ToChatResponse();
         history.AddMessages(response);
         Console.WriteLine($"\n[{response.ModelId} in={response.Usage?.InputTokenCount} out={response.Usage?.OutputTokenCount} finish={response.FinishReason}]");
     }
     ```
  3. Add a second path via the Foundry project endpoint (`AIProjectClient` → project OpenAI client → responses client for a model → `IChatClient`; follow the SDK overview's C# path and verify adapter availability). Switch between paths with `--path v1|project`.
  4. Measure TTFT and total latency for streaming vs non-streaming over 10 questions; record in `docs/c2/streaming.md`.
- **Break it:** (a) Remove the history (send only the latest message) and ask a follow-up ("And the Varna depot?") — observe the model losing context. (b) Let the history grow for 30 turns and watch input tokens per call climb (C1 cost model). (c) Press Ctrl+C mid-stream — does the request cancel or keep billing? Wire `CancellationToken` through and verify the stream stops.
- **Acceptance criteria:** `dotnet test --filter Lab=C2.L1` green (factory selects the correct client per `models.json`; history reducer test; cancellation test with a fake client); console works on both paths; `docs/c2/streaming.md` contains TTFT numbers.
- **Stretch:** Implement a simple history reducer (keep system + last N turns) and measure the token saving; note the quality risk (C13 does this properly).

### Lab 2 — The middleware pipeline: logging, OTel, cache, cost (≈2.5h)

- **Goal:** A production-shaped pipeline with a custom cost-tracking and budget-guard middleware, visible in the Aspire dashboard.
- **Start state:** `c2/lab2-start` (AppHost, ServiceDefaults, `CostCalculator` from C1, `pricing.json`).
- **Steps:**
  1. Write `CostTrackingChatClient : DelegatingChatClient`:
     ```csharp
     public sealed class CostTrackingChatClient(IChatClient inner, IPricingTable pricing, ICostSink sink)
         : DelegatingChatClient(inner)
     {
         public override async Task<ChatResponse> GetResponseAsync(
             IEnumerable<ChatMessage> messages, ChatOptions? options = null, CancellationToken ct = default)
         {
             var response = await base.GetResponseAsync(messages, options, ct);
             await sink.RecordAsync(Cost.From(response, pricing, Activity.Current?.TraceId), ct);
             return response;
         }

         public override async IAsyncEnumerable<ChatResponseUpdate> GetStreamingResponseAsync(
             IEnumerable<ChatMessage> messages, ChatOptions? options = null,
             [EnumeratorCancellation] CancellationToken ct = default)
         {
             List<ChatResponseUpdate> seen = [];
             await foreach (var u in base.GetStreamingResponseAsync(messages, options, ct))
             {
                 seen.Add(u);
                 yield return u;
             }
             await sink.RecordAsync(Cost.From(seen.ToChatResponse(), pricing, Activity.Current?.TraceId), ct);
         }
     }
     ```
     `Cost.From` uses C1's calculator; record conversation ID, role, model, tokens, € and trace ID. Also emit a metric `fleetops.ai.cost` (histogram, EUR) with `model` and `feature` tags.
  2. Add a `BudgetGuardChatClient` that rejects calls when a per-conversation budget (e.g. €0.05) is exceeded, returning a typed error the UI can show.
  3. Compose the pipeline in DI (Lab 3 moves it to the API); register `"FleetOps.AI"` as a tracing/metrics source in ServiceDefaults.
  4. Run via the AppHost; open the Aspire dashboard; find the GenAI spans, token attributes and your cost metric.
  5. Enable `UseDistributedCache` with an in-memory distributed cache; ask the same question twice; confirm the second call costs €0 and is fast — then reason about where caching is *wrong* for Fleet Ops (per-driver questions).
- **Break it:** Move `CostTrackingChatClient` *outside* the cache and observe cached calls being billed in your ledger. Remove the streaming override and observe streaming calls missing from the ledger.
- **Acceptance criteria:** Unit tests with a fake inner client verify: cost recorded once per call (streaming and non-streaming), cache hits cost 0, budget guard trips at the threshold; Aspire dashboard screenshot in `docs/c2/` showing a GenAI span with token usage; the pipeline order is documented in a code comment explaining *why*.
- **Stretch:** Write a `PiiRedactingChatClient` that masks Bulgarian mobile numbers (`+359 8x…`) and EGN-like 10-digit sequences in outgoing user messages; unit-test with BG examples.

### Lab 3 — Minimal API, DI, Aspire and the provider swap (≈2.5h)

- **Goal:** `POST /ask` with server-sent-event streaming, keyed clients per model role, and Foundry ↔ Foundry Local ↔ OpenAI-compatible swap by configuration.
- **Start state:** `c2/lab3-start` (`src/FleetOps.Api`).
- **Steps:**
  1. Register keyed clients:
     ```csharp
     foreach (var (roleName, role) in models.Roles)
     {
         builder.Services.AddKeyedChatClient(roleName, sp => ChatClientFactory.Create(role, sp))
             .UseLogging()
             .UseFunctionInvocation()
             .UseOpenTelemetry(sourceName: "FleetOps.AI")
             .Use((inner, sp) => new CostTrackingChatClient(inner, sp.GetRequiredService<IPricingTable>(), sp.GetRequiredService<ICostSink>()));
     }
     ```
     (Verify the exact `Use` overload signatures in your MEAI version.)
  2. Endpoint with streaming:
     ```csharp
     app.MapPost("/ask", (AskRequest req, [FromKeyedServices("chat-fast")] IChatClient chat,
                          IConversationStore store, CancellationToken ct) =>
     {
         async IAsyncEnumerable<string> Stream()
         {
             var history = await store.LoadAsync(req.ConversationId, ct);
             history.Add(new(ChatRole.User, req.Question));
             await foreach (var u in chat.GetStreamingResponseAsync(history, cancellationToken: ct))
                 if (!string.IsNullOrEmpty(u.Text)) yield return u.Text;
         }
         return TypedResults.ServerSentEvents(Stream()); // .NET 10 SSE result; verify overload
     });
     ```
     Persist the assistant reply after the stream completes (think about partial replies on cancel).
  3. In the AppHost, add a parameter `ModelProvider` (`foundry` | `foundry-local` | `openai-compatible`) that selects the role mapping. Start Foundry Local (or Ollama) outside Aspire and point `chat-local` at it.
  4. Run the same 15 smoke questions (BG + EN, from `evals/smoke.jsonl`) against each provider. Record answer, latency, tokens, cost and *capability failures* (e.g. unsupported option errors).
  5. Add `GET /health/ai` that calls each configured role with a 1-token prompt and reports provider metadata.
- **Break it:** Configure `chat-fast` to a model name that doesn't exist on Foundry Local; set `Temperature` on a reasoning deployment that rejects it; send a 40k-token history to a local model with a small context window. Make each failure surface as a clear problem-details response, not a 500 with a stack trace.
- **Acceptance criteria:** Integration tests (WebApplicationFactory + fake keyed clients) green; `curl -N` shows SSE streaming; switching `ModelProvider` requires zero code changes (CI job runs the smoke suite against a fake OpenAI-compatible server to prove it); `docs/c2/provider-swap.md` with the comparison table and a recommendation for which roles may run locally.
- **Stretch:** Add a minimal Blazor or static HTML page consuming the SSE stream.

### Lab 4 — Resilience: 429s, timeouts, concurrency (≈1.5h)

- **Goal:** Behave well under rate limiting and transient faults without retry storms.
- **Start state:** `c2/lab4-start` (includes `FaultInjectionHandler` that returns 429 with `Retry-After`, 503s and slow responses on a schedule).
- **Steps:**
  1. Insert the fault handler into the OpenAI client's transport (custom `HttpClient` via `HttpClientPipelineTransport`, or a pipeline policy — verify the cleanest hook for your SDK version).
  2. Fire 200 concurrent `/ask` requests with a small load script (`k6` or a C# `Parallel.ForEachAsync`). Observe default SDK retry behavior, total attempts, and p95 latency.
  3. Configure: SDK retries = 3 with exponential backoff honoring `Retry-After`; per-attempt timeout; overall request timeout; a `ConcurrencyLimiter` (e.g. 8 in-flight model calls per instance) as middleware; a fallback to `chat-local` *only* for a non-critical feature (summaries), never silently for everything.
  4. Emit metrics: attempts per request, 429 count, limiter queue length.
- **Break it:** Add a Polly retry (5 attempts) on top of SDK retries and a client-side retry in the load script. Count total upstream attempts per user request (expect multiplication). Remove the extra layers and document the single owner of retries.
- **Acceptance criteria:** Under the fault schedule, ≥ 95% of requests succeed, upstream attempts per request ≤ 4, no request exceeds the overall timeout; tests verify `Retry-After` is honored (fake clock); `docs/adr/0002-retry-ownership.md` states who retries, where, and why.
- **Stretch:** Model the capacity you'd need (TPM) for 600 drivers at peak (07:00–08:00 dispatch window) using C1's token report; compare with your deployment's quota.

## Kata

**"Pipeline surgery"** (25–35 min, repeat 3×). Given a pipeline and a bug report ("cached answers show up in the cost ledger", "streaming calls have no traces", "tool loops show only one span", "PII appears in logs"), reorder or add middleware to fix it, and write the fake-client unit test that proves the fix. Variations: a new custom middleware (rate limiter, PII redactor, model-identity tagger); a provider that emits usage only at stream end; a provider with no usage at all.

## Product increment — Fleet Ops Copilot

**"Ask Fleet Ops" v0**: console and minimal API chat over a model; streaming via SSE; conversation history; keyed clients per model role; provider swap (Foundry cloud ↔ Foundry Local ↔ OpenAI-compatible) by configuration; usage and cost recorded per call and conversation; traces in the Aspire dashboard; resilient to 429s. It has no access to Trakia data yet — it must say so when asked about specific trucks or policies (C3 adds the first tool; C7 adds documents).

## Factory increment — your agentic SDLC

First deliberate use of an AI coding assistant (Copilot agent mode in VS/VS Code, or Claude Code): use it to (1) *explain* the MEAI pipeline code and the order of middleware, (2) *scaffold* the integration tests for Lab 3, and (3) *review* your `CostTrackingChatClient` for the streaming bug. Rules for C2: you must read and be able to explain every line it produces; log each session in `docs/factory/ai-assist-log.md` (task, prompt, what you accepted/rejected, why). This log is the baseline against which C4 measures your agent workflow.

## Assessment

| Criterion | Novice | Competent | Proficient | Expert |
|---|---|---|---|---|
| Abstraction & DI | Calls SDK directly in endpoints | Uses `IChatClient` via DI | Keyed clients per role; zero-code provider swap | Capability-aware swap with metadata logging and documented per-role provider policy |
| Middleware design | None | Logging/OTel added | Custom middleware with correct streaming override and ordering | Ordering justified (cache vs cost vs telemetry), fully unit-tested with fake clients |
| Resilience | 429 crashes | SDK default retries | Single retry owner, timeouts, cancellation, concurrency limit | Retry budget + capacity model + graceful degradation policy in ADR |
| Security | Keys in config | user-secrets | Entra ID, no secrets in repo | Managed-identity-ready config, PII redaction middleware, content capture off by default |
| Cost visibility | None | Prints tokens | Per-call and per-conversation cost ledger + metric | Budget guard, cache economics explained, cost visible in dashboard |

**Auto-checked:** `Lab=C2.*` tests; CI smoke suite against a fake OpenAI-compatible server; secret scan; analyzer rule forbidding `new OpenAIClient(` outside `ChatClientFactory`; presence of ADR-0002.

## Common pitfalls

- Implementing a `DelegatingChatClient` without overriding the streaming method — half your traffic bypasses it.
- Reassembling streamed text but losing `Usage` (some providers send usage only in the final update; some only if requested).
- Persisting partial assistant messages on cancellation, corrupting history.
- Caching per-user answers globally.
- Building a "factory" that leaks provider types into endpoints, making the swap a refactor.
- Stacking retries in SDK, Polly, gateway and client.
- Turning on `EnableSensitiveData` and shipping prompts with driver names into App Insights.
- Following a sample that uses the Assistants API or dated `api-version` query strings.


## References

- .NET AI ecosystem decision guide: https://learn.microsoft.com/en-us/dotnet/ai/dotnet-ai-ecosystem
- .NET AI essentials (MEAI building blocks, `UseOpenTelemetry`, Aspire sparkles): https://devblogs.microsoft.com/dotnet/dotnet-ai-essentials-the-core-building-blocks-explained/
- Microsoft.Extensions.AI docs: https://learn.microsoft.com/en-us/dotnet/ai/microsoft-extensions-ai
- `Microsoft.Extensions.AI.Abstractions` on NuGet: https://www-1.nuget.org/packages/Microsoft.Extensions.AI.Abstractions
- Foundry SDK overview (endpoints, `BearerTokenPolicy`, OPENAI001, package warning): https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview
- What is Microsoft Foundry: https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-azure-ai-foundry
- Foundry Local GA: https://devblogs.microsoft.com/foundry/foundry-local-ga/
- Local LLMs in C# (Foundry Local, LLamaSharp, ONNX Runtime GenAI, Ollama via `IChatClient`; practitioner blog): https://www.managed-code.com/blog-post/running-local-llms-csharp-llamasharp-vs-onnx-vs-foundry-local
- Aspire blog: https://devblogs.microsoft.com/aspire/
- OTel GenAI semconv status (Development; secondary): https://dev.to/azena-ai/opentelemetrys-genai-semantic-conventions-are-not-stable-yet-heres-what-actually-shipped-in-2026-3mke
- Model retirements (410 Gone, notice periods): https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements
