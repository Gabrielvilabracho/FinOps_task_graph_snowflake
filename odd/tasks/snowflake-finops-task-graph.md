# Snowflake Native FinOps Task Graph

Objective: research, design, implement, and document a serverless FinOps monitoring system native to Snowflake.
Branch: `feat/snowflake-finops-task-graph` · Delivery: `ask-on-risk` with `feature-branch-chain` · Runner: SQL static checks plus Snowflake integration checks when credentials are explicitly available.
Forecast: more than 400 authored lines across SQL, tests, deployment scripts, Obsidian planning, and OpenWiki documentation.

## Specs

- S1 — Build, not merely describe, “el sistema FinOps en snowflake, usando task graph”. Acceptance: executable Snowflake SQL defines modular procedures and an acyclic Task Graph without Airflow or dbt.
- S2 — Cover “costes, errores, warehouses, IA, Queries, y otros costes realicionados con cost control”. Acceptance: each supported concern has an independent analysis module; unsupported thresholds remain configurable or explicitly undecided.
- S3 — “generan alertas e informes y diferencian claramente lo creado de lo pendiente”. Acceptance: persisted findings feed separate reporting and alerting paths, and documentation labels implemented, pending, proposed, and unconfirmed work.
- S4 — Perform “una busqueda adecuada de como hacerlo, buscando la informacoin en snowflake docuemntation oficial”. Acceptance: architecture decisions cite current official Snowflake documentation and record constraints, optimizations, and edition/privilege prerequisites.
- S5 — “generar le plan docuemntado en obsidian y implementarlo”. Acceptance: create a linked Obsidian architecture note and canonical TaskNotes tasks, then implement the approved plan in the repository.
- S6 — “implement Openwiki para docuematacion para la AI”. Acceptance: initialize and finish an OpenWiki lifecycle after implementation so repository behavior is grounded in source-backed Claims.
- S7 — Reproduce “el organigrma adecucuado para las carpetas”. Acceptance: repository layout separates setup, procedures, tasks, alerts/reports, tests, deployment, docs, and generated OpenWiki pages by responsibility.
- S8 — Preserve “Arquitectura de Grafo Acíclico Dirigido (Task Graph / DAG), Arquitectura Modular y Desacoplada (Separation of Concerns), Patrón de Resiliencia y Cierre (Finalizer Pattern), Fase Futura (Event-Driven)”. Acceptance: DAG dependencies are explicit, procedures own business logic, a finalizer observes graph completion, and Streams/Triggered Tasks remain a documented later phase unless immediate-event requirements are approved.
- S9 — Implement the confirmed cost rules: previous-day credits, comparison with the prior day, alert above 25 credits, alert above 30% growth, otherwise normal. Acceptance: deterministic SQL tests cover threshold, growth, normal, missing-baseline, and technical-failure semantics without inventing thresholds for other modules.
- S10 — Preserve deployment facts as historical evidence while keeping the active target explicit. Acceptance: current executable artifacts target `FINOPS_DEV.FINOPS`; prior target assumptions remain documented in the Log and no deployment or grant is claimed without observed Snowflake evidence.
- S11 — The system must answer: “¿Qué ocurrió ayer?”, “¿Está ocurriendo algo importante?”, and “¿Qué tenemos que comprobar?”. Acceptance: daily summary distinguishes module findings, business anomalies, technical failures, and an overall status such as `ATTENTION_REQUIRED`.

## Tasks

- T1 · S4,S8 · delegated exploration · complete · Official Snowflake evidence map delivered and parent spot-check completed.
- T2 · S1-S11 · inline · complete · Architecture, data contracts, DAG, repository layout, and ADR committed in `d075450` and subsequent work units.
- T3 · S5,S7 · inline · complete · Obsidian project plan, dashboard link, and canonical TaskNotes created.
- T4 · S1,S2,S9,S10 · inline · complete; live proof pending · Foundation, policy, lifecycle, and analyzers committed in `9b1d97d`, `2208992`, and `f41d08d`.
- T5 · S1,S8,S11 · inline · complete; live proof pending · Serverless graph and finalizer committed in `debb6f2`.
- T6 · S3,S10,S11 · inline · complete; live proof pending · Reporting, scoped access, deployment, and operations committed through `d229de4` and `76456b3`.
- T7 · S1-S11 · inline · complete locally; live validation deferred by user · RED/GREEN contract tests, independent high-risk verification, and deployment-order probes pass; owner and runtime configuration will be edited manually before any activation.
- T8 · S6 · inline · complete · OpenWiki initialized, six source-backed pages and Claims finalized in `2d4b305`; maintenance hardening and regression coverage completed through `b7018aa`.

