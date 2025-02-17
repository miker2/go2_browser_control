#!/bin/bash

# Project paths (REPLACE THESE WITH YOUR ACTUAL PATHS)
PROJECT_DIR="/path/to/your/project"  # Absolute path to your project directory
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
SERVICE_FILE="$PROJECT_DIR/robot-control.service"  # Path to your systemd service file
SYSTEMD_SERVICE_DIR="/etc/systemd/system"

# Conda environment name
ENV_NAME="robot-control"

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

# Copy service file and enable/start service
echo "Copying service file..."
sudo cp "$SERVICE_FILE" "$SYSTEMD_SERVICE_DIR"

echo "Enabling and starting service..."
sudo systemctl enable robot-control.service # Make sure service file is named robot-control.service
sudo systemctl restart robot-control.service # Use restart to update an existing service

# Copy frontend files (Optional - if you're serving them directly)
# If you are using a reverse proxy like nginx, you may skip this step.
echo "Copying frontend files (optional - skip if using reverse proxy)..."
# Replace with your frontend deployment method (e.g., rsync, scp, etc.)
# Example using rsync:
# sudo rsync -avz "$FRONTEND_DIR/" "/var/www/html/" # Or your web server's directory

echo "Deployment complete!"

# Check service status (optional)
sudo systemctl status robot-control.service