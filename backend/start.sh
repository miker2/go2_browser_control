#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
CONDA_BASE="/home/michael/miniconda3"

# Source conda's activation script
source "$CONDA_BASE/etc/profile.d/conda.sh"

# Activate conda environment
conda activate go2-web-control

# Navigate to the backend directory
cd "$SCRIPT_DIR"

# Start the backend server
exec uvicorn main:app --host 0.0.0.0 --port 8000