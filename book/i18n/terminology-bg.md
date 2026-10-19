# Bulgarian translation: style guide and terminology

Working reference for everyone translating the Learner Handbook (EN → BG). It is binding: when a term or rule here conflicts with personal preference, this file wins. If you hit a term that is missing, pick the form that best matches the rules below, write it down in your hand-off notes, and do not invent a second variant for a term that is already listed.

Scope: everything under `book/` (README, start-here, modules C0–C19, D1–D7, A1–A7, capstone, appendix), the site navigation and the PDF cover/footer.

---

## 1. Style rules

### 1.1 Voice and register

1. **Audience.** Bulgarian software developers with professional experience. Write the way a senior Bulgarian engineer writes a good technical blog post or internal design doc: natural, precise, without bureaucratic Bulgarian („осъществява се извършването на…“) and without calques of English word order.
2. **Translate meaning, not words.** Restructure sentences freely. Split long English sentences. Prefer verbs over nominalisations („проверете дали…“, not „извършване на проверка дали…“).
3. **Address the learner with „вие“ (lowercase)** and its verb forms: „Направете…“, „ще можете да…“, „вашият агент“. Never „Вие“ with a capital letter, never „ти“. Imperatives use the plural form („Стартирайте“, „Запишете“).
4. **Active voice, short sentences.** Passive only when the actor is genuinely unknown or irrelevant.
5. **Keep the tone direct.** The source is blunt („Do not skip it“). Keep that: „Не го пропускайте.“ Do not soften it with „би било добре да…“.
6. **Bold, italics and emphasis** stay on the equivalent words. If a bolded label ends with a colon in the source (`**Goal:**`), keep the colon inside the bold (`**Цел:**`).
7. **Slogans and named cycles** (e.g., *Learn → Do → Break → Fix → Explain*, *predict → run → explain*) use the short singular imperative, as Bulgarian slogans do („Научи → Направи → Счупи → Поправи → Обясни“). This is the only exception to rule 3.

### 1.2 Bulgarian vs English (Latin script) terms

8. **The principle.** Use what Bulgarian developers actually write in good technical prose. There are three classes, and the terminology table (section 3) assigns every term to one of them:
   - **Bulgarian word.** It is established and fully inflected: агент, модел, токен, промпт, контекст, кеш, тест, инструмент, извличане, оркестрация, наблюдаемост, латентност, тенант, фрагмент, гейт, бекенд, фронтенд, бъг, бенчмарк, секрет, таймаут, табло (dashboard), срив (outage), постмортем, функционалност (feature).
   - **English kept in Latin script.** A term of art that Bulgarian developers do not translate: RAG, LLM, MCP, embedding, eval/evals, fine-tuning, guardrails, trace, span, reranker, pipeline, endpoint, prompt injection, red teaming, canary release, rollback, feature flag, middleware, workflow, hooks, skills, sandbox, worktree, devcontainer, commit, pull request (PR), issue, CI/CD.
   - **Bulgarian word + English in parentheses on first use.** A good Bulgarian term exists but readers will meet the English one in docs and tools: „анализ на грешките“, „отворено кодиране (open coding)“, „човек в цикъла (human-in-the-loop, HITL)“.
9. **Gloss on first use per chapter.** The first time a kept-English term that is not self-evident appears in a chapter (one `.md` file), add a short Bulgarian gloss in parentheses: „embedding (векторно представяне)“, „guardrails (защитни механизми)“, „canary release (пускане към малък дял от трафика)“. The table gives the gloss to use. Do not repeat the gloss later in the same chapter. Self-evident terms (LLM, API, CI/CD, PR, JSON, SQL, .NET, Azure) never get a gloss.
10. **English in parentheses after a Bulgarian term** (class 3) also appears only on the first use per chapter. Never put glosses or English equivalents in headings or nav titles; add them at the first use in the body text under the heading.
11. **Do not use Cyrillic transliterations of Latin-kept terms** („ембединг“, „пайплайн“, „ендпойнт“, „ревю“) and do not use Latin spellings of Bulgarian-class terms („agent“, „token“ in prose). Exception: code, identifiers and product names always stay exactly as in the source.
12. **„AI“ vs „ИИ“.** In technical prose use **AI** (Latin): „AI функционалност“, „AI агент“, „AI gateway“, „генеративен AI“. Use **ИИ** only in legal and regulatory text and in the official legal terms of the AI Act: „система с ИИ“, „Акт за изкуствения интелект“, „грамотност в областта на ИИ“.
13. **Official legal terms are not negotiable.** Terms marked **official BG legal term** in the table come from the Bulgarian texts of Regulation (EU) 2024/1689 (AI Act) and Regulation (EU) 2016/679 (GDPR). Use them verbatim, even where developer slang differs. In particular: deployer → „внедрител“, provider → „доставчик“, high-risk AI system → „високорискова система с ИИ“, general-purpose AI model → „модел на ИИ с общо предназначение“, intended purpose → „предназначение“, deep fake → „убедителен фалшификат“.
14. **The word „внедряване“ is reserved.** Because the AI Act deployer is „внедрител“, do **not** use „внедряване/внедрявам“ for software deployment. Software deploy → „разгръщане/разгръщам“. A Foundry/Azure *model deployment* (a named resource) → „deployment“ (Latin), e.g. „deployment-ът на модела“ is not allowed; write „deployment на модела“ or „този deployment“.

### 1.3 Inflecting English terms

15. **No Bulgarian suffixes on Latin words.** Do not write „prompt-ът“, „embedding-ите“, „trace-ове“, „commit-нах“, „merge-нахме“. Instead:
    - put definiteness on a Bulgarian word in front: „системният промпт“, „моделът за embeddings“, „този trace“, „всеки span“, „последният commit“;
    - use a Bulgarian head noun: „стъпката build“, „файлът `AGENTS.md`“, „протоколът MCP“, „инструментът `azd`“;
    - use a Bulgarian verb: „направете commit“, „слейте PR“, „разгърнете“, not „commit-нете“, „merge-нете“, „deploy-нете“.
16. **Whitelisted acronyms may take a hyphenated article or plural.** Only these: **PR** (PR-ът, PR-а, PR-и), **API** (API-то, API-та), **ADR** (ADR-ът, ADR-а, ADR-и), **SDK** (SDK-то), **LLM** (LLM-ът, LLM-и), **SLO** (SLO-то, SLO-та). All other acronyms take a Bulgarian head noun instead: „MCP сървърът“, „протоколът A2A“, „таблото в KQL“. Everything else: rephrase.
17. **Plural of Latin nouns keeps the English plural form**, carried by a Bulgarian determiner or numeral: „всички traces“, „тези hooks“, „100 traces“, „три spans“, „нови embeddings“, „скритите evals“. Never „span-а“, „trace-ове“, „hook-ове“.
18. **Gender for agreement** of Latin nouns: masculine by default („нов endpoint“, „скрит trace“, „вашият pipeline“); neuter for API/SDK („новото API“); feminine never. „evals“ and „embeddings“ agree as plural.
19. **Counted form.** Bulgarian masculine nouns after numerals use the counted form: „100 токена“, „два агента“, „три гейта“, „50 фрагмента“.

### 1.4 What never to translate

