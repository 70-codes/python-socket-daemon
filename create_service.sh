#!/bin/bash

# Prompt for details
read -p "Enter the full path to your Python script (e.g., /home/user/server.py): " script_path
read -p "Enter the name of the service (e.g., my_python_daemon): " service_name
read -p "Enter the user to run the service as (e.g., nobody): " user
read -p "Enter the group to run the service as (e.g., nogroup): " group
log_dir="/var/log/$service_name"
service_file="/etc/systemd/system/$service_name.service"

# Validate script path
if [ ! -f "$script_path" ]; then
  echo "Error: The script file does not exist."
  exit 1
fi

# Create log directory
sudo mkdir -p "$log_dir"
sudo chown $user:$group "$log_dir"

# Create systemd service file
sudo bash -c "cat > $service_file" <<EOL
[Unit]
Description=$service_name
After=network.target

[Service]
ExecStart=/usr/bin/python3 $script_path
WorkingDirectory=$(dirname $script_path)
StandardOutput=file:$log_dir/$service_name.log
StandardError=file:$log_dir/$service_name.err
Restart=always
User=$user
Group=$group

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd, start and enable the service
sudo systemctl daemon-reload
sudo systemctl start $service_name.service
sudo systemctl enable $service_name.service

echo "Service $service_name has been created and started successfully."
