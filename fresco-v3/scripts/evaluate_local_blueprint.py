#!/usr/bin/env python3
"""EXP-085: Local Anvil RF Temporal Peak Memory Prediction.

Trains a Random Forest on the full Anvil dataset from the authoritative v3
production parquet with a temporal 80/20 split, producing canonical R², MAE,
and feature-importance numbers for Section 5 of the paper.

Column derivation follows the canonical v3 logic (fresco_data_loader.py):
  - peak_memory_gb:      from value_memused max, unit auto-detected (lines 596-613)
  - runtime_sec:         (end_time - start_time).total_seconds()           (lines 694-698)
  - queue_time_sec:      (start_time - submit_time).total_seconds()        (lines 699-703)
  - runtime_fraction:    runtime_sec / timelimit_sec                       (lines 704-707)
  - peak_memory_fraction: peak_memory_gb / (node_memory_gb * nhosts)       (lines 615-624)
  - Hardware metadata:   joined from clusters.json via (cluster, queue)    (lines 549-635)

Memory-efficient: uses chunked pyarrow scanning so the full 655M-row parquet
never needs to fit in RAM.
"""

import argparse
import json
import logging
import os
import platform
import subprocess
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score

warnings.filterwarnings("ignore")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Canonical v3 aggregation rules (from fresco_data_loader.collapse_to_job_level)
# ---------------------------------------------------------------------------
DATETIME_AGG = {"submit_time": "min", "start_time": "min", "end_time": "max"}

RAW_METRICS = [
    "value_cpuuser",
    "value_gpu",
    "value_memused",
    "value_memused_minus_diskcache",
    "value_nfs",
    "value_block",
]

NUMERIC_MAX = [
    "timelimit_sec",
    "nhosts",
    "ncores",
    "memory_sampling_interval_sec",
]

STRING_FIRST = [
    "account",
    "queue",
    "cluster",
    "memory_includes_cache",
    "memory_collection_method",
    "memory_aggregation",
]


def _load_clusters_config(path):
    with open(path) as f:
        return json.load(f)


def _resolve_hardware(clusters_cfg, cluster_name, partition_name):
    """Per fresco_data_loader._resolve_hardware_spec (lines 539-546)."""
    cluster_cfg = clusters_cfg.get("clusters", {}).get(cluster_name, {})
    spec = dict(cluster_cfg.get("default", {}))
    if partition_name and "partitions" in cluster_cfg:
        spec.update(cluster_cfg["partitions"].get(partition_name, {}))
    return spec


# ---------------------------------------------------------------------------
# Phase 1: Memory-efficient chunked loading + job-level collapse
# ---------------------------------------------------------------------------
def load_anvil_job_level(parquet_path, cluster_filter, batch_size=2_000_000):
    """Read parquet in batches, filter to cluster, aggregate to job level.

    Replicates fresco_data_loader.collapse_to_job_level() but streams data
    so that the full 655M-row file never sits in memory at once.
    """
    dataset = ds.dataset(parquet_path, format="parquet")

    # Only read columns we need (saves ~40% memory vs reading all 31)
    available = set(dataset.schema.names)
    wanted = (
        ["jid", "cluster"]
        + list(DATETIME_AGG.keys())
        + RAW_METRICS
        + NUMERIC_MAX
        + STRING_FIRST
    )
    needed = [c for c in wanted if c in available]

    scanner = dataset.scanner(
        filter=(ds.field("cluster") == cluster_filter),
        columns=needed,
        batch_size=batch_size,
    )

    # Build per-column aggregation dict (used identically for partial + final)
    agg_dict = {}
    for col in needed:
        if col == "jid" or col == "cluster":
            continue
        if col in DATETIME_AGG:
            agg_dict[col] = DATETIME_AGG[col]
        elif col in RAW_METRICS or col in NUMERIC_MAX:
            agg_dict[col] = "max"
        else:
            agg_dict[col] = "first"

    partials = []
    total_raw = 0
    n_batches = 0

    for batch in scanner.to_batches():
        chunk = batch.to_pandas()
        if chunk.empty:
            continue
        total_raw += len(chunk)
        n_batches += 1
        if n_batches % 50 == 0:
            log.info(f"  ... {n_batches} batches, {total_raw:,} raw rows")

        # Partial job-level aggregation within this batch
        cols_present = {c: agg_dict[c] for c in agg_dict if c in chunk.columns}
        partial = chunk.groupby("jid", sort=False).agg(cols_present).reset_index()
        partials.append(partial)

    log.info(f"  Scanned {total_raw:,} raw rows in {n_batches} batches")
    log.info(f"  Merging {len(partials)} partial aggregations...")

    merged = pd.concat(partials, ignore_index=True)
    cols_present = {c: agg_dict[c] for c in agg_dict if c in merged.columns}
    df = merged.groupby("jid", sort=False).agg(cols_present).reset_index()

    log.info(f"  Collapsed to {len(df):,} unique jobs")
    return df, total_raw


