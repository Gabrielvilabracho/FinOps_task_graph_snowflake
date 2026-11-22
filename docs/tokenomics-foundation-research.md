# Tokenomics Foundation Research for Snowflake FinOps

Research cutoff: **November 22, 2026**. Status: **documentary synthesis and implementation-gap analysis—not a runtime specification, adopted standard, or proof of financial results**.

The Tokenomics Foundation publishes a connected body of work about AI production, consumption, and value. Its strongest contribution is not a single KPI or schema. It is the insistence that AI economics must connect technical consumption to accountable tasks, quality-qualified outcomes, and finance-approved value claims without hiding failed work or double counting benefits.

For this repository, the conclusion is deliberately bounded: existing Snowflake credit and service evidence can support part of the **cost and consumption** layer, but it cannot establish full Total Cost of AI (TCA), task quality, business outcomes, realized value, or ROI. Those claims require additional telemetry, organizational policy, contractual cost evidence, and business attestation.

## Quick reading path

| Reader question | Start here |
|---|---|
| What did the research cover? | [Method and evidence boundary](#method-and-evidence-boundary), then [Project inventory](#project-inventory) |
| How do production and consumption fit together? | [Production and consumption model](#production-and-consumption-model) |
| How should cost connect to outcomes and value? | [Value attribution architecture](#value-attribution-architecture) |
| What can this Snowflake project support today? | [Repository fit and evidence gaps](#repository-fit-and-evidence-gaps) |
| What should maintainers do next? | [Recommended documentary and implementation sequence](#recommended-documentary-and-implementation-sequence) |
| Which source versions and limitations apply? | [Source ledger](#source-ledger) |

## Executive findings

1. **Production, consumption, and value are different evidence domains.** The Seven-Layer Stack maps production dependencies and control points; Big-T describes informal consumption-scaling behavior; VADA and Value Classification propose how tasks, outcomes, costs, and value claims could be linked. None can substitute for the others.
2. **Optimization must preserve a quality floor.** Lower token counts, cheaper models, cache hits, faster delivery, and released developer time are not benefits when quality, policy compliance, or downstream outcomes degrade.
3. **Failed and unattributed work remain economically visible.** Retries, discarded output, failed tasks, and unresolved linkage stay in cost numerators. Missing attribution is not zero cost and is not automatically the same as failed work.
4. **TCA is wider than provider tokens or Snowflake credits.** Depending on the declared boundary, it can include capacity, supporting infrastructure, platform labor, product-team labor, evaluation, audit, human review, external services, and idle commitments.
5. **Value requires settlement and attestation.** Estimated value is not realized value. Freed hours become realized benefit only when redeployed into evidenced output or an approved budget is actually removed or avoided under a defined accounting policy.
6. **Published maturity varies materially.** Some resources are release candidates, some are working-group drafts, and VADA is an early architecture draft. Future-dated index entries relative to the research cutoff are preserved as discrepancies rather than treated as completed releases.
7. **This repository is a bounded evidence producer.** It currently observes selected Snowflake costs and service usage with explicit coverage limitations. It does not implement enterprise-wide task/outcome/value attribution, full FOCUS 1.5 conformance, or validated ROI.

## Method and evidence boundary

Research began with the Foundation's public [Projects index](https://www.tokeneconomics.com/projects/) and then inspected the substantive project pages and available primary artifacts for all 12 indexed entries. The [Working Groups](https://www.tokeneconomics.com/about/tokenomics-working-groups/) and [Technical Steering Committee](https://www.tokeneconomics.com/about/technical-steering-committee/) pages supplied governance context. The [FinOps Foundation attribution guidance](https://www.finops.org/introduction/how-to-use/) supplied the licensing and adaptation boundary.

Coverage labels mean:

- **FULL:** the returned substantive page text was read through its relevant sections. It does not mean every linked paper, image, dataset, simulator, or external citation was independently validated.
- **PARTIAL:** only a bounded portion, selected entries, abstract, HTML metadata, or supporting artifact could be inspected.
- **UNAVAILABLE:** the artifact was discoverable but could not be substantively decoded or accessed through the available research path.

Foundation pages are primary evidence for **what the Foundation proposes or reports**. They are not independent evidence that example savings reproduce, vendor behavior remains current, survey correlations are causal, or this repository implements the proposal. Underlying provider documentation, contracts, account behavior, and business records need separate verification.

The cutoff matters. The Projects index displayed VADA as **November 23, 2026** and FOCUS 1.5 as **December 2026**, both later than the November 22 snapshot. Those entries are documented as accessible, future-dated materials—not normalized into completed releases as of the cutoff.

## Project inventory

| # | Indexed project | Published status/date evidence | Coverage | Admission verdict |
|---:|---|---|---|---|
| 1 | [The Seven-Layer Tokenomics Stack](https://www.tokeneconomics.com/projects/the-seven-layer-tokenomics-stack/) | Index RC, August 4; companion paper metadata October 14–17 | FULL | Production dependency and measurement framework; not evidence of control over every managed-service layer. |
| 2 | [Big-T Notation](https://www.tokeneconomics.com/projects/big-t-notation/) | Published August 1; modified August 27 | FULL | Informal scaling vocabulary, not formal complexity proof or a savings forecast. |
| 3 | [Big-T Notation Paper](https://www.tokeneconomics.com/projects/big-t-notation-paper/) | Index “Full Paper,” August 1; page metadata July 28–October 16 | FULL HTML | Detailed token-efficiency framework; no separate PDF was inspected. |
| 4 | [The cache is a prefix, not a memory](https://www.tokeneconomics.com/cache-explainer/) | RC1, updated September 22 | FULL text | Cache taxonomy and economics; simulator was not executed and provider snapshot was not independently verified. |
| 5 | [AI Tokenomics Personas and Operating Model](https://www.tokeneconomics.com/personas-and-operating-model-map/) | RC2, updated September 4; index September 5 | FULL | Responsibility archetypes and illustrative RACI, not mandatory organization design. |
| 6 | [AI Tokenomics Mind Map](https://www.tokeneconomics.com/ai-tokenomics-mind-map/) | Index Draft, August 5; wrapper modified November 17 | PARTIAL | Production/consumption YAML and repository metadata inspected; viewer not executed and Value branch excluded from delegated scope. |
| 7 | [Terminology](https://www.tokeneconomics.com/projects/terminology-kpis/) | Index RC, October 30; body WG draft; data v0.0.3 | PARTIAL | Selected definitions and KPIs inspected; not all 827 terms, 94 KPIs, or linked papers. |
| 8 | [Value Attribution Data Architecture](https://www.tokeneconomics.com/projects/value-attribution-data-architecture/) | v0.2, index/body November 23; early draft | FULL text | Detailed proposed contracts and KPIs; no executable reference implementation. Future-dated relative to cutoff. |
| 9 | [Measuring AI Value in Software Engineering](https://www.tokeneconomics.com/projects/measuring-ai-value-in-software-engineering/) | RC1, updated November 19; index November 18 | FULL page / PARTIAL citations | Measurement approach inspected; selected underlying studies checked, not the entire citation corpus. |
| 10 | [AI Value Classification](https://www.tokeneconomics.com/ai-value-classification/) | RC3, updated November 17; index September 16 | FULL | Four-step value method and worked illustration; not an adopted accounting policy. |
| 11 | [What FOCUS 1.5 Does for AI Cost—and What It Does Not](https://www.tokeneconomics.com/projects/what-1-5-does-for-ai-cost-and-what-it-does-not/) | Updated November; describes December ratification/announcement | FULL explainer / PARTIAL release audit | Candidate-recommendation analysis, not ratified FOCUS 1.5 as of cutoff. |
| 12 | [State of Tokenomics](https://www.tokeneconomics.com/state-of-tokenomics/) | RC1.0, September 23; HTML modified November 4 | PARTIAL | Public results inspected; methods/raw data unavailable on the page and PDF could not be substantively decoded. |

## Production and consumption model

### Seven layers are a control and dependency map

The Seven-Layer Stack separates where AI economics originate and where different actors can intervene:

| Layer | Economic decisions | Representative measures |
|---|---|---|
| **L0 Energy** | Power price/capacity, water, carbon accounting, time shifting | Energy per token or completion, PUE, WUE |
| **L1 Physical infrastructure** | Accelerator, memory, interconnect, cooling, density, region | Cost per million tokens, tokens/second/accelerator, performance/watt |
| **L2 Infrastructure management** | Scheduling, queues, autoscaling, shared pools, quotas | Productive versus idle hours, commitment use, queue time |
| **L3 Inference stack** | Engines, batching, KV/prefix caches, tools, runtime safety, iteration | Time to first token, inter-token latency, throughput, cache reuse, percentiles |
| **L4 Model management and selection** | Provider/model/version, runtime configuration, precision, adapted weights | Cost per task/outcome, quality per dollar, memory use, regressions |
| **L5 AI access and control** | Admission, identity, proxy/router, budgets, retry/fan-out bounds | Cost by route/team/tenant, model mix, budget burn, step counts |
| **L6 Demand and entry points** | Human/application/agent demand, context, frequency, concurrency | Sessions, context volume, workload and owner traceability |

Governance, identity, observability, security, and cost management cut across the stack. L6 identifies the use case and beneficiary; L5 validates and propagates that identity into controlled execution. Measurements reveal drift, but workload owners decide whether consumption is justified by outcomes.

The key boundary for this repository is **influence versus ownership**. A managed Snowflake consumer can choose workloads, models exposed by the platform, request patterns, some routing or quota controls, and account-level policies. It does not therefore own facility power contracts, accelerator scheduling, KV-cache implementation, quantization, or the inference engine. The stack should guide dependency analysis and evidence requests, not imply unavailable control.

### Big-T is informal scaling notation

Big-T uses `T(n·k·a)` as an explanatory model:

- `n`: requests and/or input size; the source uses this ambiguously, so any application must define the scaling dimension.
- `k`: model calls, reasoning loops, repeated context, or other per-task multiplication.
- `a`: agent depth or delegation multiplication.

The ladder ranges from `T(1)` precomputed/no-per-request inference through slowly growing retrieval contexts, linear demand, hidden loops, agent multiplication, and `T(∞)` behavior without termination ceilings. The authors explicitly reject formal proofs and exact token prediction. A comparison is meaningful only when workload, scaling dimension, and quality floor remain fixed.

Five proposed levers are model routing, prompt/serialization design, caching, abstraction transparency, and workload governance. The reference pipeline uses deterministic preprocessing, cache checks, routing, prompt architecture, inference, and output-mode selection, wrapped by telemetry, attribution, circuit breakers, and budgets.

The published ten-paper example moves from **$3.04 to $0.65 to $0.13 to $0.09** and reports approximately 34× savings. This is an illustrative source result, not a forecast for this repository: no reproducibility dataset was inspected, and filtering, batch reduction, serialization, quality, and downstream execution assumptions remain workload-specific.

Several source tensions must remain visible:

- A semantic response-cache hit can bypass inference; prefix-cache reuse generally preserves generation while reusing attention state. They are not equivalent.
- Cheaper routing changes cost per unit unless it also demonstrably changes calls, context, or scaling behavior.
- The explainer says an assessment worksheet is “Coming soon,” while the paper calls it published. The seven assessment areas were readable, but no complete scored worksheet was inspected.
- Generated code may move work from model inference into execution and external APIs. That can change the cost location without eliminating cost.

### Cache economics require denominators

The cache explainer distinguishes KV state, prefix reuse, provider prompt caching, and semantic answer reuse. A practical prompt layout places stable content first, growing shared content next, and per-request content last. Exact-prefix changes, minimum cache blocks, expiration, model/version binding, hidden harness prefixes, and routing locality can all reduce reuse.

For cache-read tokens `R`, cache-write tokens `W`, uncached input tokens `U`, and applicable input price `p`:

```text
Token-weighted hit rate = R / (R + W + U)

Uncached-equivalent input cost = (R + W + U) × p

Cache cost efficiency =
    1 − actual prompt cost / uncached-equivalent input cost
```

The glossary also proposes `R/W` as a reuse ratio. A break-even ratio depends on actual write and read price multipliers; the published 1.25× write and 0.1× read example yields roughly 0.28, but those coefficients are not universal prices.

Metrics must be segmented by workload, window, model/version, and contract. Aggregate underlying token and cost numerators and denominators rather than averaging percentages. Input-side cache savings do not settle output charges, commitments, subscription fees, storage/token-hour costs, routing fragmentation, or quality risk.

### Operating model means accountable roles, not mandatory hires

The operating-model project describes eight archetypes: Engineering, FinOps Practitioner, AI End User, Finance, Product, Procurement, Leadership, and Capacity. Individuals can span several archetypes, and Capacity itself can span functions. Security/Compliance, Legal, Sustainability, and IT asset/financial management are allied responsibilities.

The proposed accountability pattern is useful because it prevents cost dashboards from silently owning business decisions:

| Decision | Responsible | Accountable |
|---|---|---|
| Platform architecture, routing, and caching | Engineering | Engineering |
| Model selection and replacement | Engineering | Product |
| Cost attribution, budgets, and forecasts | FinOps | Finance |
| Cost anomalies | FinOps | FinOps |
| Service incidents | Engineering | Engineering |
| Quality and use-case fit | Product | Product |
| Value measurement | Finance | Finance |
| Policy | FinOps | Leadership |
| Sourcing and commitments | Procurement | Procurement |
| Capacity and power strategy | Capacity | Leadership |

This is a starting RACI, not an instruction to create eight job positions. Re-prompts, corrections, discarded outputs, shadow usage, and off-platform work are operational signals. Example token shares, model-cost multiples, and savings are external assertions rather than enterprise accounting coefficients.

## Value attribution architecture

### TCA establishes the cost boundary before ROI

The Foundation's [Total Cost of AI guidance](https://www.tokeneconomics.com/insights/total-cost-of-ai/) separates two costing steps. First, establish a fully loaded rate for each delivery path using compatible units and an explicit period. The five described cost pools are direct consumption/capacity, shared infrastructure, platform labor, platform-provision costs, and idle/committed waste. Second, assign those rates to product runtime, build-and-maintain activity, and team agents/assistants, then add product-specific costs.

```text
Fully loaded path rate =
    cost assigned to one path and period
    / compatible delivered units

Product TCA =
    Σ(path rate × product usage by consumption driver)
    + product-specific costs
```

Mixed token, seat, accelerator, and labor units must not be divided by an undefined composite denominator. Platform labor belongs in the shared path rate; product delivery labor belongs in product-specific cost. The allocation handoff must preserve lineage so the same invoice, amortized cost, and product allocation are not counted as independent costs.

The practical starting point is one delivery path, one rate card, and one product. Snowflake credits can be one input to that exercise, but a single-account credit view remains **bounded account/workload economics** unless labor, external APIs/SaaS, shared platforms, commercial rates, and business outcomes are included or explicitly excluded.

### VADA proposes four linked evidence domains

VADA v0.2 proposes `CostAndUsage`, `Telemetry`, `Task`, `Outcome`, and `Value` contracts. Its central design concern is grain discipline:

- `CostAndUsage`: one row per charge, usually hourly or daily. `BilledCost` is invoiced spend; `EffectiveCost` is the amortized allocation numerator.
- `Telemetry`: consumption scope × `WorkloadId` × `TaskId` × aligned UTC window. Deep spans are aggregated separately for each scope.
- `Task`: linked through `(WorkloadId, TaskId)` and able to reference an upstream outcome for multi-stage lineage.
- `Outcome`: identified by `WorkloadId + OutcomeId + OutcomeEntryNumber`. Ledger entries must be aggregated before joins to avoid measure multiplication.
- `Value`: stakeholder claims identified by `ValueClaimId`, with workload/outcome, value period, basis, and attestation. Alternative stakeholder valuations are lenses, not additive amounts.

Cost and telemetry are many-to-many because several priced charge rows can cover the same activity. The draft allocates scope/window EffectiveCost by an activity weight:

```text
Allocated cost =
    row ActivityWeight × scope/window EffectiveCost
    / total scope/window ActivityWeight
```

Weights must reflect differently priced usage. Published output-token and cache-read multipliers are illustrations, not prescribed coefficients. Allocation method, idle-capacity handling, zero-weight scopes, unmatched billing, late corrections, and rounding reconciliation remain incomplete organizational or implementation decisions.

VADA's conservation promise is narrower than enterprise TCA: it applies to cost matched to telemetry. Seats, support, labor, and charges without telemetry are not automatically reconciled. Proposed `AllocationBasis`, `OVERHEAD`, and internal-labor extensions are not part of the represented schema.

### Missing linkage, time, and quality are first-class states

Unresolved task or outcome identifiers become `'UNLINKED'`, not `NULL`. Their cost remains visible and the unlinked share is reported separately. This prevents missing attribution from disappearing, but it also means unlinked work should not be silently equated with failed work. `NON_PRODUCTION_OVERHEAD` distinguishes planned evaluation, indexing, and similar activity from production scrap.

Billing and telemetry windows use UTC half-open intervals: `[start, end)`. Tasks may cross periods; late linkage is allowed; and cohort and atomic modes provide different attribution resolutions. The draft does not declare one as a mandatory maturity stage or provide a complete correlation algorithm.

Two quality gates separate technical task completion from durable outcome survival:

1. `TaskQualityBarMet`: technical inspection and policy compliance.
2. `OutcomeQualityBarMet`: the delivered result survives its agreed SLA or settlement window.

Business owners define settlement by outcome type. Pending evidence can change; settled evidence freezes. Later reversals become signed amendments rather than silent history rewrites. `RealizedValue` remains `NULL` before settlement; `EstimatedValue` covers in-flight worth; `PlannedValue` preserves the originally approved figure. Booked claims require claimant/attestor separation, cutoff time, and supporting evidence when the Outcome record alone is insufficient.

### Value Classification prevents automatic dollarization

The four steps are **Observe, Net, Convert, Book**:

1. **Observe:** compare the same period, work mix, unit, and quality floor. Record whether evidence is measured, sampled, or estimated.
2. **Net:** subtract failed output, created rework, review burden, and harm using compatible units.
3. **Convert:** apply documented conversion hops to net evidence and carry uncertainty forward.
4. **Book:** recognize only what meets Finance-approved evidence and destination rules.

Three conversion hops are an illustrative reporting threshold, not a standard. Hours can remain hours; they do not need forced dollar conversion. Freed labor that is not redeployed creates **zero realized benefit**. Revenue won, revenue retained, spend removed, spend avoided, and capital freed are different destinations. Spend avoided is generally a budget-variance claim rather than a ledger entry; it becomes realized only when an approved budget is actually reduced.

The software-engineering illustration reports review time falling from 45 minutes to 10 minutes plus 8 minutes of triage, yielding 27 minutes net per review and about 90 hours across 200 weekly pull requests. That is an illustration, not a case study. It assumes review is the bottleneck and a backlog absorbs capacity. Avoided contractors require an approved hiring plan and returned budget. Capacity and avoided spend cannot both be booked for the same benefit.

### Proposed KPI meanings

| KPI | Proposed meaning | Critical boundary |
|---|---|---|
| Scrap Rate | Unlinked and failed-task cost ÷ workload EffectiveCost | Missing attribution and failure should remain distinguishable in detail. |
| Cost per Quality Outcome | All workload cost, including failures and unlinked activity, ÷ net qualified outcomes | Requires a fixed outcome unit and quality bar. |
| Cost per Net Outcome | Workload cost ÷ net operational quantity | Undefined when net quantity is zero or negative. |
| Scrap-Adjusted Margin Erosion | Scrap cost ÷ EstimatedValue | Not equivalent to Scrap Rate or realized ROI. |
| Realization Rate | Settled realized value ÷ original planned value | Segment by role/unit; undefined when planned value is zero. |

Currency, unit, stakeholder lens, and cost basis must always be explicit. Minutes cannot be subtracted from ticket counts. Friction already deducted in a value claim must not also be added again as fully loaded cost.

## Software-engineering and survey evidence

The software-engineering project does not prescribe one universal developer metric. It recommends pairing efficiency and quality, establishing comparable pre-AI baselines, measuring at release or customer-delivery level, and using stage counts to diagnose queues rather than declaring business value.

A strong evaluation candidate is a bounded migration with countable inventory, pre-recorded estimates, explicit completion criteria, and all tooling/review/rework time included. Staggered rollout can preserve comparison groups, and follow-up must be long enough to detect fading gains and delayed defects. Within-team comparisons are not normalized team rankings.

The page's three prominent external examples have different evidentiary strength:

- [METR v1](https://arxiv.org/html/2507.09089v1) reports a task-randomized study of 16 experienced developers and 246 tasks using early-2025 tools. It estimated 19% longer completion even though participants retrospectively believed they were 20% faster. The result is setting-specific, not proof that AI universally slows development.
- The [NBER working paper](https://www.nber.org/papers/w35275) reports a matched event study over more than 500,000 GitHub developers and attenuation from coding activity toward releases/use. The design is observational, not randomized; only the abstract/disclosures were inspected here.
- The [Amazon Q milestone article](https://aws.amazon.com/blogs/devops/amazon-q-developer-just-reached-a-260-million-dollar-milestone/) reports first-party promotional estimates of 4,500 developer-years and $260 million annual savings using different methods. They are not additive, independently audited results.

The State of Tokenomics public page reports 472 responses collected in August–September 2026, with technology/software at 40%, financial services at 17%, and median respondent revenue of $1.8B. The page did not expose recruitment frame, response rate, organization deduplication, question-level denominators, weighting, uncertainty intervals, raw records, or free-text coding method.

Reported 4× router-use and 3.7× ownership associations with CFO-value confidence are correlations, not causal effects. The headline revenue total of $4.6T conflicts with industry rows that exceed it; technology, financial services, and healthcare alone total $5.5T. The discrepancy must not be silently reconciled. The associated PDF was discoverable but not substantively decoded, so it cannot be used to assert methods absent from the HTML page.

## FOCUS and interoperability

The inspected FOCUS material came from an immutable commit of candidate 1.5 recommendations, not a ratified 1.5 release. It proposes principal, credential, requester, SKU-price, currency, and AI-model billing concepts useful for future interoperability.

Important boundaries include:

- A requester or principal identifier describes attribution; it must not be reusable as an authentication credential.
- SKU price resolution requires provider, price identifier, effective interval, contract, currency, and selected price type. A SKU Price ID alone is insufficient.
- Historical price snapshots must be retained when EffectiveCost depends on time-varying rates.
- National currencies use ISO 4217; a consumption unit must not masquerade as a currency code.
- AI billing examples keep input and output token rows separate. One inspected illustration uses 8.4M input tokens at $5/M and 2.1M output tokens at $25/M, without discounts.
- Published query examples were BigQuery SQL and were not executed or ported to Snowflake.

The local Snowflake `FOCUS_COST_USAGE_V1_3` view remains useful for current billing evidence, subject to its documented limitations. It must not be labeled FOCUS 1.5 compliant based on candidate concepts or this research.

## Repository fit and evidence gaps

The implemented boundary is defined in [FinOps Evidence Contract](operations/finops-evidence-contract.md). The current report carries selected raw credits, warehouse residuals, Functions observations, User-AI aggregates, and an explicit coverage inventory. Several AI service paths remain `NOT_COLLECTED`; `OTHER_COSTS` overlaps other views; FOCUS, currency, contract, and EffectiveCost evidence are not currently collected by the implementation.

| Tokenomics evidence need | Current repository evidence | Verdict |
|---|---|---|
| Snowflake account/service consumption | Selected Account Usage and service-aware credit evidence | **Partial fit.** Useful bounded consumption evidence with freshness and overlap caveats. |
| National-currency billed/effective cost | Not implemented in the current report | **Gap.** Credits cannot establish invoiced or amortized monetary cost. |
| Full delivery-path TCA | No external API/SaaS, labor, platform provision, or idle-commitment model | **Gap.** Current evidence is not fully loaded TCA. |
| Request/run trace to workload and owner | Some query/task/service identifiers; no universal workload/task contract | **Partial/gap.** Do not infer joins where source identity is absent. |
| Cache read/write/uncached token buckets | Not represented as a complete contract | **Gap.** Cache economics cannot be calculated reliably. |
| Task attempts and technical quality gate | Operational task status exists for Snowflake tasks, not business AI tasks/outcomes | **Semantic gap.** Infrastructure task runs are not VADA Tasks. |
| Outcome ledger and settlement | Not implemented | **Gap.** No quality-qualified business outcome or amendment ledger. |
| Value claims and Finance attestation | Not implemented | **Gap.** No estimated/realized/planned value or booking authority. |
| FOCUS interoperability | Native Snowflake FOCUS v1.3 exists outside this report | **Bounded fit.** Not evidence of candidate 1.5 adoption. |
| ROI or realized savings | No matched value and complete cost boundary | **Unsupported.** Current repository must not claim ROI. |

The most important protection is semantic: **do not relabel existing fields to appear compliant**. A query ID is not automatically a business Task ID. A successful Snowflake task is not a quality-qualified customer Outcome. Credits are not currency EffectiveCost. A threshold alert is not a value decision. Missing data must remain unknown or unlinked, not become zero.

## Recommended documentary and implementation sequence

This research authorizes documentation only. Any runtime work requires a separate scoped decision, source-contract verification, tests, and deployment authorization.

1. **Keep the existing evidence contract explicit.** Continue publishing source, scope, basis, freshness, and overlap warnings before adding derived metrics.
2. **Choose one bounded use case.** Follow the TCA advice: one delivery path, one rate card, one product/workload, and one quality-qualified outcome. Avoid an enterprise-wide schema before the evidence exists.
3. **Define identifiers before joins.** Establish opaque `WorkloadId`, `TaskId`, and `OutcomeId` ownership, propagation, retention, and privacy rules. Never store credentials or raw prompts merely to support costing.
4. **Add monetary evidence separately from credits.** Select billed versus EffectiveCost, currency, contract/rate version, period, allocation basis, and reconciliation policy. Preserve source charge identity.
5. **Instrument attempts and quality.** Count retries, failures, discarded work, and unlinked activity in cost. Define technical and post-delivery quality gates with accountable owners.
6. **Introduce an outcome ledger before value claims.** Use half-open UTC windows, immutable settlement/amendment behavior, net compatible units, and explicit evidence provenance.
7. **Require Finance-approved value conversion.** Keep estimated, planned, and realized value distinct; record conversion hops and uncertainty; prevent alternative stakeholder claims from being summed.
8. **Validate optimization experimentally.** For routing, caching, prompt changes, or model replacement, compare quality, latency, retries, total cost, and distribution—not list price alone.
9. **Adopt FOCUS only at a named version.** Validate the actual produced dataset and preserve historical price resolution. Do not implement against future-dated candidate text as though ratified.
10. **Add governance without creating committee theater.** Reuse existing Engineering, Product, FinOps, Finance, Procurement, Security, and Leadership authorities where possible. Assign decision rights and escalation paths before automation.

## Open decisions before any implementation

- Which workload and delivery path is the first bounded pilot?
- Which monetary basis is authoritative: billed cost, amortized EffectiveCost, or a separately approved fully loaded rate?
- Who owns workload, task, outcome, and value identifiers?
- What technical and business quality floors apply, and over what settlement window?
- How are retries, evaluations, indexing, idle capacity, shared costs, and unmatched charges classified?
- Which value destinations may be estimated, realized, or booked, and who may attest them?
- What privacy boundary applies to prompts, outputs, traces, user identity, and business evidence?
- Which FOCUS version is normative, and what conformance/validation process applies?
- How will late billing, late linkage, reversals, and rounding reconciliation preserve conservation and history?

Until these are resolved, this research should guide terminology, evidence gaps, and future design—not create fields that imply unsupported maturity.

## Source ledger

The project-level ledger above records the 12 indexed entries. The following supporting artifacts materially informed interpretation:

| Source | Coverage | Use and caveat |
|---|---|---|
| [Seven-Layer Tokenomics Stack Paper](https://www.tokeneconomics.com/projects/the-seven-layer-tokenomics-stack-paper/) | FULL HTML | Detailed layer definitions, influence boundary, and measurement guidance. |
| [Tokenomics Mind Map viewer](https://tokenomics-foundation.github.io/tokenomics_mindmap/mindmap.html) and [served YAML](https://tokenomics-foundation.github.io/tokenomics_mindmap/tokenomics_mindmap.yaml) | PARTIAL | Source/YAML inspected without executing the viewer; child maturity varies independently of root status. |
| [Mind-map repository README](https://raw.githubusercontent.com/tokenomics-foundation/tokenomics_mindmap/main/README.md) | FULL | Draft → WG-consensus RC → stable maturity definitions; not implementation status. |
| [Terminology Markdown export](https://www.tokeneconomics.com/projects/terminology-kpis.md) | PARTIAL | Selected terms/KPIs from data v0.0.3; served YAML was not hash-matched to tagged source. |
| [METR randomized study](https://arxiv.org/html/2507.09089v1) | PARTIAL | Abstract, core method/results, and caveats; appendices/data not comprehensively audited. |
| [NBER working paper 35275](https://www.nber.org/papers/w35275) | PARTIAL | Abstract and disclosures only; observational design. |
| [Amazon Q $260M milestone](https://aws.amazon.com/blogs/devops/amazon-q-developer-just-reached-a-260-million-dollar-milestone/) | FULL article | First-party estimate method; underlying data and independent audit absent. |
| [FOCUS candidate source at commit `4fd8cf4`](https://github.com/FinOps-Open-Cost-and-Usage-Spec/FOCUS_Spec/tree/4fd8cf44c0eb5b147146074ba1cfa8489e325d0a/specification) | PARTIAL release audit | Selected candidate columns, currency, SKU-price, AI billing examples, and query examples; not ratified 1.5. |
| [State of Tokenomics RC1.0a PDF](https://www.tokeneconomics.com/wp-content/uploads/2026/09/State-of-Tokenomics-September-23-2026-Release-Candidate-1.0a.pdf) | UNAVAILABLE | Binary was reachable but not decoded; no claims are attributed to unseen slide content. |

## Attribution and adaptation notice

This document summarizes and adapts material published by the [Tokenomics Foundation](https://www.tokeneconomics.com/), a FinOps Foundation project. The inspected website footer identifies the material as licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). The [FinOps Foundation attribution guidance](https://www.finops.org/introduction/how-to-use/) requires appropriate credit, a license link, and indication of changes.

Changes here include selection, reorganization, comparison with this repository, equations rendered in project terminology, implementation-gap analysis, and recommendations. The adaptation is not endorsed by the Tokenomics Foundation or FinOps Foundation. No certification, conformance, logo right, or production implementation is claimed. Linked third-party research, provider documentation, repositories, and code can have separate terms; the website license must not be assumed to license every linked artifact.

## Completion boundary

This research establishes a traceable documentary baseline for the Foundation's 12 indexed projects as of the cutoff. It does not approve a schema, financial policy, FOCUS upgrade, task/outcome pipeline, data collection expansion, Snowflake change, or deployment. The next valid step is a separately authorized, bounded pilot decision that names its use case, evidence contracts, quality gates, accountable owners, and verification plan.