20. **Code, entirely.** Code blocks are copied byte for byte, **including code comments and string literals**. (Comments in the source are short technical notes that must match the code that readers copy; prompts inside code are part of the lab.) Inline code in backticks is never translated either.
21. **Commands, flags and output**: `dotnet test`, `azd up`, `git tag`, `--purge`.
22. **File and folder names, paths, branches, git tags**: `docs/adr/0007-document-parsing.md`, `c7/lab2-start`, `copilot/*`, `evals/golden/v1/`.
23. **URLs and link targets.** Translate the link **text** only: `[Course overview](course-overview.md)` → `[Преглед на курса](course-overview.md)`. Keep the target exactly as in the source (`.md`, not `.bg.md`; the i18n plugin resolves the localised page). Keep any `#fragment` as is.
24. **Product, service, API, protocol, package and feature names**, with their capitalisation: Microsoft Foundry, Foundry Agent Service, Foundry IQ, Foundry Local, Microsoft Agent Framework (MAF), Azure AI Search, Azure API Management (APIM), Content Safety, Content Understanding, Prompt Shields, Entra Agent ID, Azure SRE Agent, AI Red Teaming Agent, GitHub Copilot, Copilot Studio, Claude Code, Claude Agent SDK, Aspire, Voice Live, Responses API, Assistants API, Model Context Protocol, A2A, AG-UI, OpenTelemetry, PyRIT, Playwright, Stryker.NET, xUnit, MSTest, Bicep, KQL, Structurizr. Also course entities: **Fleet Ops Copilot, Fleet Assistant, Fleet Analyst, Trakia Freight, TrakiaOps, TrakiaBench, TrakiaSim**, and fictional clients (Municipality of Trimontium → keep „Trimontium“; translate „Municipality of“ → „Община“; „Rhodope Medical Network“, „Maritsa Home“ stay). Role titles **AI Solution Developer** and **AI Solution Architect** stay in English (they are the course credentials).
25. **Identifiers**: module IDs (C0–C19, D1–D7, A1–A7), gates (G1–G3), competency areas (K1–K12), ADR-0012, TRK-0471, ASI01, LLM01, `Lab=C2.*`, risk IDs. **Never replace Latin letters in identifiers with look-alike Cyrillic letters** (C/С, A/А, K/К, E/Е, P/Р, O/О, T/Т, H/Н, B/В, M/М, X/Х). Check this before delivery; it breaks search and links.
26. **Metric and statistic names**: recall@k, nDCG@k, pass@k, pass^k, pass^3, TPR, TNR, ASR, EX, CPST, TTFT, TPM, PTU, RRF, BM25, McNemar's test → „тест на McNemar“.
27. **Markdown structure**: heading levels, list nesting, table column count and alignment row, admonitions, `{.part}` / `{#id}` attributes, HTML tags, image paths. Translate image **alt text** (`![Course map]` → `![Карта на курса]`).
28. **Quoted literal strings that are examples of model input/output** (e.g., a Bulgarian Latin-script user message like „Kamion PB4521KH…“) stay exactly as in the source. English example user questions shown in prose may be translated only if the surrounding text does not depend on them being English; when in doubt, keep them and add the translation in parentheses.
29. **Book titles, paper titles and quoted English sources** in References stay in English. Translate only the connecting prose („Използвайте за…“).

### 1.5 What to translate

30. Headings, prose, table cells (except code/identifiers), list items, admonition text, image alt text, link text, the module header line (labels and values), rubric cells, Common pitfalls, explanatory text inside References entries.

### 1.6 Module and lab structure: fixed strings

Use these exact strings. They must be identical in all 34 modules.

| English (source) | Bulgarian (use exactly) |
|---|---|
| `## Why this matters` | `## Защо е важно` |
| `## Learning outcomes` | `## Резултати от обучението` |
| `By the end of C5 you can:` | `В края на C5 ще можете да:` — then each numbered item starts with the bold verb in 2nd person plural, lowercase: `1. **извършите** анализ на грешките…`, `2. **изградите**…` |
| `## Concepts` | `## Концепции` |
| `### Misconceptions to unlearn` / `**Misconceptions to unlearn:**` | `### Погрешни представи, от които да се откажете` / `**Погрешни представи, от които да се откажете:**` |
| `## Tools & versions (as of Oct 2026)` | `## Инструменти и версии (към окт. 2026 г.)` |
| Table header `Tool / package \| Purpose \| Status \| Notes` | `Инструмент / пакет \| Предназначение \| Статус \| Бележки` |
| `## Labs` | `## Лабораторни упражнения` |
| `### Lab 1 — … (≈2h)` | `### Лабораторно упражнение 1 — … (≈2 ч)` |
| `**Goal:**` | `**Цел:**` |
| `**Start state:**` | `**Начално състояние:**` |
| `**Steps:**` | `**Стъпки:**` |
| `**Break it:**` | `**Счупете го:**` |
| `**Acceptance criteria:**` | `**Критерии за приемане:**` |
| `**Stretch:**` | `**Допълнително предизвикателство:**` |
| `## Kata` | `## Ката` |
| `## Product increment — Fleet Ops Copilot` | `## Продуктов инкремент — Fleet Ops Copilot` |
| `## Factory increment — your agentic SDLC` | `## Инкремент на Фабриката — вашият агентен SDLC` |
| `## Assessment` | `## Оценяване` |
| Rubric header `Criterion \| Novice \| Competent \| Proficient \| Expert` | `Критерий \| Начинаещ \| Компетентен \| Напреднал \| Експерт` |
| `**Auto-checked:**` | `**Автоматични проверки:**` |
| `**Human-reviewed:**` | `**Преглед от човек:**` |
| `## Common pitfalls` | `## Чести грешки` |
| `## References` | `## Източници` |
| `**What separates an expert architect from a proficient one here:**` | `**Какво отличава експертния архитект от напредналия тук:**` |
| `**Decision rule(s):**` | `**Правило за решение:**` / `**Правила за решение:**` |
| `> **Not legal advice.**` | `> **Това не е правен съвет.**` |

Module header line (blockquote at the top of each module):

| English | Bulgarian |
|---|---|
| `**Level:** 1 — Foundations (Beginner)` | `**Ниво:** 1 — Основи (начинаещи)` |
| `**Level:** 2 — Building blocks (Intermediate)` | `**Ниво:** 2 — Градивни елементи (средно ниво)` |
| `**Level:** 3 — Production systems (Advanced)` | `**Ниво:** 3 — Продукционни системи (напреднали)` |
| `**Level:** Expert — AI Solution Developer track` | `**Ниво:** Експерт — специализация AI Solution Developer` |
| `**Level:** Expert — AI Solution Architect track` | `**Ниво:** Експерт — специализация AI Solution Architect` |
| `**Duration:** 10h (theory 20% / labs 80%)` | `**Продължителност:** 10 ч (теория 20% / упражнения 80%)` |
| `**Prerequisites:**` | `**Предварителни изисквания:**` |
| `**Volatility:** Low / Med / High` | `**Променливост:** ниска / средна / висока` |

Rubric levels are always **Начинаещ / Компетентен / Напреднал / Експерт** (also in prose: „оценява се като Начинаещ“).

### 1.7 Numbers, units, dates

31. **Decimal comma** in prose **and** in tables: 3,5 ч; 0,85; 4,1/5; 19,7%. Exceptions, which stay exactly as in source: anything in code/backticks, version numbers (1.42.0, Aspire 13.6, MAF 1.0, API 2026-04-01), release IDs (2026.11), model names, IP addresses, file names.
32. **Thousands separator**: non-breaking space for 5+ digits (10 000; 225 000; 2 230 000). Four-digit numbers are written without a separator (1000; 4096). Never a comma or dot as thousands separator.
33. **k / M / B suffixes** in prose → „хил.“, „млн.“, „млрд.“: „~113 хил. токена“, „2,23 млн. примера“. In table cells where space is tight, „113k“ may stay. Inside identifiers or model names (`200k`), never change.
34. **Percent** stays attached to the number as in the source: „20%“.
35. **Currency**: number, non-breaking space, symbol after: „1,02 $“, „250 €“, „0,40 $ за 1 млн. токена“. Ranges: „150–300 €“.
36. **Units**: hours „ч“ (2 ч, ≈2,25 ч), minutes „мин“ (30 мин), seconds „с“, milliseconds „ms“, days „дни“, weeks „седмици“. Header shorthand like `10h` → `10 ч`. Data sizes stay MB, GB.
37. **Dates**: „9 април 2026 г.“, „към октомври 2026 г.“, short in tables „окт. 2026 г.“ ISO dates and API versions (2026-04-01, MCP 2026-07-28) stay as is. Month names lowercase.
38. **Times**: 24-hour „06:40“. Durations „48 часа“ in prose, „48 ч“ in tables.
39. **Ranges**: en dash without spaces, as in source: „3–5“, „C6–C11“, „20–40 минути“.
40. **Symbols** ≈, ≥, ≤, ×, ÷, →, ● stay.
41. **Abbreviations**: e.g. → „напр.“, i.e. → „т.е.“, etc. → „и т.н.“, vs → „срещу“ (or „или“ when it means a choice), Art. → „чл.“, para. → „ал.“, point → „т.“, Annex → „приложение“.

