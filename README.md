English | [Русский](./README-ru.md)

<h1 align="center">OpenVPN-LogMonitor</h1>
<h3>Requirements</h3>
<p>This project requires <strong>Python 3.x</strong> and the <code>web.py</code> module. You can install it using the following command:</p>
<pre><code>pip3 install web.py</code></pre>

<h3>Installation</h3>
<p>To install OpenVPN-LogMonitor on your server, follow these steps:</p>
<ol>
  <li>Clone the repository:
    <pre><code>git clone https://github.com/Dylariz/OpenVPN-LogMonitor.git
cd OpenVPN-LogMonitor</code></pre>
  </li>
  <li>Ensure the OpenVPN status log file is located at <code>/var/log/openvpn/status.log</code>. If it's located elsewhere, modify the <code>STATUS</code> variable in both script files or specify the log path in your <code>server.conf</code> file using:
    <pre><code>status /var/log/openvpn/status.log</code></pre>
  </li>
  <li>Run the setup script to create and enable systemd services:
    <pre><code>bash setup_openvpn_services.sh</code></pre>
  </li>
  <li>(Optional) To reload the monitoring services, you can use the following commands:
    <pre><code>systemctl disable --now openvpn_stats.service
systemctl disable --now openvpn_display_html.service
systemctl enable --now openvpn_stats.service
systemctl enable --now openvpn_display_html.service</code></pre>
  </li>
  <li>By default, connect to:
    <pre><code>http://{Your IP}:8075/</code></pre>
  </li>
</ol>

<h3>Screenshot</h3>
<img src="https://github.com/Dylariz/OpenVPN-LogMonitor/blob/master/preview.png?raw=true" alt="Screenshot"/>

<h3>Configuration</h3>
<p>You can modify certain settings at the beginning of the script files:</p>
<ul>
  <li><strong>openvpn_stats.py</strong> and <strong>openvpn_display_html.py</strong>:
    <pre><code>STATUS = "/var/log/openvpn/status.log"  # OpenVPN status log path
LOG_UPDATE_INTERVAL = 60  # Backup time interval</code></pre>
  </li>
  <li><strong>setup_openvpn_services.sh</strong>:
    <pre><code>SERVICE_NAME_HTML="openvpn_display_html"
SERVICE_NAME_STATS="openvpn_stats"
SCRIPT_HTML_PATH="$SCRIPT_DIR/openvpn_display_html.py"
SCRIPT_STATS_PATH="$SCRIPT_DIR/openvpn_stats.py"
PYTHON_PATH="/usr/bin/python3"</code></pre>
  </li>
</ul>
