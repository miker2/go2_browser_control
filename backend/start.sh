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
exec gunicorn --workers 1 --worker-class eventlet -b 127.0.0.1:5000 app:app