# Edusched

Intelligent, school‑wide timetabling system for pre‑term scheduling across all classes, teachers, and rooms. Backend planned with FastAPI; Frontend planned with Vue 3. This repository is currently in Phase 0 (docs and research only).

## Repository structure (current vs planned)

- `docs/` — Single source of truth for requirements, architecture, algorithms, API, frontend, ops, and adoption.
- `AGENTS.md` — Governance: MCP feedback loop + Context7 research rules.
- Planned (to be scaffolded in Phase 1):
  - `backend/` — FastAPI app, domain, workers, migrations, tests
  - `frontend/` — Vue 3 app, components, stores, tests
  - `infra/` — Docker/Kubernetes manifests, compose

## Start here

- `docs/README.md` — Documentation entry point and navigation
- `docs/product/vision-and-scope.md` — Product goals and boundaries
- `docs/architecture/system-architecture.md` — High‑level architecture and components
- `docs/algorithms/approach-overview.md` — Solver strategy and orchestration
- `docs/backend/api-design.md` — API standards and resource map
- `docs/frontend/ui-information-architecture.md` — UI IA and key flows
- `docs/operations/ci-cd.md` — CI/CD and environments
- `docs/product/pricing-and-packaging.md` — Packaging, pricing, and billing model
- `docs/GLOSSARY.md` — Domain glossary (CN/EN)

## Governance and collaboration

- Please read `AGENTS.md` and follow:
  - MCP feedback loop: propose → get feedback → refine
  - Context7 research: use latest official docs before making technical decisions
  - Docs are the source of truth; update docs before code

## Status

- Phase 0: Documentation and research in progress. No implementation yet.
