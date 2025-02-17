#!/bin/bash

# Project paths (REPLACE THESE WITH YOUR ACTUAL PATHS)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # Absolute path to the directory containing this script
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
SERVICE_FILE="$PROJECT_DIR/robot-control.conf"
SYSTEMD_SERVICE_DIR="/etc/systemd/system"

# Conda environment name
ENV_NAME="robot-control"


sudo apt-get update
sudo apt-get install -y lighttpd
# Install dependencies for go2_webrtc_connect
sudo apt-get install -y portaudio19-dev

# Create or update conda environment
if conda env list | grep -q "$ENV_NAME"; then
  echo "Updating conda environment '$ENV_NAME'..."
  conda env update -f "$PROJECT_DIR/environment.yml" --prune # --prune removes old packages
else
  echo "Creating conda environment '$ENV_NAME'..."
  conda env create -f "$PROJECT_DIR/environment.yml"
fi

# Activate conda environment
eval "$(conda shell.bash hook)"  # Important for conda to work in the script
conda activate "$ENV_NAME"

# Install this additional python package that can't be installed via conda
# pip install git+https://github.com/legion1581/go2_webrtc_connect.git

python setup/generate_service.py -o "$SERVICE_FILE"

# Copy Lighttpd config file and enable
echo "Copying and enabling Lighttpd config..."
sudo cp "$PROJECT_DIR/robot-control.conf" "/etc/lighttpd/conf-available/"
sudo lighttpd-enable-mod robot-control
sudo systemctl restart lighttpd


# Copy frontend files (Optional - if you're serving them directly)
# If you are using a reverse proxy like nginx, you may skip this step.
echo "Copying frontend files (optional - skip if using reverse proxy)..."
# Replace with your frontend deployment method (e.g., rsync, scp, etc.)
# Example using rsync:
# sudo mkdir -p "/var/www/html"  # Or your web server's directory
# sudo rsync -avz "$FRONTEND_DIR/" "/var/www/html/" # Or your web server's directory

echo "Deployment complete!"
