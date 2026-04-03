#!/bin/bash
#SBATCH --job-name=exp085_blueprint
#SBATCH --output=experiments/EXP-085_local_anvil_rf_temporal_peak_memory/logs/blueprint_%j.out
#SBATCH --error=experiments/EXP-085_local_anvil_rf_temporal_peak_memory/logs/blueprint_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:1
#SBATCH --partition=a100-80gb
#SBATCH --qos=normal
#SBATCH --account=sbagchi
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mckerracher@gmail.com

# EXP-085: Local Anvil RF Temporal Peak Memory Prediction
# Trains Random Forest on full Anvil dataset from authoritative v3 parquet.

echo "========================================"
echo "EXP-085: LOCAL ANVIL RF TEMPORAL FORECAST"
echo "========================================"
echo "Job ID:   $SLURM_JOB_ID"
echo "Node:     $SLURM_NODELIST"
echo "CPUs:     $SLURM_CPUS_PER_TASK"
echo "Memory:   $SLURM_MEM_PER_NODE MB"
echo "Started:  $(date --iso-8601=seconds)"
echo ""

# Change to pipeline root
cd <FRESCO_V3_CODE_ROOT>

# Ensure output directories exist
mkdir -p experiments/EXP-085_local_anvil_rf_temporal_peak_memory/{logs,results,manifests,validation}

# Activate conda environment (module load anaconda does NOT work on Gilbreth)
source <CONDA_INIT_SCRIPT>
conda activate fresco_v2

echo "Python:   $(python --version)"
echo "Conda:    $CONDA_DEFAULT_ENV"
echo "PyArrow:  $(python -c 'import pyarrow; print(pyarrow.__version__)')"
echo "Sklearn:  $(python -c 'import sklearn; print(sklearn.__version__)')"
echo ""

# Run the evaluation
python scripts/evaluate_local_blueprint.py \
    --config experiments/EXP-085_local_anvil_rf_temporal_peak_memory/config/exp085_local_anvil_rf_temporal_peak_memory.json

exit_code=$?

echo ""
echo "========================================"
echo "Completed: $(date --iso-8601=seconds)"
echo "Exit code: $exit_code"
echo "========================================"

exit $exit_code
