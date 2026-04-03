# Experiment / Production Run Log

**Run ID**: EXP-085_local_anvil_rf_temporal_peak_memory  
**Date**: 2026-03-29  
**Owner**: Josh McKerracher

## Objective

Produce canonical R², MAE, and feature-importance numbers for Section 5 of the
paper by training a Random Forest on the full Anvil dataset from the authoritative
v3 production parquet with a temporal 80/20 split. This is the 85th experiment in
the FRESCO-v3 series — the definitive "local telemetry blueprint" demonstrating
that intra-cluster memory prediction works, in contrast to the cross-cluster
transfer challenges documented in EXP-044 through EXP-084.

## Hypothesis

A Random Forest trained on historical Anvil jobs (temporal 80% split) will achieve
positive predictive R² (> 0.5) on future Anvil jobs (temporal 20% split) for
peak_memory_gb, demonstrating that local HPC telemetry contains strong signal for
memory usage prediction within a single cluster.

## Inputs

- input_root: `<FRESCO_DATA_ROOT>/chunks-v3/PROD-20260203-v3_v3.parquet`
- date_range: 2015-01-01 to 2023-12-31
- clusters: anvil (single cluster, intra-cluster prediction)
- regime: hardware_cpu_standard (GPU nodes and highmem excluded)
- label: peak_memory_gb (derived from value_memused via canonical v3 logic)
- features: all available numeric columns (log1p transformed)
- model: Random Forest (n_estimators=100, max_depth=20, min_samples_leaf=4, n_jobs=-1)
- split: temporal 80/20 by submit_time

## Code & Environment

- git commit (pipeline): _TO BE FILLED POST-RUN_ (see validation/git_commit.txt)
- conda env: fresco_v2
- python: _TO BE FILLED POST-RUN_ (see validation/python_version.txt)
- package lock artifact path: validation/pip_freeze.txt, validation/conda_env.yml

## Execution

- cluster: Gilbreth (Purdue RCAC)
- submission command: `sbbest experiments/EXP-085_local_anvil_rf_temporal_peak_memory/exp085_blueprint.slurm`
- job IDs: _TO BE FILLED POST-RUN_
- start/end time (UTC): _TO BE FILLED POST-RUN_

## Outputs

- output_root: experiments/EXP-085_local_anvil_rf_temporal_peak_memory/
- results: results/metrics.json, results/feature_importances.json, results/predictions_test.parquet
- manifests: manifests/run_metadata.json, manifests/input_files_used.json
- validation: validation/git_commit.txt, validation/git_status.txt, validation/pip_freeze.txt, validation/conda_env.yml, validation/host_info.txt, validation/python_version.txt

## Results Summary

_TO BE FILLED POST-RUN from results/metrics.json_

## Validation Summary

- [ ] metrics.json exists and contains R², MAE, bootstrap CI
- [ ] feature_importances.json exists
- [ ] predictions_test.parquet exists
- [ ] All validation artifacts present (git_commit, pip_freeze, conda_env, host_info, python_version)
- [ ] manifests/run_metadata.json exists
- [ ] manifests/input_files_used.json exists

## Known Issues / Caveats

- GPU requested but unused (a100-80gb is the only partition with sbagchi allocation)
- Column derivation replicated from fresco_data_loader.py, not imported directly, to support chunked memory-efficient loading of the 655M-row parquet
- Temporal split means test set covers only the most recent 20% of jobs; performance on earlier/later periods may differ

## Repro Steps

1. `cd <FRESCO_V3_CODE_ROOT>`
2. `source <CONDA_INIT_SCRIPT> && conda activate fresco_v2`
3. `python scripts/evaluate_local_blueprint.py --config experiments/EXP-085_local_anvil_rf_temporal_peak_memory/config/exp085_local_anvil_rf_temporal_peak_memory.json`