# ---------------------------------------------------------------------------
# Phase 2: Canonical v3 column derivation
# ---------------------------------------------------------------------------
def derive_v3_columns(df, clusters_cfg, cluster_name):
    """Derive normalized columns per fresco_data_loader.py formulas."""

    # Normalize nullable dtypes (pyarrow → pandas may produce Int64/Float64
    # with pd.NA instead of numpy float64 with np.nan; pd.NA breaks np.where)
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].astype("float64")

    # runtime_sec  (lines 694-698)
    if {"start_time", "end_time"}.issubset(df.columns):
        df["runtime_sec"] = (df["end_time"] - df["start_time"]).dt.total_seconds()

    # queue_time_sec  (lines 699-703)
    if {"submit_time", "start_time"}.issubset(df.columns):
        df["queue_time_sec"] = (
            df["start_time"] - df["submit_time"]
        ).dt.total_seconds()

    # runtime_fraction  (lines 704-707)
    if {"runtime_sec", "timelimit_sec"}.issubset(df.columns):
        tl = df["timelimit_sec"]
        df["runtime_fraction"] = np.where(tl > 0, df["runtime_sec"] / tl, np.nan)

    # partition = queue  (line 563)
    if "queue" in df.columns:
        df["partition"] = df["queue"]

    # Hardware metadata from clusters.json  (lines 549-635)
    hw_cols = [
        "node_type",
        "node_cores",
        "node_memory_gb",
        "gpu_count_per_node",
        "gpu_model",
    ]
    for col in hw_cols:
        df[col] = None

    if "partition" in df.columns:
        for part in df["partition"].dropna().unique():
            spec = _resolve_hardware(clusters_cfg, cluster_name, part)
            mask = df["partition"] == part
            for col in hw_cols:
                if col in spec:
                    df.loc[mask, col] = spec[col]
        for col in ["node_cores", "node_memory_gb", "gpu_count_per_node"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # peak_memory_gb from value_memused  (lines 596-613)
    mem_col = "value_memused"
    if mem_col in df.columns:
        vals = df[mem_col].dropna()
        if len(vals) > 0:
            p95 = vals.quantile(0.95)
            if p95 > 1e6:  # bytes → GB
                df["peak_memory_gb"] = df[mem_col] / (1024**3)
                unit = "bytes"
            else:  # already GB
                df["peak_memory_gb"] = df[mem_col]
                unit = "GB"
            df["memory_original_value"] = df[mem_col]
            df["memory_original_unit"] = unit
            log.info(f"  Memory unit: {unit} (95th pct = {p95:.2f})")

    # peak_memory_fraction  (lines 615-624)
    needed = {"peak_memory_gb", "node_memory_gb", "nhosts"}
    if needed.issubset(df.columns):
        denom = df["node_memory_gb"] * df["nhosts"]
        df["peak_memory_fraction"] = np.where(
            denom > 0, df["peak_memory_gb"] / denom, np.nan
        )

    return df


# ---------------------------------------------------------------------------
# Provenance helpers
# ---------------------------------------------------------------------------
def _capture_provenance(output_root):
    """Write validation artifacts: git commit, pip freeze, host info."""
    val_dir = output_root / "validation"
    val_dir.mkdir(parents=True, exist_ok=True)

    # git commit
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        commit = "unknown"
    (val_dir / "git_commit.txt").write_text(commit + "\n")

    # git status
    try:
        status = subprocess.check_output(
            ["git", "status", "--short"], text=True, stderr=subprocess.DEVNULL
        )
    except Exception:
        status = "unknown"
    (val_dir / "git_status.txt").write_text(status)

    # python version
    (val_dir / "python_version.txt").write_text(sys.version + "\n")

    # pip freeze
    try:
        freeze = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        freeze = "unknown"
    (val_dir / "pip_freeze.txt").write_text(freeze)

    # conda env export
    try:
        conda_env = subprocess.check_output(
            ["conda", "env", "export"], text=True, stderr=subprocess.DEVNULL
        )
    except Exception:
        conda_env = "unknown"
    (val_dir / "conda_env.yml").write_text(conda_env)

    # host info
    host_lines = [
        f"hostname: {platform.node()}",
        f"platform: {platform.platform()}",
        f"python: {sys.executable}",
    ]
    slurm_id = os.environ.get("SLURM_JOB_ID", "none")
    host_lines.append(f"slurm_job_id: {slurm_id}")
    (val_dir / "host_info.txt").write_text("\n".join(host_lines) + "\n")

    return commit


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------
def run_experiment(config_path):
    wall_start = time.time()
    utc_start = datetime.now(timezone.utc).isoformat()

    with open(config_path) as f:
        cfg = json.load(f)

    run_id = cfg["run_id"]
    output_root = Path(cfg["output_root"])
    input_root = Path(cfg["input_root"])
    cluster = cfg["source_cluster"]
    regime = cfg.get("regime", "hardware_cpu_standard")
    label_col = cfg["label_column"]

    log.info("=" * 60)
    log.info("EXP-085: LOCAL ANVIL RF TEMPORAL PEAK MEMORY PREDICTION")
    log.info(f"Run ID: {run_id}")
    log.info("=" * 60)

    # Resolve paths
    parquet_path = input_root / "PROD-20260203-v3_v3.parquet"
    # clusters_config in config takes priority; then sibling config/ dir; then Gilbreth fallback
    if cfg.get("clusters_config"):
        clusters_json = Path(cfg["clusters_config"])
    else:
        clusters_json = Path(__file__).resolve().parent.parent / "config" / "clusters.json"
        if not clusters_json.exists():
            clusters_json = Path(
                "<FRESCO_V3_CODE_ROOT>/config/clusters.json"
            )

    log.info(f"Parquet:  {parquet_path}")
    log.info(f"Clusters: {clusters_json}")

    clusters_cfg = _load_clusters_config(clusters_json)

    # Ensure output dirs exist
    for sub in ["results", "manifests", "validation", "logs"]:
        (output_root / sub).mkdir(parents=True, exist_ok=True)

    # Capture provenance first
    git_commit = _capture_provenance(output_root)

    # ------------------------------------------------------------------
    log.info("\n[Phase 1] Loading %s data (chunked)...", cluster)
    df, raw_rows = load_anvil_job_level(str(parquet_path), cluster)

    # ------------------------------------------------------------------
    log.info("\n[Phase 2] Deriving canonical v3 columns...")
    df = derive_v3_columns(df, clusters_cfg, cluster)

    total_jobs = len(df)

    # ------------------------------------------------------------------
    log.info("\n[Phase 3] Regime filter (%s)...", regime)
    if regime == "hardware_cpu_standard":
        gpu_ok = (
            pd.to_numeric(df.get("gpu_count_per_node", 0), errors="coerce").fillna(0)
            <= 0
        )
        mem_ok = (
            pd.to_numeric(df.get("node_memory_gb", 0), errors="coerce").fillna(0)
            < 512
        )
        before = len(df)
        df = df[gpu_ok & mem_ok].copy()
        log.info(f"  {before:,} → {len(df):,} jobs")
    jobs_after_regime = len(df)

    # ------------------------------------------------------------------
    log.info("\n[Phase 4] Label filter (%s > 0, not null)...", label_col)
    df[label_col] = pd.to_numeric(df[label_col], errors="coerce")
    before = len(df)
    df = df[df[label_col].notna() & (df[label_col] > 0)].copy()
    log.info(f"  {before:,} → {len(df):,} jobs")
    jobs_after_label = len(df)

    # ------------------------------------------------------------------
    log.info("\n[Phase 5] Feature engineering...")

    exclude = set(
        cfg.get("leakage_columns", [])
        + cfg.get("id_columns", [])
        + cfg.get("temporal_columns", [])
        + [label_col]
    )

    X = df.select_dtypes(include=[np.number]).copy()
    X = X.drop(columns=[c for c in exclude if c in X.columns], errors="ignore")
    X = X.dropna(axis=1, how="all")
    # Ensure standard float64 (guard against nullable dtypes from filtering)
    for col in X.columns:
        X[col] = X[col].astype("float64")
    feature_cols = sorted(X.columns.tolist())
    X = X[feature_cols]

    log.info(f"  {len(feature_cols)} numeric features selected:")
    for f in feature_cols:
        log.info(f"    - {f}")

    y = df[label_col].copy()

    # log1p all features (v3 convention: model_transfer.py lines 338-342)
    for col in feature_cols:
        X[col] = np.log1p(X[col].clip(lower=0))

    # ------------------------------------------------------------------
    log.info("\n[Phase 6] Temporal split (80/20 by submit_time)...")
    sort_col = cfg["split"].get("sort_column", "submit_time")
    test_frac = float(cfg["split"].get("test_frac", 0.2))

    order = df[sort_col].values.argsort()
    X = X.iloc[order].reset_index(drop=True)
    y = y.iloc[order].reset_index(drop=True)
    times = df[sort_col].iloc[order].reset_index(drop=True)

    split = int(len(X) * (1 - test_frac))
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    t_train, t_test = times.iloc[:split], times.iloc[split:]

    log.info(f"  Train: {len(X_train):,} jobs  ({t_train.min()} → {t_train.max()})")
    log.info(f"  Test:  {len(X_test):,} jobs  ({t_test.min()} → {t_test.max()})")

    # Impute
    strategy = cfg.get("imputer", {}).get("strategy", "median")
    imputer = SimpleImputer(strategy=strategy)
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)

    # log1p target
    y_train_log = np.log1p(y_train.values)
    y_test_log = np.log1p(y_test.values)

    # ------------------------------------------------------------------
    mcfg = cfg["model"]
    log.info(
        "\n[Phase 7] Training %s (n=%d, depth=%s, n_jobs=%d)...",
        mcfg["type"],
        mcfg.get("n_estimators", 100),
        mcfg.get("max_depth", "None"),
        mcfg.get("n_jobs", -1),
    )

    model = RandomForestRegressor(
        n_estimators=mcfg.get("n_estimators", 100),
        max_depth=mcfg.get("max_depth", 20),
        min_samples_leaf=mcfg.get("min_samples_leaf", 4),
        random_state=mcfg.get("random_state", 42),
        n_jobs=mcfg.get("n_jobs", -1),
    )

    t0 = time.time()
    model.fit(X_train_imp, y_train_log)
    train_secs = time.time() - t0
    log.info(f"  Training completed in {train_secs:.1f}s")

    # ------------------------------------------------------------------
    log.info("\n[Phase 8] Evaluation...")

    pred_test_log = model.predict(X_test_imp)
    pred_test_gb = np.expm1(pred_test_log)
    y_test_gb = np.expm1(y_test_log)

    r2_gb = float(r2_score(y_test_gb, pred_test_gb))
    mae_gb = float(mean_absolute_error(y_test_gb, pred_test_gb))
    r2_log = float(r2_score(y_test_log, pred_test_log))
    mae_log = float(mean_absolute_error(y_test_log, pred_test_log))
    bias_log = float(np.mean(pred_test_log - y_test_log))

    pred_train_log = model.predict(X_train_imp)
    r2_train_log = float(r2_score(y_train_log, pred_train_log))

    # Bootstrap 95% CI
    n_boot = cfg.get("n_boot", 200)
    rng = np.random.default_rng(cfg.get("random_seed", 42))
    boot_r2 = []
    for _ in range(n_boot):
        idx = rng.choice(len(y_test_gb), size=len(y_test_gb), replace=True)
        if len(np.unique(y_test_gb[idx])) < 2:
            continue
        boot_r2.append(float(r2_score(y_test_gb[idx], pred_test_gb[idx])))
    boot_r2 = np.array(boot_r2)
    r2_ci_lo = float(np.percentile(boot_r2, 2.5))
    r2_ci_hi = float(np.percentile(boot_r2, 97.5))

    # Feature importances
    importances = pd.Series(model.feature_importances_, index=feature_cols)
    importances = importances.sort_values(ascending=False)

    # --- Print headline results ---
    log.info("")
    log.info("=" * 60)
    log.info("FINAL PAPER RESULTS: ANVIL LOCAL TEMPORAL FORECAST")
    log.info("=" * 60)
    log.info(f"Training Period:  {t_train.min()} → {t_train.max()}")
    log.info(f"Testing Period:   {t_test.min()} → {t_test.max()}")
    log.info(f"Train jobs: {len(X_train):,}   Test jobs: {len(X_test):,}")
    log.info("")
    log.info(f"Predictive R² (GB):    {r2_gb:.4f}   95%% CI [{r2_ci_lo:.4f}, {r2_ci_hi:.4f}]")
    log.info(f"Mean Absolute Error:   {mae_gb:.4f} GB")
    log.info(f"R² (log space):        {r2_log:.4f}")
    log.info(f"MAE (log space):       {mae_log:.4f}")
    log.info(f"Bias (log space):      {bias_log:.4f}")
    log.info(f"R² train (overfit?):   {r2_train_log:.4f}")
    log.info("")
    log.info("Top 10 Most Important Features:")
    for feat, imp in importances.head(10).items():
        log.info(f"  {feat:35s} {imp:.4f}")
    log.info("=" * 60)

    # ------------------------------------------------------------------
    log.info("\n[Phase 9] Writing outputs...")

    results_dir = output_root / "results"
    manifests_dir = output_root / "manifests"

    # metrics.json
    metrics = {
        "run_id": run_id,
        "eval": {
            "test": {
                "r2_gb": round(r2_gb, 6),
                "mae_gb": round(mae_gb, 6),
                "r2_log": round(r2_log, 6),
                "mae_log": round(mae_log, 6),
                "bias_log": round(bias_log, 6),
                "r2_bootstrap": {
                    "r2_mean": round(float(boot_r2.mean()), 6),
                    "r2_ci_lower": round(r2_ci_lo, 6),
                    "r2_ci_upper": round(r2_ci_hi, 6),
                    "n_boot": n_boot,
                },
            },
            "train": {"r2_log": round(r2_train_log, 6)},
        },
        "dataset": {
            "parquet_path": str(parquet_path),
            "raw_rows_scanned": raw_rows,
            "total_jobs_after_collapse": total_jobs,
            "jobs_after_regime_filter": jobs_after_regime,
            "jobs_after_label_filter": jobs_after_label,
            "regime": regime,
            "cluster": cluster,
        },
        "split": {
            "type": "temporal",
            "sort_column": sort_col,
            "test_frac": test_frac,
            "n_train": len(X_train),
            "n_test": len(X_test),
            "train_start": str(t_train.min()),
            "train_end": str(t_train.max()),
            "test_start": str(t_test.min()),
            "test_end": str(t_test.max()),
        },
        "model": {
            "type": mcfg["type"],
            "n_estimators": mcfg.get("n_estimators", 100),
            "max_depth": mcfg.get("max_depth", 20),
            "min_samples_leaf": mcfg.get("min_samples_leaf", 4),
            "training_seconds": round(train_secs, 2),
        },
        "features": {
            "count": len(feature_cols),
            "names": feature_cols,
            "transform": "log1p",
            "imputer": strategy,
        },
        "provenance": {
            "git_commit": git_commit,
            "started_utc": utc_start,
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "wall_seconds": round(time.time() - wall_start, 2),
            "slurm_job_id": os.environ.get("SLURM_JOB_ID", "none"),
        },
    }
    with open(results_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    # feature_importances.json
    fi = {feat: round(float(imp), 6) for feat, imp in importances.items()}
    with open(results_dir / "feature_importances.json", "w") as f:
        json.dump(fi, f, indent=2)

    # predictions parquet (test set only, for downstream analysis)
    pred_df = pd.DataFrame(
        {
            "y_true_gb": y_test_gb,
            "y_pred_gb": pred_test_gb,
            "y_true_log": y_test_log,
            "y_pred_log": pred_test_log,
        }
    )
    pred_df.to_parquet(results_dir / "predictions_test.parquet", index=False)

    # run_metadata.json (manifest)
    run_meta = {
        "run_id": run_id,
        "script": str(Path(__file__).resolve()),
        "config_path": str(Path(config_path).resolve()),
        "git_commit": git_commit,
        "started_utc": utc_start,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(manifests_dir / "run_metadata.json", "w") as f:
        json.dump(run_meta, f, indent=2)

    # input_files_used.json
    input_files = {
        "parquet": str(parquet_path),
        "clusters_json": str(clusters_json),
        "config": str(Path(config_path).resolve()),
    }
    with open(manifests_dir / "input_files_used.json", "w") as f:
        json.dump(input_files, f, indent=2)

    log.info(f"  Outputs written to {output_root}")
    log.info(f"  Total wall time: {time.time() - wall_start:.1f}s")
    log.info("Done.")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="EXP-085: Local Anvil RF Temporal Peak Memory Prediction"
    )
    parser.add_argument(
        "--config", required=True, help="Path to experiment config JSON"
    )
    args = parser.parse_args()
    run_experiment(args.config)
