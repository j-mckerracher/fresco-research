# FRESCO Research Artifacts for the MASCOTS 2026 Cross-Cluster Paper

This repository is a curated public snapshot of the documents, configs, scripts, result summaries, and experiment records behind the MASCOTS 2026 paper on cross-cluster HPC memory prediction. It is organized so that a reader can move from the paper, to the claims, to the canonical experiment records, and then to the underlying pipeline and methodology documents without needing access to the original private working directory.

The central paper result is the contrast between:

- catastrophic zero-shot cross-cluster transfer, with `R^2` as low as `-21.3`, and
- a local Anvil-only telemetry blueprint evaluated on the canonical FRESCO v3 dataset, with `R^2 = 0.2520` on `416,616` filtered jobs under a strict temporal split.

## What is in this repository

The repository is intentionally organized around the original project structure instead of flattening everything into a generic artifact dump.

### `paper/`

This folder contains the paper-facing materials:

- `MASCOTS_2026.pdf` — the current paper PDF snapshot
- `EXP-085-Results.md` — the canonical local-blueprint result summary used for Section 5
- `Outline.md` — the paper outline/skeleton
- `latex/FRESCO_CrossCluster/` — the LaTeX source snapshot used to draft the paper, including `main.tex`, `references.bib`, and `r2_comparison.pdf`

If you are starting from the paper and want to understand the artifact trail, read this folder first.

### `fresco-v3/`

This is the authoritative reproducibility backbone for the zero-shot transfer portion of the paper and for the canonical FRESCO v3 dataset:

- `docs/` — schema, provenance, validation, workload taxonomy, feature-availability, and master-index documentation
- `runbooks/` — operational runbooks and reproducibility checklists
- `paper/` — paper-ready methods, evaluation, threats, and artifact guidance
- `config/` — canonical JSON configs, including `clusters.json` and the v3 production config
- `scripts/` — the core v3 analysis and production scripts
- `experiments/` — curated experiment records copied in lightweight form
- `results/` — top-level production run log material

For most readers, the best entry points here are:

- `docs/MASTER_INDEX.md`
- `docs/SCHEMA_AND_PROVENANCE.md`
- `docs/WORKLOAD_TAXONOMY_AND_MATCHING.md`
- `ZERO_SHOT_CROSS_CLUSTER_TRANSFER_PLAN.md`

### `fresco-v4/`

This folder captures the follow-on few-shot calibration work that grew directly out of the negative zero-shot transfer result:

- `FEW_SHOT_TRANSFER_PLAN.md`
- `docs/FEW_SHOT_METHODOLOGY.md`
- `paper/` methodology and evaluation notes
- `config/` and `scripts/` for the few-shot experiments
- `experiments/` run logs for the repaired few-shot sweep cells
- `results/` summary tables harvested from the sweep

This material is useful for readers who want to understand what was tried after the zero-shot result failed, even though the MASCOTS paper’s core empirical backbone is the v3 analysis.

### `historical-notes/`

This is a small, curated slice of the older `FRESCO-Research` workspace. It is included to preserve the research trail without publishing the entire internal scaffolding repository.

Included here are:

- early planning notes for cross-site runtime and memory prediction,
- the central findings log,
- an early cross-cluster transfer experiment (`EXP-007`), and
- the important `EXP-015` enhanced validation report that helped establish the negative transfer narrative before the authoritative v3 pipeline was finalized.

Treat this section as historical context, not as the canonical source of final paper claims.

## How the repository is organized conceptually

If you are reading the paper and want to trace a claim:

1. Start in `paper/`.
2. Use `paper/EXP-085-Results.md` for the canonical local-telemetry result.
3. Use `fresco-v3/docs/WORKLOAD_TAXONOMY_AND_MATCHING.md` and `fresco-v3/ZERO_SHOT_CROSS_CLUSTER_TRANSFER_PLAN.md` for the zero-shot transfer methodology and the 84-experiment framing.
4. Use `fresco-v3/experiments/` and `fresco-v4/experiments/` for run-level documentation.
5. Use `fresco-v3/scripts/` and `fresco-v4/scripts/` if you want to inspect or adapt the code paths that produced the reported artifacts.

## What was intentionally included

The selection policy for this public snapshot was:

- include human-readable research artifacts that explain the methods, experiment lineage, and reported results,
- include configs and scripts necessary to understand what was run,
- include lightweight result summaries and experiment logs,
- preserve original project names where possible so that paper references and internal doc references remain intelligible.

## What was intentionally excluded

This repository does **not** include the raw FRESCO dataset or large intermediate binary outputs.

In particular, the public snapshot excludes:

- large parquet predictions and matched-index artifacts,
- bulky scratch outputs and model binaries from the older `FRESCO-Research` workspace,
- private or environment-specific HPC runtime traces that do not help an outside reader reproduce the reasoning,
- internal working folders that were primarily used as LLM/research-management scaffolding.

## Sanitization notes

Some copied documents originally contained machine-specific paths and hostnames. In this public snapshot, those references were replaced with placeholders such as:

- `<FRESCO_DATA_ROOT>`
- `<FRESCO_V3_CODE_ROOT>`
- `<FRESCO_V4_CODE_ROOT>`
- `<REDACTED_HPC_HOST>`

This keeps the artifact trail readable while avoiding publication of environment-specific infrastructure details. The placeholders are descriptive enough for another researcher to map them onto their own environment.

## Recommended reading order

If you want the fastest path through the repository:

1. `paper/MASCOTS_2026.pdf`
2. `paper/EXP-085-Results.md`
3. `fresco-v3/docs/MASTER_INDEX.md`
4. `fresco-v3/docs/WORKLOAD_TAXONOMY_AND_MATCHING.md`
5. `fresco-v3/docs/SCHEMA_AND_PROVENANCE.md`
6. `fresco-v4/docs/FEW_SHOT_METHODOLOGY.md`
7. `historical-notes/fresco-research/Experiments/EXP-015_enhanced_validation/EXP015_FINAL_REPORT.md`

## If you want to reproduce or adapt the work

This repository is best understood as a **research artifact archive**, not as a polished software package.

The most useful starting points for reproduction are:

- `fresco-v3/scripts/evaluate_local_blueprint.py`
- `fresco-v3/scripts/regime_matching.py`
- `fresco-v3/scripts/model_transfer.py`
- `fresco-v4/scripts/few_shot_transfer.py`
- `fresco-v3/config/clusters.json`
- `fresco-v3/runbooks/REPRODUCIBILITY_CHECKLIST.md`

Because the original work used HPC-resident parquet data and site-specific compute environments, an external researcher should expect to adapt dataset paths, environment setup, and job-submission details.

## Scope and intended use

This repository exists to help readers of the paper answer:

- what exactly was run,
- how the canonical results were produced,
- which earlier experiments motivated the final framing,
- and where the code, config, and run-level notes live.

It is meant to support transparency, artifact review, and follow-on research.
