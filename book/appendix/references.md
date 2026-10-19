# Further reading

The key external references cited in the module *References* sections, deduplicated and grouped by theme. Module codes in brackets show where each source is used. Vendor blogs and product pages describe the state of things around October 2026; statuses, prices and names change, so verify against current documentation before relying on them. Secondary and aggregator sources are marked as such.

## How models work

- [Vaswani et al., Attention Is All You Need](https://arxiv.org/abs/1706.03762) (C1)
- [Liu et al., Lost in the Middle](https://arxiv.org/abs/2307.03172) (C1, C3, C13)
- [Chroma, Context Rot](https://trychroma.com/research/context-rot) (C1, C7, C13, A3)
- [Fedus et al., Switch Transformers (mixture-of-experts)](https://arxiv.org/abs/2101.03961) (C1, D1)
- [Ouyang et al., InstructGPT (RLHF)](https://arxiv.org/abs/2203.02155) (C1)
- [Rafailov et al., Direct Preference Optimization](https://arxiv.org/abs/2305.18290) (C1, D1)
- [DeepSeek-R1: reinforcement learning with verifiable rewards](https://arxiv.org/abs/2501.12948) (C1, D1)
- [Thinking Machines Lab, Defeating Nondeterminism in LLM Inference](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/) (C1, C5, D7)
- [OpenAI, Why language models hallucinate](https://openai.com/index/why-language-models-hallucinate/) (C1, C5)
- [Chip Huyen, *AI Engineering*](https://github.com/chiphuyen/aie-book) (C5, D1)

## The .NET AI stack and Microsoft Foundry

- [.NET AI ecosystem decision guide](https://learn.microsoft.com/en-us/dotnet/ai/dotnet-ai-ecosystem) (C0, C2, C6, D6)
- [Microsoft.Extensions.AI documentation](https://learn.microsoft.com/en-us/dotnet/ai/microsoft-extensions-ai) (C2, C3)
- [.NET AI essentials: the core building blocks explained](https://devblogs.microsoft.com/dotnet/dotnet-ai-essentials-the-core-building-blocks-explained/) (C2, C3, C15, D3, D4)
- [What is Microsoft Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-azure-ai-foundry) (C0, C2, C17)
- [Models sold directly by Azure](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure) (C0, C1, C6, D1, D3, D5)
- [Foundry Local GA announcement](https://devblogs.microsoft.com/foundry/foundry-local-ga/) (C0, C2, D1, D3)
- [What's new in Microsoft Foundry, Build 2026](https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-build-2026/) (C13, C14, C16, C17, D1, A1, A3, A6)
- [What's new in Microsoft Foundry, July–August 2026](https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-july-august-2026/) (C8, C9, C17, D2, D3, D6, A2, A4)
- [Foundry Agent Service at Build 2026](https://devblogs.microsoft.com/foundry/agent-service-build2026/) (C8, C9, C12, C13, C15, C17, D2, D3, D6, D7, A2, A4)

## Prompting, structured outputs and tools

- [OpenAI, Introducing Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/) (C3)
- [Anthropic, Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (C3, C8, C10, C14)
- [Claude Opus 5.5 overview (prompt caching and batch pricing)](https://platform.claude.com/docs/en/models/opus-5-5/overview) (C1, C3, C13, C15, D5, A1)

## Retrieval, RAG and context engineering

- [Vectors in SQL Server and Azure SQL](https://learn.microsoft.com/en-us/sql/sql-server/ai/vectors) (C6, C10, A3)
- [Azure AI Search: what's new](https://learn.microsoft.com/en-au/Azure/search/whats-new) (C6, C7, C10, C13, C17, A3)
- [Azure AI Search: agentic retrieval overview](https://learn.microsoft.com/azure/search/agentic-retrieval-overview) (C7, C13, A3)
- [.NET vector stores overview (Microsoft.Extensions.VectorData)](https://learn.microsoft.com/en-us/dotnet/ai/vector-stores/overview) (C6, A3)
- [Cormack et al., Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) (C7)
- [Anthropic, Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) (C7, C13, D5, A1, A3)
- [What's new in Content Understanding at Build 2026](https://devblogs.microsoft.com/foundry/whats-new-in-azure-content-understanding-at-build-2026/) (C7, D3, A3)
- [Foundry RAG evaluators](https://learn.microsoft.com/en-my/Azure/foundry/concepts/evaluation-evaluators/rag-evaluators) (C6, C7, C14, A3)
- [Agent Framework RAG (TextSearchProvider)](https://learn.microsoft.com/agent-framework/agents/rag) (C7, C9, C13, A3)
- [RAGAS metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) [Python] (C7, C10, C14, A3)
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (C7, C13)
- [Edge et al., GraphRAG](https://arxiv.org/abs/2404.16130) (C13, A3)
- [Microsoft Research, LazyGraphRAG](https://www.microsoft.com/en-us/research/blog/lazygraphrag/) (C13, A3)
- [Foundry memory at Build 2026](https://devblogs.microsoft.com/foundry/memory-build2026/) (C9, C13, D7)

## MCP and agent interoperability

- [MCP specification 2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) (C3, C8, C12, C13, C15, C16, D2, D4, D5, D6, A4)
- [AAIF, MCP 2026-07-28: what's changing and how to migrate](https://aaif.io/blog/mcp-2026-07-28-whats-changing-and-how-to-migrate) (C8, C16, D2, D4, D6, A4)
- [MCP C# SDK 2.0 announcement](https://www.i-programmer.info/news/89-net/19065-c-sdk-for-model-context-protocol-version-20-announced.html) (secondary) (C8, D6, A4)
- [Azure Functions MCP bindings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-mcp) (C8, C17, D4, A4)
- [Anthropic, Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) (C8, D2, D5)
- [MCP Registry preview](https://blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview/) (D6, A4)
- [Linux Foundation, A2A protocol v1.0](https://linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year) (C12, C17, A1, A2, A4)
- [AG-UI documentation](https://docs.ag-ui.com) (D4)

## Agents, workflows and orchestration

- [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (C9, C12)
- [Microsoft Agent Framework 1.0 announcement](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/) (C9, C10, C12, C17, D2, D4, A4)
- [MAF workflows overview](https://learn.microsoft.com/en-us/agent-framework/workflows/overview) (C12, D2)
- [MAF workflows: human-in-the-loop](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) (C9, C12, D2, D4, A4, A5)
- [MAF Durable extension / Azure Functions hosting](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions) (prerelease) (C9, C12, C17, D2, A4, A5)
- [Azure Architecture Center, AI agent orchestration patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) (C9, C12, A2)
- [Anthropic, How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (C12, D7, A1, A2)
- [Cognition, Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) (C12, C19, A2)
- [Anthropic, Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (C13, D2)
- [Azure Container Apps dynamic sessions](https://learn.microsoft.com/en-us/azure/container-apps/sessions) (C16, C17, D2)

## Evaluation, testing and reliability

- [Husain & Shankar, LLM evals FAQ](https://hamel.dev/blog/posts/evals-faq/) (C5, C10, C11, C14, D4, D7, A1, A7)
- [Husain, Using LLM-as-a-Judge](https://hamel.dev/blog/posts/llm-judge/) (C5, C14)
- [Microsoft.Extensions.AI.Evaluation libraries](https://learn.microsoft.com/en-us/dotnet/ai/evaluation/libraries) (C5, C7, C9, C10, C11, C14, C16, C18, D7, A5, A6)
- [Microsoft Foundry built-in evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators) (C14, D7)
- [Reinhard, How to evaluate AI agents in Microsoft Foundry](https://jannikreinhard.com/microsoft-foundry-agent-evaluations/) (practitioner) (C5, C14, C15, D7, A5)
- [Yao et al., τ-bench](https://arxiv.org/abs/2406.12045) (C5, C9, C10, C14, D7, A5)
- [τ²-bench](https://arxiv.org/abs/2506.07982) (C14, D7)
- [Stryker.NET](https://stryker-mutator.io/docs/stryker-net/introduction/) (C11)
- [Playwright test agents](https://playwright.dev/docs/test-agents) [Node] (C11, C19, D4)
- [Jimenez et al., SWE-bench](https://arxiv.org/abs/2310.06770) and [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) (D6, D7)
- [Berkeley RDI, Agentic AI (green and white agents)](https://rdi.berkeley.edu/agentic-ai/f25) (D6)

## Observability, cost and model lifecycle

- [Dash0, OpenTelemetry GenAI semantic conventions explained](https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained) (C9, C15, D5, A5)
- [GenAI semantic conventions are not stable yet](https://dev.to/azena-ai/opentelemetrys-genai-semantic-conventions-are-not-stable-yet-heres-what-actually-shipped-in-2026-3mke) (secondary) (C2, C15, D5, A5)
- [GenAIOps for organisations with MLOps investments](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/genaiops-for-mlops) (C15)
- [Foundry model retirements](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements) (C0, C2, C15, C17, D1, D5, D7, A1, A5, A7)
- [Foundry model router](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-router) (C15, C17, D5, A1, A5)
- [APIM AI gateway capabilities](https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities) (C8, C12, C15, C17, D5, D7, A2, A4, A5)
- [Per-task vs per-token cost (September 2026 model tracker)](https://www.digitalapplied.com/blog/ai-model-releases-september-2026-tracker) (aggregator) (C1, C15, D5, A1, A5)
- [Azure SRE Agent FAQ](https://learn.microsoft.com/en-us/azure/sre-agent/faq) (C19, D7, A7)

## Security and red teaming

- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) (C3, C10, C16, D4)
- [OWASP Top 10 for Agentic Applications, summary](https://cycode.com/blog/owasp-top-10-agentic-applications/) (C16, D2, D4, A4, A6)
- [MITRE ATLAS](https://atlas.mitre.org) (C16)
- [Willison, The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (C8, C16, A2)
- [Beurer-Kellner et al., Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837) (C16, D2)
- [Meta, Agents Rule of Two](https://ai.meta.com/blog/practical-ai-agent-security/) (C9, C16)
- [Invariant Labs, MCP tool poisoning attacks](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks) (C8, C16, D6, A4)
- [Azure AI Content Safety overview](https://learn.microsoft.com/en-gb/azure/ai-services/content-safety/overview) (C3, C7, C14, C16, C18, D3, A2, A3, A5)
- [Foundry guardrails overview](https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview) (C16, A2, A6)
- [AI Red Teaming Agent](https://learn.microsoft.com/azure/ai-foundry/concepts/ai-red-teaming-agent) (C14, C16, A3, A4, A6)
- [PyRIT](https://github.com/Azure/PyRIT) [Python] (C14, C16)
- [What's new in Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/whats-new-agent-id) (C16, D2, A2, A4)
- [CSA research note on slopsquatting](https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419/) (C4, C11, C16, C19, D6, A7)

## Coding agents and the automated SDLC

- [Claude Code best practices](https://code.claude.com/docs/en/best-practices) (C4, C11, C19, D6, A7)
- [Claude Code overview](https://code.claude.com/docs/en/overview) (C4, C19, D6)
- [AGENTS.md](https://agents.md) (C4, D6)
- [Anthropic, Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) (C4, D2)
- [Copilot cloud agent with Azure Boards](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/use-copilot-agents/cloud-agent/integrate-cloud-agent-with-azure-boards) (C4, C19, D6, A7)
- [GitHub Copilot testing for .NET in Visual Studio](https://devblogs.microsoft.com/dotnet/github-copilot-testing-for-dotnet-available-in-visual-studio/) (C4, C11, C19)
- [Copilot SDK is generally available](https://github.blog/changelog/2026-06-02-copilot-sdk-is-now-generally-available/) (C19, D6)
- [Agentic autofix for code scanning alerts, GA](https://github.blog/changelog/2026-10-15-agentic-autofix-for-code-scanning-alerts-general-availability) (C19, A7)
- [Böckeler, Understanding spec-driven development](https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) (C4, C11, C19, A7)
- [Thoughtworks Technology Radar Vol. 34 digest](https://agentic-ai.readthedocs.io/en/latest/AgenticTechStack/thoughtworks-radar-vol34/) (secondary) (C4, C8, C11, C16, C19, D6, A7)

## Model customization and local models

- [Foundry fine-tuning overview](https://learn.microsoft.com/en-us/azure/foundry/fine-tuning/overview) (C1, D1)
- [Hu et al., LoRA](https://arxiv.org/abs/2106.09685) (D1)
- [Dettmers et al., QLoRA](https://arxiv.org/abs/2305.14314) (D1)
- [Hinton et al., Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531) (D1)
- [ML.NET](https://dotnet.microsoft.com/apps/ai/ml-dotnet) (C1, D1)

## Front-ends and accessibility

- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) (D4)

## Architecture and platform

- [Baseline Microsoft Foundry chat reference architecture](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat) (C9, C15, C16, C17, C18, D4, D5, A1, A2, A5, A6)
- [Azure AI Landing Zones](https://github.com/Azure/AI-Landing-Zones) (preview) (C17, A2)
- [Cloud Adoption Framework AI scenario](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/) (C17, A1, A2)
- [Well-Architected Framework for AI workloads](https://learn.microsoft.com/azure/well-architected/ai/get-started) (A2, A7)
- [Multitenant approaches for AI and machine learning](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/ai-machine-learning) (A3, A4, A5)
- [C4 model](https://c4model.com) and [Structurizr DSL](https://docs.structurizr.com/dsl) (A2)

## Responsible AI, the EU AI Act and governance

- [Regulation (EU) 2024/1689 (AI Act), EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) (C18, A6)
- [Digital Omnibus on AI published (Cuatrecasas)](https://www.cuatrecasas.com/en/spain/intellectual-property/art/digital-omnibus-ai-has-been-published) (C18, D3, A6)
- [AI omnibus formally adopted (Addleshaw Goddard)](https://www.addleshawgoddard.com/en/insights/insights-briefings/2026/technology/eu-ai-act-ai-omnibus-formally-adopted/) (C10, C18, D3, D7, A6)
- [FPF EU AI Act Timeline 2026 R2](https://fpf.org/wp-content/uploads/2026/07/FPF-EU-AI-Act-Timeline-2026-R2.pdf) (C18, A6)
- [AI regulation in Bulgaria tracker](https://vlolawfirm.com/trackers/ai-regulation-bulgaria) (single source, unconfirmed) (C18, A6)
- [Microsoft Responsible AI](https://www.microsoft.com/en-us/ai/responsible-ai) (C18, D4)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) (C18, A6)
- [ISO/IEC 42001](https://www.iso.org/standard/81230.html) (C18, A6)

## Delivery evidence, roles and certifications

- [DORA 2025 report](https://blog.google/technology/developers/dora-report-2025/) (C4, C11, C19, A7)
- [DORA AI Capabilities Model (InfoQ)](https://infoq.com/news/2026/03/ai-dora-report/) (C4, C19, A7)
- [METR uplift update, February 2026](https://metr.org/blog/2026-02-24-uplift-update/) (C4, C19, A7)
- [AB-100 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ab-100) (A1, A7)