### 1.8 Punctuation and typography

42. **Quotation marks**: „…“ (opening low „ U+201E, closing high “ U+201C; not the ASCII "). Nested: ‚…‘. English quotes "…" around Bulgarian text are wrong. Quotes inside code are untouched.
43. **Dashes**: keep the source's em dash with spaces ( — ) in titles and prose; the hyphen „-“ only inside compounds („PR-ът“, „read-only“).
44. Bulgarian comma rules apply (comma before „че“, „който“, „за да“, „когато“, etc.), even where the English has none.
45. **Capitalisation**: Bulgarian sentence case in headings („Наблюдаемост, GenAIOps и разходи“), lowercase for months, weekdays, „вие“, languages and nationalities. Product names keep their own capitalisation.

### 1.9 Status words and fixed phrases

| English | Bulgarian | Rule |
|---|---|---|
| GA | „GA (общодостъпно)“ on first use per chapter, then „GA“ | In status columns always just `GA`. |
| preview | „preview (предварителна версия)“ on first use, then „preview“ | In status columns just `preview`. „в preview“ is fine. |
| prerelease | „prerelease (предварително издание)“, then „prerelease“ | NuGet/package status. |
| Development (OTel stability) | `Development` | Status name; do not translate. |
| legacy | „legacy (остаряло)“ first use, then „legacy“ | |
| deprecated | „обявено за остаряло (deprecated)“, then „deprecated“ in tables | |
| retired / retirement | „изведено от употреба“ / „извеждане от употреба“ | |
| verify against current documentation | **„проверете в актуалната документация“** | Fixed. Bold if bold in source. |
| verify (status/name) | „проверете“ | e.g. „Verify per-feature status“ → „Проверете статуса на всяка функционалност“. |
| as of October 2026 | „към октомври 2026 г.“ | |
| (first taught in C7) | „(въведено в C7)“ | Glossary. |
| (see Capstone) | „(вж. Финален проект)“ | Glossary. |
| Not legal advice | „Това не е правен съвет.“ | |
| Course rule: … | „Правило на курса: …“ | |

### 1.10 Course-specific terms (decisions)

| English | Bulgarian | How to use |
|---|---|---|
| the Factory | **Фабриката** (capital Ф, definite) | First use per chapter: „Фабриката (Factory, вашият агентен SDLC)“. Then „Фабриката“, „във вашата Фабрика“. |
| kata | **ката** (ж.р.; членувано „катата“; мн.ч. „ката“) | Plural: „три ката“, „упражненията ката“. |
| lab | **лабораторно упражнение** | In headings always full. In prose „лабораторното упражнение“; plural „лабораторните упражнения“. Do not use „лаб“, „лабът“. |
| gate (exam) | **гейт** (м.р., гейтът, гейтове) | First use per chapter: „гейт (gate, практически изпит)“. „Gate G1“ → „гейт G1“. |
| gate (CI) | **гейт** | „eval гейт“, „гейт в CI“. Same word on purpose: the course equates the two. |
| hard gate | **задължителен критерий (hard gate)** | |
| Learn → Do → Break → Fix → Explain | **Научи → Направи → Счупи → Поправи → Обясни** | First use: add „(Learn → Do → Break → Fix → Explain)“. |
| Break it (lab step) | **„Счупете го“** | Label `**Счупете го:**`; in prose: стъпката „Счупете го“. |
| capstone | **финален проект** | First use: „финален проект (capstone)“. „Joint capstone“ → „Съвместен финален проект“. |
| track | **специализация** | „Developer track“ → „специализация AI Solution Developer“; „Expert track“ → „експертна специализация“; „A-track“ → „архитектурната специализация“. |
| learner | **курсист** | Not „обучаем“, „студент“. |
| module | **модул** | |
| increment | **инкремент** | Product/Factory increment. |
| oral / oral defense | **устен изпит / устна защита** | |
| design defense | **защита на дизайна** | |
| unaided segment | **част без AI помощ** | „solo-first“ → „първо самостоятелно“. |
| ownership rule | **правило за собственост** | Full form once: „правилото за собственост: отговаряте за всичко, което слеете“. |
| explain the diff | **„Обяснете промените“ (explain the diff)** | Kata/review practice. |
| Fleet Ops Copilot, Trakia Freight | unchanged | Never translated, never transliterated. „Trakia“ → „Trakia“ (not „Тракия“). |
| running product | **продуктът, който развивате** | |
| instructor / mentor / assessor | **преподавател / ментор / изпитващ** | |
| cohort | **випуск** | |

---

## 2. Fixed UI strings (site and PDF)

### 2.1 General

| English | Bulgarian |
|---|---|
| English (language switcher) | English |
| Bulgarian (language switcher) | Български |
| Site name | AI Solution Developer & Architect — Наръчник за курсиста |
| Learner Handbook | Наръчник за курсиста |
| Learner edition | Издание за курсисти |
| Release 2026.11 | Версия 2026.11 |
| content as of October 2026 | съдържание към октомври 2026 г. |
| Table of contents | Съдържание |
| Welcome | Добре дошли |
| Dark mode / Light mode | Тъмен режим / Светъл режим |
| Course map (image alt) | Карта на курса |
| Page X / Y (footer) | X / Y (unchanged format) |

Note: `mkdocs.yml` currently sets the BG `site_name` to „… — Наръчник за обучаемия“. Align it to „Наръчник за курсиста“.

### 2.2 Navigation: parts and pages

| English | Bulgarian |
|---|---|
| Start here | Започнете оттук |
| How to use this handbook | Как да използвате наръчника |
| Course overview | Преглед на курса |
| Assessment and gates | Оценяване и гейтове |
| Competency matrix | Матрица на компетентностите |
| Part 1 — Foundations (Level 1) | Част 1 — Основи (ниво 1) |
| Part 2 — Building blocks (Level 2) | Част 2 — Градивни елементи (ниво 2) |
| Part 3 — Production systems (Level 3) | Част 3 — Продукционни системи (ниво 3) |
| Part 4 — Expert track: AI Solution Developer | Част 4 — Експертна специализация: AI Solution Developer |
| Part 5 — Expert track: AI Solution Architect | Част 5 — Експертна специализация: AI Solution Architect |
| Part 6 — Joint capstone | Част 6 — Съвместен финален проект |
| Capstone | Финален проект |
| Appendix | Приложение |
| Glossary | Речник на термините |
| Further reading | Допълнителна литература |

### 2.3 Module titles (use in nav, H1 and every cross-reference)

| English | Bulgarian |
|---|---|
| C0 — Orientation, setup & toolchain | C0 — Ориентация, настройка и инструменти |
| C1 — How generative AI works: an engineer's mental model | C1 — Как работи генеративният AI: мисловен модел за инженери |
| C2 — Your first AI feature in .NET | C2 — Първата ви AI функционалност в .NET |
| C3 — Prompting, structured outputs & tool calling | C3 — Промптинг, структуриран изход и извикване на инструменти |
| C4 — Working with coding agents: the Factory, day one | C4 — Работа с кодиращи агенти: Фабриката, първи ден |
| C5 — Evals from day one | C5 — Evals от първия ден |
| C6 — Embeddings & vector search | C6 — Embeddings и векторно търсене |
| C7 — RAG: from documents to cited, permission-aware answers | C7 — RAG: от документи до отговори с цитати, съобразени с правата на достъп |
| C8 — Tools & the Model Context Protocol | C8 — Инструменти и Model Context Protocol |
| C9 — Agents with Microsoft Agent Framework | C9 — Агенти с Microsoft Agent Framework |
| C10 — Agents over structured data: text-to-SQL on SQL Server | C10 — Агенти върху структурирани данни: text-to-SQL върху SQL Server |
| C11 — Agentic testing: AI-driven TDD, mutation & E2E test agents | C11 — Агентно тестване: TDD с AI, мутационно тестване и агенти за E2E тестове |
| C12 — Workflows & multi-agent orchestration | C12 — Workflows и многоагентна оркестрация |
| C13 — Context engineering, advanced retrieval & memory | C13 — Инженеринг на контекста, напреднало извличане и памет |
| C14 — Failure-driven evals, LLM judges & red teaming | C14 — Evals, водени от грешките, LLM съдии и red teaming |
| C15 — Observability, GenAIOps & cost | C15 — Наблюдаемост, GenAIOps и разходи |
| C16 — Security for LLM & agentic systems | C16 — Сигурност на LLM и агентни системи |
| C17 — Shipping to Azure: hosting, AI gateway, IaC & interop | C17 — Пускане в Azure: хостинг, AI gateway, IaC и оперативна съвместимост |
| C18 — Responsible AI & the EU AI Act in practice | C18 — Отговорен AI и Актът за изкуствения интелект на ЕС на практика |
| C19 — The automated SDLC: agents from issue to production | C19 — Автоматизираният SDLC: агенти от issue до продукция |
| D1 — Model customization & small/local models | D1 — Адаптиране на модели и малки/локални модели |
| D2 — Long-running, durable & autonomous agents | D2 — Дълго работещи, устойчиви и автономни агенти |
| D3 — Multimodal & realtime agents | D3 — Мултимодални агенти и агенти в реално време |
| D4 — Agent UX & front-ends | D4 — UX и фронтенди за агенти |
| D5 — Performance & cost engineering | D5 — Инженеринг на производителността и разходите |
| D6 — Building your own agent tooling | D6 — Изграждане на собствени инструменти за агенти |
| D7 — Agent reliability engineering | D7 — Инженеринг на надеждността на агенти |
| A1 — AI strategy, use-case discovery & business case | A1 — AI стратегия, откриване на сценарии на употреба и бизнес обосновка |
| A2 — Azure AI reference architectures & Well-Architected for AI | A2 — Референтни AI архитектури в Azure и Well-Architected за AI |
| A3 — Enterprise knowledge & data architecture for AI | A3 — Корпоративна архитектура на знанията и данните за AI |
| A4 — Agent platform & integration architecture | A4 — Платформа за агенти и интеграционна архитектура |
| A5 — Reliability, scale, model lifecycle & FinOps | A5 — Надеждност, мащаб, жизнен цикъл на моделите и FinOps |
| A6 — AI governance, risk & compliance architecture | A6 — Архитектура за управление на AI, риска и съответствието |
| A7 — The architect's craft in AI programmes | A7 — Занаятът на архитекта в AI програми |

### 2.4 PDF cover and footer

| Element | English | Bulgarian |
|---|---|---|
| Cover H1 | AI Solution Developer & AI Solution Architect | AI Solution Developer & AI Solution Architect |
| Cover line 1 | Learner Handbook · Release 2026.11 · content as of October 2026 | Наръчник за курсиста · Версия 2026.11 · съдържание към октомври 2026 г. |
| Cover line 2 | Learning by doing on one evolving product, gated by evals | Учене чрез правене върху един развиващ се продукт, с гейтове, базирани на evals |
| Document title (metadata) | AI Solution Developer & Architect — Learner Handbook | AI Solution Developer & Architect — Наръчник за курсиста |
| Footer left | AI Solution Developer & Architect — Learner Handbook · 2026.11 | AI Solution Developer & Architect — Наръчник за курсиста · 2026.11 |
| Footer right | `n / N` | `n / N` |
| README tagline | Release 2026.11 · content as of October 2026 · Learner edition | Версия 2026.11 · съдържание към октомври 2026 г. · Издание за курсисти |
| PDF output file name | AI-Solution-Developer-Architect-Learner-Handbook.pdf | AI-Solution-Developer-Architect-Learner-Handbook-bg.pdf |

---

## 3. Terminology

Columns: **English**, the term as it appears in the source; **Bulgarian usage**, what to write (text in parentheses = the first-use gloss or the English term to add on first use per chapter); **Note**, the decision, collisions, or **official BG legal term** (AI Act = Regulation (EU) 2024/1689; GDPR = Regulation (EU) 2016/679).

Class shorthand in notes: **BG** = Bulgarian word, inflect normally; **EN** = keep in Latin script, no Bulgarian suffixes (rule 15); **name** = product or proper name, never translate.

Not repeated in the table: course-structure terms (Factory, kata, lab, gate, hard gate, capstone, track, learner, Learn → Do → Break → Fix → Explain, explain the diff, ownership rule, unaided segment, cohort, oral, design defense, instructor, mentor) are in 1.10; module and lab labels (Why this matters … References, Goal, Start state, Steps, Break it, Acceptance criteria, Stretch, Auto-checked, Volatility, rubric levels) are in 1.6; status words (GA, preview, prerelease, legacy, deprecated, retired) are in 1.9; product, protocol, metric and code names from the glossary are listed after the table.

| English | Bulgarian usage | Note |
|---|---|---|
| abstain / abstention | въздържа се от отговор / въздържане от отговор | BG. Not „абстиниране“. |
| acceptance test (human-owned) | приемателен тест (написан от човек) | BG. |
| actionable error | грешка с указания за поправка (actionable error) | BG + EN on first use. |
| ADR (architecture decision record) | ADR (запис на архитектурно решение) | EN acronym; ADR-ът, ADR-и allowed. |
| agent | агент | BG; агентът, агенти, два агента. |
| agent goal hijack (ASI01) | отвличане на целта на агента (ASI01) | Translate OWASP risk names, keep the ID. |
| agent registry | регистър на агентите | BG. |
| agentic | агентен / агентна / агентни | BG: „агентна система“, „агентно тестване“. |
| agentic retrieval | агентно извличане (agentic retrieval) | Azure AI Search feature; BG + EN. |
| agentic SDLC | агентен SDLC | BG adjective + EN acronym. |
| agents-as-code | агенти като код (agents-as-code) | BG + EN. |
| AI | AI | Technical prose. Use „ИИ“ only in legal terms (rule 12). |
| AI Act (EU) | Актът за изкуствения интелект (AI Act); кратко „Актът за ИИ“ | **official BG legal term** (short title of Reg. 2024/1689: „Акт за изкуствения интелект“). |
| AI gateway | AI gateway (единна точка за политики върху трафика към моделите) | EN. |
| AI literacy | грамотност в областта на ИИ | **official BG legal term** (AI Act, чл. 4). |
| AI management system (AIMS) | система за управление на ИИ (AIMS) | ISO/IEC 42001 term. |
| AI system | система с ИИ | **official BG legal term** (AI Act, чл. 3, т. 1). In non-legal prose „AI система“ is fine. |
| alert | известие (alert); глагол „известява“ | BG. Azure Monitor alert rule → „правило за известяване“. |
| allow-list / deny rule | списък с разрешени (allow-list) / правило за забрана (deny rule) | BG + EN. |
| Annex I / Annex III | приложение I / приложение III | **official BG legal term**. Lowercase in running text. |
| API | API | EN; API-то allowed. |
| approval card | карта за одобрение (approval card) | BG + EN. |
| Art. 50 transparency obligations | задължения за прозрачност по чл. 50 | **official BG legal term**. |
| ASR (attack success rate) | ASR (процент успешни атаки) | Metric name stays ASR. |
| authorised representative | упълномощен представител | **official BG legal term** (AI Act). |
| automation bias | пристрастие към автоматизацията (automation bias) | BG + EN. |
| availability | наличност | BG (SRE sense). |
| axial coding | аксиално кодиране (axial coding) | BG + EN; standard qualitative-research term. |
| backend pool (APIM) | backend pool (пул от бекенди) | EN, APIM type name. |
| backoff | изчакване с нарастващ интервал (backoff) | BG + EN. |
| baseline (measurement) | изходно ниво (baseline) | BG. „working baseline“ (lab) → „работеща изходна версия“. |
| baseline (reference architecture) | базова референтна архитектура | „Baseline Microsoft Foundry chat reference architecture“ — keep the name, add „(базовата референтна архитектура)“. |
| benevolent dictator | „добронамерен диктатор“ (benevolent dictator) | BG in quotes + EN. |
| biometric categorisation system | система за биометрично категоризиране | **official BG legal term**. |
| blue/green | blue/green | EN: „blue/green преиндексиране“. |
| BOLA (broken object level authorization) | BOLA (неоторизиран достъп до чужд обект) | EN acronym + gloss. |
| bootcamp (pace) | интензивен формат (bootcamp) | BG + EN. |
| BPE (byte-pair encoding) | BPE (byte-pair encoding) | EN. |
| branch / branch protection | клон (branch) / защита на клона | BG. Branch names in backticks. |
| build / buy / extend | изграждане / покупка / разширяване (build / buy / extend) | BG + EN. |
| build (CI) | build | EN; rephrase: „стъпката build“, „build-ът“ not allowed. „the build is green“ → „build минава“. |
| business case | бизнес обосновка (business case) | BG + EN. |
| canary release | canary release (пускане към малък дял от трафика) | EN. Verb: „пуснете като canary“. |
| cascade (model routing) | каскада (cascade) | BG. |
| CE marking | маркировка „СЕ“ | **official BG legal term** (AI Act). |
| chaos engineering | chaos engineering (контролирано внасяне на откази) | EN. |
| chargeback | chargeback (префактуриране на разходите към звената) | EN. |
| checkpoint / checkpointing | контролна точка / записване на контролни точки (checkpointing) | BG. |
| chunk | фрагмент (chunk) | BG; фрагментът, фрагменти. Class names like `HeadingChunker` unchanged. |
| chunking | фрагментиране (chunking) | BG. „semantic chunking“ → „семантично фрагментиране“. |
| CI/CD | CI/CD | EN. |
| circuit breaker | прекъсвач (circuit breaker) | BG. |
| citation / cited answer | цитат / отговор с цитати | BG. „citation accuracy“ → „точност на цитатите“. |
| code of practice (GPAI) | кодекс за добри практики | **official BG legal term** (AI Act, чл. 56). |
| code review / code scanning | преглед на кода (code review) / сканиране на кода | BG. |
| codebase cognitive debt | когнитивен дълг към кодовата база | BG. |
| coding agent | кодиращ агент (coding agent) | BG. |
| commit | commit | EN. Verb: „направете commit“. |
| compaction | уплътняване на контекста (compaction) | BG. |
| compensation (saga) | компенсираща стъпка | BG. |
| confidence (score) | увереност | BG: „калибрирана увереност“. |
| conformity assessment | оценяване на съответствието | **official BG legal term** (AI Act). |
| confused deputy | confused deputy („объркан пълномощник“) | EN + gloss. |
| consent | съгласие | **official BG legal term** (GDPR). |
| content capture | записване на съдържанието (content capture) | BG + EN. |
| context engineering | инженеринг на контекста (context engineering) | BG + EN. |
| context rot | деградация на контекста (context rot) | BG + EN. |
| context window | контекстен прозорец | BG. |
| contextual retrieval | контекстуално извличане (contextual retrieval) | BG + EN. |
| continuous evaluation | непрекъснато оценяване | BG. |
| controller (GDPR) | администратор на лични данни | **official BG legal term** (GDPR). |
| cost per successful task (CPST) | цена на успешна задача (CPST) | BG; metric ID unchanged. |
| cost per task | цена на задача | BG. |
| counsel (legal) | юрист / правен съветник | BG. |
| critical infrastructure | критична инфраструктура | **official BG legal term**. |
| cross-encoder | cross-encoder (кръстосан енкодер) | EN. |
| custom agent | потребителски агент (custom agent) | BG + EN. |
| data flow diagram (DFD) | диаграма на потоците от данни (DFD) | BG. |
| data minimisation | свеждане на данните до минимум | **official BG legal term** (GDPR, чл. 5). |
| data protection officer | длъжностно лице по защита на данните (ДЛЗД) | **official BG legal term** (GDPR). Do not confuse with DPO (Direct Preference Optimization). |
| data residency | местоположение на данните (data residency) | BG + EN. |
| data subject | субект на данните | **official BG legal term** (GDPR). |
| deep fake | убедителен фалшификат | **official BG legal term** (AI Act, чл. 3, т. 60). |
| degradation ladder | стълбица на деградацията (degradation ladder) | BG + EN. |
| deploy (verb) / deployment (process) | разгръщам / разгръщане | BG. **Never „внедряване“** (rule 14). |
| deployer (AI Act) | внедрител | **official BG legal term** (AI Act, чл. 3, т. 4). |
| deployment (Foundry/Azure model deployment resource) | deployment (на модел) | EN resource name. |
| depot | депо | BG (Trakia domain); депото, депа. |
| design (architecture) | дизайн | BG: „системен дизайн“, „преглед на дизайна“. |
| dev / held-out split | работна (dev) / контролна (held-out) извадка | BG + EN. |
| devcontainer | devcontainer | EN. |
| diff / diff hunk | diff / част от diff (hunk) | EN. Not „фрагмент“ (reserved for chunk). |
| Digital Omnibus on AI | Цифровият омнибус за ИИ (Регламент (ЕС) 2026/1744) | Legal context; always cite the regulation number on first use. |
| dispatch / dispatcher / dispatch lead | диспечерска служба / диспечер / ръководител на диспечерите | BG (Trakia domain). |
| distillation | дестилация (distillation) | BG. „student/teacher model“ → „модел ученик / модел учител“. |
| distributor (AI Act) | дистрибутор | **official BG legal term**. |
| dogfooding | вътрешно ползване (dogfooding) | BG + EN. |
| DORA metrics | DORA метрики | Deployment frequency → „честота на разгръщане“; lead time for changes → „време за доставка на промени“; change failure rate → „дял на неуспешните промени“; failed-deployment recovery time → „време за възстановяване след неуспешно разгръщане“; rework rate → „дял на преработките“. |
| downstream provider | доставчик надолу по веригата | **official BG legal term** (AI Act, чл. 3, т. 68). |
| DPIA (data protection impact assessment) | оценка на въздействието върху защитата на данните (DPIA) | **official BG legal term** (GDPR, чл. 35). Short form „DPIA“ after first use. |
| DPO (Direct Preference Optimization) | DPO (Direct Preference Optimization) | EN; never „ДЛЗД“. |
| DR (disaster recovery) / DR by reconstruction | DR (възстановяване след бедствие) / DR чрез повторно изграждане | EN acronym + gloss. |
| drift | отклонение (drift) | BG. „architecture drift“ → „архитектурно отклонение“; „capability drift“ → „промяна във възможностите на модела“. |
| drill (DR) | учение (drill) | BG: „учение с измерено време“. |
| driver (truck) | шофьор | BG (Trakia domain). |
| dual LLM pattern | шаблон с два LLM (dual LLM pattern) | BG + EN. |
| durable (agents, execution) | устойчив (durable) | BG + EN. Names like Durable Task Scheduler unchanged. |
| egress | изходящ трафик (egress) | BG + EN. |
| embedding / embeddings | embedding / embeddings (векторно представяне) | EN; „моделът за embeddings“, „повторно генериране на embeddings“ (re-embedding). |
| emotion recognition system | система за разпознаване на емоции | **official BG legal term**. |
| endpoint | endpoint | EN; „project endpoint“ → „endpoint на проекта“. |
| error analysis | анализ на грешките | BG. |
| error budget | бюджет за грешки | BG. |
| eval / evals | eval / evals (автоматизирани оценки на качеството) | EN. „eval case“ → „тестов случай“; „eval suite“ → „набор от evals“; „hidden eval suite“ → „скрит набор от evals“; „eval gate“ → „eval гейт“; „eval report“ → „доклад от evals“. |
| evaluation | оценяване | BG (of a system). |
| evaluator | оценител (evaluator) | BG; `IEvaluator` unchanged. |
| execution accuracy (EX) | точност при изпълнение (EX) | BG; metric ID EX. |
| exfiltration | изнасяне на данни (exfiltration) | BG + EN. |
| fail closed / fail open | при отказ блокира (fail closed) / при отказ пропуска (fail open) | BG + EN. |
| failure mode | вид грешка (failure mode) | BG + EN. |
| fairness testing | тестване за справедливост | BG. „flag-rate parity“ → „паритет на дела на маркиранията“. |
| feature flag | feature flag | EN. |
| feature (product capability) | функционалност | BG. |
| few-shot prompting | few-shot промптинг (с няколко примера в промпта) | EN modifier + BG noun. |
| fine-tuning | fine-tuning (дообучаване) | EN. |
| first-pass acceptance | приемане от първия опит | BG. |
| fitness function | функция за пригодност (fitness function) | BG + EN. |
| fixture | fixture | EN (test). |
| flaky test | нестабилен тест (flaky) | BG + EN. |
| fork | fork | EN. |
| Foundry resource / project | ресурс на Foundry / проект във Foundry | BG + name. |
| function calling | извикване на функции (function calling) | BG + EN. |
| fundamental rights impact assessment | оценка на въздействието върху основните права | **official BG legal term** (AI Act, чл. 27). |
| gate stack | поредица от гейтове (gate stack) | BG + EN. |
| gate-sensitivity check | проверка на чувствителността на гейта | BG. |
| GDPR | GDPR (Общ регламент относно защитата на данните) | **official BG legal term** for the full name; abbreviation GDPR in prose. |
| GenAI semantic conventions (OpenTelemetry) | семантични конвенции за GenAI на OpenTelemetry | BG + name. |
| GenAIOps | GenAIOps | EN. |
| general-purpose AI model (GPAI model) | модел на ИИ с общо предназначение | **official BG legal term** (AI Act, чл. 3, т. 63). |
| general-purpose AI system | система с ИИ с общо предназначение | **official BG legal term** (AI Act, чл. 3, т. 66). |
| golden set / golden dataset | еталонен набор (golden set) | BG + EN. Folder `evals/golden/` unchanged. |
| go/no-go memo | бележка с решение „да/не“ (go/no-go) | BG + EN. |
| grader (course) | оценяващата система | BG. |
| grader (RFT) | grader (оценяваща функция) | EN. |
| groundedness / grounded / grounding | обоснованост (groundedness) / обоснован в източниците / обосноваване в източниците (grounding) | BG + EN. |
| guardrails | guardrails (защитни механизми) | EN. Foundry feature „Guardrails“ capitalised as in source. |
| hallucination | халюцинация | BG. |
| handoff | предаване (handoff) | BG. „human handoff“ → „предаване на човек“. |
| harmonised standard | хармонизиран стандарт | **official BG legal term**. |
| harness (test/eval) | тестова рамка (harness) | BG + EN. „sampling harness“ → „рамка за семплиране“. |
| high-risk AI system | високорискова система с ИИ | **official BG legal term** (AI Act, глава III). |
| HITL (human-in-the-loop) | човек в цикъла (human-in-the-loop, HITL) | BG + EN. „HITL approval“ → „HITL одобрение“. |
| honeypot items | контролни елементи-капани (honeypot) | BG + EN. |
| hooks | hooks (команди, изпълнявани при събития от жизнения цикъл на агента) | EN; „hook-ът“ not allowed. |
| hosted agent (Foundry) | хостван агент (hosted agent) | BG + EN. |
| human oversight | човешки надзор | **official BG legal term** (AI Act, чл. 14). |
| hybrid retrieval / hybrid search | хибридно извличане / хибридно търсене | BG. |
| IaC (infrastructure as code) | IaC (инфраструктура като код) | EN acronym + gloss. |
| idempotency key | ключ за идемпотентност | BG. |
| impact assessment (ISO/IEC 42005) | оценка на въздействието на ИИ | BG. |
| importer (AI Act) | вносител | **official BG legal term**. |
| index alias | alias на индекс | EN + BG. |
| indirect prompt injection | непряк prompt injection | BG adjective + EN term (м.р.). |
| inference | инференция | BG. |
| ingestion | зареждане на данни (ingestion) | BG + EN. |
| input data (AI Act) | входящи данни | **official BG legal term**. |
| instructions for use | инструкции за употреба | **official BG legal term** (AI Act). |
| intended purpose | предназначение | **official BG legal term** (AI Act, чл. 3, т. 12). |
| issue (GitHub) | issue | EN. „work item“ (Azure Boards) → „work item“. |
| jailbreak | jailbreak | EN. |
| judge (LLM-as-judge) | LLM съдия (LLM-as-judge) | BG; съдията, съдии. |
| kill switch | авариен изключвател (kill switch) | BG + EN. |
| knowledge base (Azure AI Search) | база от знания (knowledge base) | BG + EN. |
| KV cache | KV кеш | EN acronym + BG noun. |
| label / labeling (eval data) | етикет / етикетиране | BG. „human labels“ → „етикети, поставени от човек“. |
| landing zone | landing zone (базова среда в Azure с готово управление и мрежа) | EN. |
| latency | латентност | BG. „perceived latency“ → „възприемана латентност“. |
| lawful basis | правно основание за обработване | **official BG legal term** (GDPR, чл. 6). |
| least agency | минимална агентност (least agency) | BG + EN. |
| least operational responsibility | най-малка оперативна отговорност | BG. |
| least privilege | минимални привилегии (least privilege) | BG + EN. |
| legitimate interest | легитимен интерес | **official BG legal term** (GDPR). |
| lethal trifecta | смъртоносната тройка (lethal trifecta) | BG + EN. |
| LLM | LLM | EN; LLM-ът, LLM-и allowed. |
| lockfile | lockfile | EN. |
| logs (AI Act, automatically generated) | автоматично генерирани записи | **official BG legal term** (AI Act, чл. 19). Technical logs → „логове“. |
| LoRA (low-rank adaptation) | LoRA | EN. |
| lost in the middle | „изгубено в средата“ (lost in the middle) | BG + EN. |
| managed identity | управлявана самоличност (managed identity) | BG + EN (Microsoft BG localisation). |
| market surveillance authority | орган за надзор на пазара | **official BG legal term**. |
| MCP (Model Context Protocol) | MCP | EN. „MCP server/client/host“ → „MCP сървър/клиент/хост“. |
| memory (agent) | памет | BG. „session/episodic, semantic, procedural“ → „сесийна/епизодична, семантична, процедурна“. |
| memory poisoning | отравяне на паметта (memory poisoning) | BG + EN. |
| merge (Git) | сливане (merge); глагол „сливам“ | BG. „merged PR“ → „слят PR“. |
| middleware | middleware (междинен слой) | EN. |
| Mixture-of-Experts (MoE) | Mixture-of-Experts (MoE) | EN. |
| mock / fake / stub | mock / fake / stub | EN (test doubles). |
| model lifecycle | жизнен цикъл на модела | BG. |
| model migration | миграция на модел | BG. |
| model role | роля на модел (model role) | BG + EN. Role IDs `chat-fast` unchanged. |
| multi-tenant | многотенантен | BG. |
| mutant / mutation score | мутант / мутационен резултат (mutation score) | BG. „killed / survived“ → „убит / оцелял“. |
| mutation testing | мутационно тестване | BG. |
| nondeterminism | недетерминизъм | BG. |
| notified body | нотифициран орган | **official BG legal term**. |
| OBO (on-behalf-of) | OBO (on-behalf-of) | EN. |
| observability | наблюдаемост (observability) | BG + EN. |
| on-call | дежурство (on-call) | BG. |
| open coding | отворено кодиране (open coding) | BG + EN. |
| operator (AI Act) | оператор | **official BG legal term**. |
| orchestration / orchestrator | оркестрация / оркестратор | BG. |
| output (model) | изход | BG. „output tokens“ → „изходни токени“. |
| pairwise judge | съдия за сравнение по двойки (pairwise judge) | BG + EN. „position bias“ → „пристрастие към позицията“. |
| PAYG (pay-as-you-go) | PAYG (плащане при ползване) | EN acronym + gloss. |
| peer review | преглед от колеги | BG. |
| permission-aware | съобразен с правата на достъп | BG. |
| personal data | лични данни | **official BG legal term**. |
| pipeline | pipeline | EN. |
| placing on the market | пускане на пазара | **official BG legal term** (AI Act, чл. 3, т. 9). |
| plan mode | plan mode (режим на планиране) | EN feature name. |
| plan-then-execute | „първо план, после изпълнение“ (plan-then-execute) | BG + EN. |
| post-market monitoring | мониторинг след пускането на пазара | **official BG legal term** (AI Act). |
| postmortem / blameless postmortem | постмортем / постмортем без търсене на виновни | BG; постмортемът. |
| PR (pull request) | PR (pull request) | EN; PR-ът, PR-а, PR-и allowed. |
| procedural memory | процедурна памет | BG. |
| processor (GDPR) | обработващ лични данни | **official BG legal term** (GDPR). |
| production | продукция; „в продукция“ | BG. „production-grade“ → „готов за продукция“. |
| production-readiness review (PRR) | преглед за готовност за продукция (PRR) | BG + acronym. |
| profiling | профилиране | **official BG legal term** (GDPR / AI Act). |
| progressive disclosure | постепенно разкриване (progressive disclosure) | BG + EN. |
| prohibited AI practices | забранени практики в областта на ИИ | **official BG legal term** (AI Act, глава II). |
| prompt / prompting | промпт / промптинг | BG; промптът, промптове. Exception: the security term „prompt injection“ stays EN. |
| prompt caching | кеширане на промпта (prompt caching) | BG + EN. |
| prompt injection | prompt injection (вмъкване на инструкции) | EN, fixed security term. |
| prompts as code | промптове като код | BG. |
| property-based testing | тестване, базирано на свойства (property-based testing) | BG + EN. |
| protected paths | защитени пътища (protected paths) | BG + EN. |
| provider (AI Act) | доставчик | **official BG legal term** (AI Act, чл. 3, т. 3). |
| provider (model/cloud) | доставчик (на модели) | BG; same word, context differs. |
| pseudonymisation / pseudonymised | псевдонимизация / псевдонимизирани | **official BG legal term** (GDPR). |
| PTU (provisioned throughput units) | PTU (резервиран капацитет) | EN acronym + gloss. |
| putting into service | пускане в действие | **official BG legal term** (AI Act, чл. 3, т. 11). |
| qrels | qrels (оценки за релевантност) | EN. |
| quality management system | система за управление на качеството | **official BG legal term** (AI Act). |
| query | заявка | BG. „query planning / rewriting“ → „планиране / пренаписване на заявки“. |
| RAG (retrieval-augmented generation) | RAG (генериране, допълнено с извличане) | EN. |
| rate limit / throttling | лимит на заявките (rate limit) / ограничаване на заявките (throttling) | BG + EN. |
| reasonably foreseeable misuse | разумно предвидима неправилна експлоатация | **official BG legal term** (AI Act, чл. 3, т. 13). |
| reasoning effort | усилие за разсъждение (reasoning effort) | BG + EN; parameter value in code unchanged. |
| reasoning model | модел с разсъждение (reasoning model) | BG + EN. |
| recall@k / recall / precision | recall@k / recall (пълнота) / precision (прецизност) | EN metric names + gloss. |
| red team / red teaming | red team / red teaming (атакуващо тестване) | EN. |
| redaction | маскиране (redaction) | BG + EN. |
| red-team swap | размяна за red teaming (red-team swap) | Capstone milestone. |
| regulatory sandbox (AI) | регулаторна лаборатория в областта на ИИ | **official BG legal term** (AI Act, чл. 3, т. 55). |
| release | версия / пускане | BG. „per release“ → „за всяка версия“. |
| reranker / reranking | reranker (модел за повторно класиране) / повторно класиране | EN / BG. |
| retention | срок на съхранение | BG. |
| retrieval | извличане (retrieval) | BG + EN. |
| retry | повторен опит (retry) | BG + EN. |
| RFT / SFT / DPO | unchanged | EN acronyms. |
| risk (AI Act) | риск | **official BG legal term**. |
| risk file (AI Act) | досие за риска (risk file) | BG + EN; course artefact. |
| risk management system | система за управление на риска | **official BG legal term** (AI Act, чл. 9). |
| RLS (row-level security) | RLS (сигурност на ниво ред) | EN acronym + gloss. |
| ROI | ROI (възвръщаемост на инвестицията) | EN acronym + gloss. |
| rollback | rollback (връщане към предишна версия) | EN. Verb: „върнете предишната версия“. |
| rollout | поетапно пускане (rollout) | BG + EN. |
| RRF (reciprocal rank fusion) | RRF (reciprocal rank fusion) | EN. |
| rubric | рубрика за оценяване | BG. |
| rug pull | rug pull (подмяна на инструмент след одобрение) | EN. |
| Rule of Two | Rule of Two („правилото на двете“) | EN + gloss. |
| runbook | runbook (оперативна инструкция) | EN. |
| saga | сага (saga) | BG. |
| sampling (decoding) | семплиране | BG. |
| sampling (traffic, traces) | извадка / вземане на извадка | BG. „tail sampling“ stays EN. |
| sandbox | sandbox | EN; „в sandbox“. AI Act regulatory sandbox: see that row. |
| security trimming | филтриране по права на достъп (security trimming) | BG + EN. |
| semantic cache | семантичен кеш | BG. |
| semantic layer | семантичен слой | BG. |
| serious incident | сериозен инцидент | **official BG legal term** (AI Act, чл. 73). |
| shadow deployment | shadow разгръщане (без показване на резултата на потребителите) | EN + BG. |
| ship / shipping | пускам / пускане (в продукция) | BG. |
| showback | showback (показване на разходите по звена без префактуриране) | EN. |
| skill (Agent Skills) | skill (пакет с процедурни знания за агента) | EN. |
| SLO / SLI | SLO / SLI | EN; SLO-то allowed. |
| slopsquatting | slopsquatting | EN + one-line explanation on first use. |
| span | span | EN. |
| spec / spec-driven development | спецификация / разработка, водена от спецификации (spec-driven development) | BG. `SPEC.md` unchanged. |
| special categories of personal data | специални категории лични данни | **official BG legal term** (GDPR, чл. 9). |
| spillover | преливане (spillover) | BG + EN. |
| sponsor (human) | спонсор (отговорно лице) | BG. |
| spotlighting | spotlighting (маркиране на недовереното съдържание) | EN. |
| stakeholder | заинтересована страна | BG. |
| streaming | стрийминг | BG. |
| STRIDE | STRIDE | Category names stay EN: Spoofing, Tampering… |
| structured outputs | структуриран изход (structured outputs) | BG + EN. |
| sub-agent | подагент | BG. |
| substantial modification | съществено изменение | **official BG legal term** (AI Act, чл. 3, т. 23). |
| supervisory authority (GDPR) | надзорен орган | **official BG legal term**. |
| synthetic content (AI Act Art. 50) | синтетично съдържание | Legal context. |
| synthetic data | синтетични данни | BG. „dimension tuples“ → „кортежи от измерения“. |
| system card | системна карта (system card) | BG + EN. |
| system prompt | системен промпт | BG. |
| systemic risk | системен риск | **official BG legal term** (AI Act, чл. 3, т. 65). |
| tag (Git) | таг | BG; тагът. Tag names in backticks. |
| technical documentation | техническа документация | **official BG legal term** (AI Act, чл. 11). |
| temperature | температура | BG; parameter in code unchanged. |
| tenant | тенант | BG; тенантът, тенанти. |
| test-driven development (TDD) | TDD (разработка, водена от тестове) | EN acronym + gloss. |
| testing data (AI Act) | изпитвателни данни | **official BG legal term**. |
| testing in real-world conditions | изпитване в реални условия | **official BG legal term**. |
| text-to-SQL | text-to-SQL | EN. |
| threat register / threat model / threat modelling | регистър на заплахите / модел на заплахите / моделиране на заплахите | BG. |
| throughput | пропускателна способност | BG. |
| token | токен | BG; токенът, 100 токена. |
| tool | инструмент | BG. „tool definition / schema / result“ → „дефиниция / схема / резултат на инструмента“. |
| tool calling | извикване на инструменти (tool calling) | BG + EN. |
| tool definition pinning | фиксиране на дефинициите на инструментите (pinning) | BG + EN. |
| tool poisoning | отравяне на инструменти (tool poisoning) | BG + EN. |
| top-p | top-p (nucleus sampling) | EN. |
| TPM (tokens per minute) | TPM (токени в минута) | EN acronym + gloss. |
| trace | trace | EN; „този trace“, „100 traces“. |
| tracing | проследяване (tracing) | BG + EN. |
| track-critical area | ключова за специализацията област | BG. |
| training data (AI Act) | обучителни данни | **official BG legal term**. |
| trajectory / trajectory eval | траектория / оценка на траекторията (trajectory eval) | BG. |
| Transparency Note | Transparency Note (документ за прозрачност) | Microsoft document type; EN + gloss. |
| TTFT (time to first token) | TTFT (време до първия токен) | EN acronym + gloss. |
| turn (conversation) | ход (в разговора) | BG. |
| untrusted content / input | недоверено съдържание / недоверен вход | BG. |
| use case | сценарий на употреба (use case) | BG + EN. |
| validation data (AI Act) | валидационни данни | **official BG legal term**. |
| vehicle / fleet / trip / shipment | превозно средство / автопарк / курс / пратка | BG (Trakia domain). |
| version pinning | фиксиране на версията (pinning) | BG + EN. |
| WAF (Well-Architected Framework) | Azure Well-Architected Framework (WAF) | name. Watch for collision with WAF = Web Application Firewall → „WAF (защитна стена за уеб приложения)“. |
| work order | работна поръчка | BG (Trakia domain). Azure Boards „work item“ stays EN. |
| workers' representatives | представители на работниците | **official BG legal term** (AI Act, чл. 26). |
| workflow | workflow (работен поток с предварително зададени стъпки) | EN. GitHub Actions workflow also „workflow“. |
| worktree | worktree | EN. |


### Names and identifiers from the glossary (keep exactly as in the source)

These glossary headwords are names (rule 24), metrics (rule 26) or code (rule 20). Do not translate them; add only the Bulgarian gloss shown, on first use per chapter.

- `410 Gone` (HTTP статус, винаги в backticks)
- A2A (Agent2Agent), Agent Card · AG-UI · MCP, MCP Apps, MCP 2026-07-28 („ревизия с несъвместими промени“ for *breaking revision*)
- Agent Skills (`SKILL.md`) · `AGENTS.md` · `CLAUDE.md` · `.github/copilot-instructions.md`
- AI Red Teaming Agent · PyRIT (orchestrators, converters, scorers stay EN) · Azure SRE Agent (режим Reader / Privileged)
- Aspire (AppHost, ServiceDefaults; *dashboard* → „таблото на Aspire“) · `azd` (Azure Developer CLI)
- Microsoft Agent Framework (MAF; *graph workflows* → „графови workflows“) · MEAI (`Microsoft.Extensions.AI`) · MEVD (`Microsoft.Extensions.VectorData`) · `Microsoft.Extensions.AI.Evaluation` · `IChatClient` · `ChatClientBuilder` · `IEvaluator`
- Microsoft Foundry · Foundry Agent Service · Foundry IQ · Foundry Local · Model router · Data Zone (EU) deployment · Responses API · Assistants API
- GitHub Copilot, its cloud agent (cloud agent на GitHub Copilot) · GitHub Copilot SDK (*bring-your-own-key* → „собствен ключ (BYOK)“) · Copilot Studio · Claude Code · Claude Agent SDK
- Content Safety · Prompt Shields · Content Understanding · Entra Agent ID · Voice Live · Azure AI Search *semantic ranker* · `VECTOR` / `VECTOR_DISTANCE` (SQL Server 2025)
- Playwright test agents (planner, generator, healer → „тестовите агенти на Playwright“) · Stryker.NET · FsCheck · CsCheck
- GraphRAG · LazyGraphRAG · τ-bench · τ²-bench · C4 model (моделът C4) · Structurizr DSL
- `allowed_groups` / `allowedGroups` (филтър `allowed_groups`) · `llm-token-limit` / `llm-emit-token-metric` / `llm-semantic-cache-*` (политики на AI gateway в APIM)
- OpenTelemetry (OTel) · `gen_ai.*` · OWASP Top 10 for LLM Applications · OWASP Top 10 for Agentic Applications (risk IDs LLM01–LLM10, ASI01–ASI10; translate the risk descriptions, e.g. *agent goal hijack* → „отвличане на целта на агента“)
- ISO/IEC 42001, 23894, 42005 (*certifiable* → „подлежащ на сертифициране“) · NIST AI RMF (Govern, Map, Measure, Manage) · JSON Schema · KQL
- Fleet Ops Copilot · Fleet Assistant · Fleet Analyst · Trakia Freight · TrakiaOps · TrakiaBench · TrakiaSim (never „Тракия“)
- Identifiers: C0–C19, D1–D7, A1–A7, G1–G3, K1–K12 (Latin letters only)
- Metrics: BM25 · recall@k · nDCG@k (нормализирана дисконтирана кумулативна печалба) · pass@k · pass^k · TPR / TNR (дял на верните положителни / верните отрицателни резултати) · McNemar's test → „тест на McNemar“ (*discordant pairs* → „несъвпадащи двойки“)

---

## 4. Pre-delivery checklist (per file)

1. Code blocks and inline code identical to source (`diff` the fenced blocks).
2. Heading count, table column counts and list structure match the source.
3. Module section headings and lab labels match section 1.6 character for character.
4. No Cyrillic look-alike letters in IDs (C0–C19, D1–D7, A1–A7, G1–G3, K1–K12, ADR-0012).
5. All link targets unchanged; all link texts translated.
6. Quotes are „…“; decimal commas outside code; dates in „9 април 2026 г.“ form.
7. First-use glosses present once per chapter, not repeated.
8. No „внедряване“ for software deploys; AI Act and GDPR terms match the table verbatim.
9. „вие“ lowercase throughout; imperatives in the plural form.

## 5. Addendum — decisions made during translation (binding for all further files)

| English | Bulgarian usage | Note |
|---|---|---|
| brief (gate / client brief) | задание; client brief → задание от клиент | |
| candidate (in gates) | кандидат | |
| board / review board | комисия; first mention „комисия за преглед (review board)“ | |
| assessors | изпитващи | |
| reference solution | референтно решение | |
| floor (threshold) | долна граница | |
| pinned (model, judge, version) | фиксиран | |
| stratum / strata / stratified | страта / страти / стратифициран | |
| remediation / remediation plan | наваксване / план за наваксване | not „отстраняване на пропуските“ |
| resit / retake | повторно явяване | |
| time box | времева рамка | |
| root cause | първопричина | |
| happy path | основният успешен сценарий (happy path) | |
| debug | дебъгване | |
| baseline (system/code) | изходна версия | metric baseline → базова стойност |
| mastery learning / mastery gates | обучение до пълно усвояване (mastery learning) / гейтове за пълно усвояване | |
| scaffolding | опора (scaffolding) | |
| integrity (academic) | почтеност | |
| evidence pack | пакет с доказателства | |
| elicitation (requirements) | изясняване на изискванията | not „извличане“ (= retrieval) |
| inception (phase) | началната фаза (inception) | |
| spike | кратко проучване (spike) | |
| bake-off | сравнително изпитване (bake-off) | |
| agent harness | harness за агенти; plural harness-и | test/eval harness → тестова рамка |
| plugin(s) | плъгин / плъгини | |
| concept session | занятие по концепциите | |
| office hours | консултации | |
| part-time / full-time pacing | при непълно / пълно натоварване | |
| course-designer estimate | оценка на авторите на курса | |
| seniority | сениор ниво | |
| delivery notes | товарителници | |
| cloud agent (generic) | облачен агент; Copilot feature: cloud agent на Copilot | |
| Developer / Architect (role labels) | keep English | |
| K-areas | K1 Основи на AI · K2 Промптинг и структуриран вход/изход · K3 Извличане и знания · K4 Инструменти и MCP · K5 Агенти и оркестрация · K6 Контекст и памет · K7 Оценяване · K8 Тестване и автоматизация на SDLC · K9 Експлоатация, наблюдаемост и разходи · K10 Сигурност · K11 Отговорен AI и управление · K12 Архитектура и бизнес | |
| predict → run → explain | прогнозирай → изпълни → обясни | |
| plan → implement → verify | планирай → реализирай → провери | |
