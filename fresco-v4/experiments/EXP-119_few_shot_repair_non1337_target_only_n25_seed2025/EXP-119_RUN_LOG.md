# EXP-119 Run Log - repaired non-1337 target-only N=25 seed 2025 rerun

**Run ID**: EXP-119_few_shot_repair_non1337_target_only_n25_seed2025
**Date**: 2026-03-16

## Objective
Re-run the original non-1337 target-only with N=25 anvil -> conte hardware_cpu_standard cell on the frozen 1337 data/split universe so this point reflects only label-sampling variation.

## Hypothesis (if experiment)
Freezing `data_seed`/`split.seed` at 1337 should remove the original seed confound, and setting `few_shot.min_target_eval_rows=50` should prevent the original zero-eval failure mode while keeping this rerun on the same frozen overlap cohort as the valid 1337 cells.

## Repair Context
- Original main cell: `EXP-065_few_shot_main_target_only_n25_seed2025`.
- Original issue: Original main cell `EXP-065_few_shot_main_target_only_n25_seed2025` was invalid: `results\exp003_main_few_shot_summary.csv` records `status=null_metrics` and `status_reason=no data after filters; metrics not computed`; related logs are `<FRESCO_V4_CODE_ROOT>/experiments/sweep_logs/exp003_main_10409707_63.out` / `<FRESCO_V4_CODE_ROOT>/experiments/sweep_logs/exp003_main_10409707_63.err`. That original config also used `split.seed=2025`, `random_seed=2025`, and `data_seed=unset` (`<FRESCO_V4_CODE_ROOT>/experiments/EXP-065_few_shot_main_target_only_n25_seed2025/config/EXP-065_few_shot_main_target_only_n25_seed2025.json`).
- Repair applied: Repair rerun `EXP-119_few_shot_repair_non1337_target_only_n25_seed2025` froze `data_seed=1337` and `split.seed=1337` and set `few_shot.min_target_eval_rows=50` in `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/config/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025.json`; parent array job is `10410106` and this run corresponds to task `10410106_42` via `<FRESCO_V4_CODE_ROOT>/config/exp078_repair_non1337_config_paths.txt` and `<FRESCO_V4_CODE_ROOT>/scripts/exp078_repair_non1337.slurm`.

## Inputs
- Dataset label: `chunks-v3-authoritative` (`<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/config/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025.json`)
- Input manifest: `<FRESCO_DATA_ROOT>/chunks-v3/manifests/output_manifest.jsonl` (`<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/config/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025.json`)
- Clusters: `anvil` -> `conte` (`<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/config/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025.json`)
- Date range: not recorded in run-specific artifacts; this rerun uses the authoritative chunks-v3 snapshot referenced by `<FRESCO_DATA_ROOT>/chunks-v3/manifests/output_manifest.jsonl` (`<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/config/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025.json`)

## Code & Environment
- Script: `<FRESCO_V4_CODE_ROOT>/scripts/few_shot_transfer.py` (`<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/manifests/run_metadata.json`)
- Config: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/config/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025.json`
- Git commit (pipeline): not recorded (`git_commit=null` in `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/manifests/run_metadata.json`)
- Git commit (analysis): not separately recorded; same caveat as pipeline (`<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/manifests/run_metadata.json`)
- Conda env: `fresco_v2` (`<FRESCO_V4_CODE_ROOT>/scripts/exp078_repair_non1337.slurm`)
- Python: `3.10.19 (main, Oct 21 2025, 16:43:05) [GCC 11.2.0]` (`<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/validation/python_version.txt`)
- Package lock: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/validation/pip_freeze.txt`

## Execution
- Cluster: Gilbreth
- Submission command: `sbatch <FRESCO_V4_CODE_ROOT>/scripts/exp078_repair_non1337.slurm` (`<FRESCO_V4_CODE_ROOT>/scripts/exp078_repair_non1337.slurm`)
- Job IDs: parent array `10410106`; task `10410106_42` with `state=COMPLETED` (`<FRESCO_V4_CODE_ROOT>/config/exp078_repair_non1337_config_paths.txt`; `<FRESCO_V4_CODE_ROOT>/experiments/sweep_logs/exp078_repair_10410106_42.out`)
- Start / end time (UTC): `2026-03-16T23:26:26Z` / `2026-03-16T23:28:06Z` (`<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/logs/few_shot_transfer.log`)

## Outputs
- Output root: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/results/`
- Manifests: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/manifests/`
- Validation reports: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/validation/`
- Predictions artifact: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/results/predictions_target.parquet`
- Metrics artifact: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/results/metrics.json`
- Relevant logs: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/logs/few_shot_transfer.log`; `<FRESCO_V4_CODE_ROOT>/experiments/sweep_logs/exp078_repair_10410106_42.out`; `<FRESCO_V4_CODE_ROOT>/experiments/sweep_logs/exp078_repair_10410106_42.err`

## Results Summary
- Source-test R-squared: `0.2091`; Target R-squared: `0.0204`; Target bootstrap 95% CI: `[-0.0293, 0.0567]`; Target MAE(log): `0.0855`; Target MdAE(log): `0.0734`; Target SMAPE: `63.53`; Target bias(log): `0.0149`; Target calibration slope: `1.0207`. Source: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/results/metrics.json`.
- Calibration / evaluation counts: `actual_cal_n=25`, `actual_eval_n=198`, `matched_source_n=6995`, `matched_target_n=223`, `overflow_pred=false`. Source: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/results/metrics.json`.

## Validation Summary
- Runtime completed with `state=COMPLETED` / `exit_code=0:0` and materialized `results/metrics.json`, `predictions_target.parquet`, and `predictions_source_test.parquet`. Sources: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/results/metrics.json`; `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/results/predictions_target.parquet`; `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/results/predictions_source_test.parquet`.
- Recorded split sizes: `actual_cal_n=25`, `actual_eval_n=198`, `min_target_eval_rows=50`, `min_target_eval_rows_satisfied=true`, `calibration_n_capped=false`. Sources: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/results/metrics.json`; `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/logs/few_shot_transfer.log`.
- No standalone Level 0/1 validation report was emitted beyond environment capture files in `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/validation/python_version.txt` and `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/validation/pip_freeze.txt`, so treat this as runtime/metrics validation rather than a full archived validation sign-off.

## Known Issues / Caveats
- This is a repair rerun for original main cell `EXP-065_few_shot_main_target_only_n25_seed2025`, not a net-new experiment. Sources: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-065_few_shot_main_target_only_n25_seed2025/config/EXP-065_few_shot_main_target_only_n25_seed2025.json`; `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/config/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025.json`.
- Provenance caveat: `manifests/run_metadata.json` records `git_commit=null`, so the exact pipeline commit was not captured for this run. Source: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/manifests/run_metadata.json`.
- Repair design caveat: the repaired config froze `data_seed=1337` / `split.seed=1337` and set `few_shot.min_target_eval_rows=50`. Source: `<FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/config/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025.json`.

## Repro Steps
1. `ssh jmckerra@<REDACTED_HPC_HOST> && cd <FRESCO_V4_CODE_ROOT>`
2. `source <CONDA_INIT_SCRIPT> && conda activate fresco_v2`
3. `python <FRESCO_V4_CODE_ROOT>/scripts/few_shot_transfer.py --config <FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/config/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025.json`
4. `sed -n "42p" <FRESCO_V4_CODE_ROOT>/config/exp078_repair_non1337_config_paths.txt && cat <FRESCO_V4_CODE_ROOT>/experiments/EXP-119_few_shot_repair_non1337_target_only_n25_seed2025/results/metrics.json`
