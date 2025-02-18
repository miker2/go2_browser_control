#!/bin/bash

# Project paths (REPLACE THESE WITH YOUR ACTUAL PATHS)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # Absolute path to the directory containing this script
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
SERVICE_FILE="$PROJECT_DIR/robot-control.service"
SYSTEMD_SERVICE_DIR="/etc/systemd/system"

# Conda environment name
ENV_NAME="go2-web-control"


sudo apt-get update
sudo apt-get install -y nginx
# Install dependencies for go2_webrtc_connect
sudo apt-get install -y portaudio19-dev

# Create or update conda environment
if conda env list | grep -q "$ENV_NAME"; then
  echo -e "\n*****\nUpdating conda environment '$ENV_NAME'...\n*****\n"
  conda env update -f "$PROJECT_DIR/environment.yml" --prune # --prune removes old packages
else
  echo "\n*****\nCreating conda environment '$ENV_NAME'...\n*****\n"
  conda env create -f "$PROJECT_DIR/environment.yml"
fi

# Activate conda environment
eval "$(conda shell.bash hook)"  # Important for conda to work in the script
conda activate "$ENV_NAME"

# Install this additional python package that can't be installed via conda
# pip install git+https://github.com/legion1581/go2_webrtc_connect.git

python setup/generate_service.py -i wlan0 -o "$PROJECT_DIR"

# Copy Lighttpd config file and enable
echo -e "\n*****"
echo "Copying and enabling nginx config..."
sudo cp "$SERVICE_FILE" "$SYSTEMD_SERVICE_DIR/"
sudo systemctl daemon-reload
sudo systemctl enable robot-control
sudo systemctl start robot-control


# Copy frontend files (Optional - if you're serving them directly)
# If you are using a reverse proxy like nginx, you may skip this step.
# echo "Copying frontend files (optional - skip if using reverse proxy)..."
# Replace with your frontend deployment method (e.g., rsync, scp, etc.)
# Example using rsync:
# sudo mkdir -p "/var/www/html"  # Or your web server's directory
# sudo rsync -avz "$FRONTEND_DIR/" "/var/www/html/" # Or your web server's directory

echo "Deployment complete!"
