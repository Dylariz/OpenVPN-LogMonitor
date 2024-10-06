#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# SETTINGS
SERVICE_NAME_HTML="openvpn_display_html"
SERVICE_NAME_STATS="openvpn_stats"
SCRIPT_HTML_PATH="$SCRIPT_DIR/openvpn_display_html.py"
SCRIPT_STATS_PATH="$SCRIPT_DIR/openvpn_stats.py"
PYTHON_PATH="/usr/bin/python3"
# SETTINGS

echo "Creating $SERVICE_NAME_HTML service..."
cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME_HTML.service > /dev/null
[Unit]
Description=OpenVPN Display HTML Service
After=network.target

[Service]
ExecStart=$PYTHON_PATH $SCRIPT_HTML_PATH
WorkingDirectory=$SCRIPT_DIR
Restart=always
User=$(whoami)
StandardOutput=inherit
StandardError=inherit
SyslogIdentifier=$SERVICE_NAME_HTML

[Install]
WantedBy=multi-user.target
EOF

echo "Creating $SERVICE_NAME_STATS service..."
cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME_STATS.service > /dev/null
[Unit]
Description=OpenVPN Stats Service
After=network.target

[Service]
ExecStart=$PYTHON_PATH $SCRIPT_STATS_PATH
WorkingDirectory=$SCRIPT_DIR
Restart=always
User=$(whoami)
StandardOutput=inherit
StandardError=inherit
SyslogIdentifier=$SERVICE_NAME_STATS

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd..."
sudo systemctl daemon-reload


echo "Enabling $SERVICE_NAME_HTML service to start on boot..."
sudo systemctl enable $SERVICE_NAME_HTML.service

echo "Enabling $SERVICE_NAME_STATS service to start on boot..."
sudo systemctl enable $SERVICE_NAME_STATS.service


echo "Starting $SERVICE_NAME_HTML service..."
sudo systemctl start $SERVICE_NAME_HTML.service

echo "Starting $SERVICE_NAME_STATS service..."
sudo systemctl start $SERVICE_NAME_STATS.service


echo "Checking the status of $SERVICE_NAME_HTML service..."
sudo systemctl status $SERVICE_NAME_HTML.service

echo "Checking the status of $SERVICE_NAME_STATS service..."
sudo systemctl status $SERVICE_NAME_STATS.service