## Log

- L1 · 2026-11-15 · User request (verbatim): “no es solo documentar, es crear el sistem FinOps en snowflake , usando task graph , organizado con tareas que revisan costes, errores, warehouses, IA, Queries, y otros costes realicionados con cost control,  generan alertas e informes y diferencian claramente lo creado de lo pendiente, para ello tenemos que realizar una busqueda adecuada de como hacerlo, buscando la informacoin en snowflake docuemntation oficial que se cneuntra otod docuemntado, buscar las optimizaciones y la generar el sistema , generar le plan docuemntado en obsidian y implementarlo , tambine es necesario implementar Openwiki para docuematacion para la AI. 
reporudicir el organigrma adecucuado para las carpetas Se trata de un modelo FinOps nativo en Snowflake (Serverless) altamente maduro. Evita usar herramientas externas (como Airflow o dbt) para la monitorización de costes, aprovechando al máximo las capacidades internas de Snowflake (Tasks, Procedures) para mantener los datos de consumo y la lógica de alertas en el mismo lugar, reduciendo latencia, costes de extracción y complejidad de infraestructura. siguiendo Arquitectura de Grafo Acíclico Dirigido (Task Graph / DAG), Arquitectura Modular y Desacoplada (Separation of Concerns), Patrón de Resiliencia y Cierre (Finalizer Pattern), Fase Futura (Event-Driven) .”
- L2 · 2026-11-15 · Repository created at `/Users/gabrielvilabracho/projects/FinOps_task_graph_snowflake` and initialized on feature branch `feat/snowflake-finops-task-graph`.
- L3 · 2026-11-15 · No project-specific `.atl/skill-registry.md` exists in the new repository; delegated work must use applicable installed skills only.
- L4 · 2026-11-15 · Official documentation confirmed finalizer behavior, graph ownership/limits, runtime graph IDs, Account Usage latency, native notification constraints, and triggered-task tradeoffs. T1 covered S4 and S8.
- L5 · 2026-11-15 · The Obsidian source note is `projects/FinOps Task Graph/FinOps Task Graph.md`; eight canonical TaskNotes represent execution work without duplicate checkbox tasks.
- L6 · 2026-11-15 · Local test-first evidence: `python3 -m unittest discover -s tests -p "test_*.py"` failed before implementation with 30 missing-contract failures, then passed 7 tests after implementation.
- L7 · 2026-11-15 · The user selected `feature-branch-chain` for delivery because the forecast exceeds 400 authored changed lines.
- L8 · 2026-11-15 · Engram task-document mirror remains pending because the new project identity was rejected as ambiguous by the server despite repository-local detection; local progress is authoritative until resynchronization succeeds.
- L9 · 2026-11-16 · Independent security verification rejected blanket and runtime-owner grants to `GG_APP_CC_REC_DATAWARE_DMO`; `d229de4` now limits it to named FinOps read/monitor access and leaves owner privileges in an explicit template.
- L10 · 2026-11-16 · Local verification passes 15 deterministic tests, deployment-order mocking, shell syntax, and diff checks. Live Snowflake compilation, privileges, smoke execution, notification, and finalizer behavior remain unavailable without an explicitly authorized session.
- L11 · 2026-11-16 · OpenWiki run `edcf391c-817b-4895-bd74-54330d281a1d` finalized six pages with 29 source-backed Claims; generated indexes, manifests, and maintenance workflow were committed in `2d4b305`.
- L12 · 2026-11-16 · Generated workflow hardening keeps trusted schedule/manual triggers, full-SHA action pins, non-persisted checkout credentials, and environment-mediated PR URL annotation. Deterministic npm transitive locking remains an advisory.
- L13 · 2026-11-16 · User decision (verbatim): “no no es necesario ejecutar el smoke test , DEJALE EN MODO ADITABLE PAR YO MODIFICARLO PERSONALMENTE CUANDO TENGA QUIEN VA SER EL PROPIETARIO Y COO SER ALA CONFIGURACION.” The repository remains suspended and editable; no live smoke test or remote Snowflake operation is authorized.
- L14 · 2026-11-20 · User selected `FINOPS_DEV.FINOPS` for a clean first deployment and confirmed the historical `DATALAB.SPAIN` objects were never executed, so no data migration is required. S10 was updated to preserve the old context as history rather than an active target.
