<h1 align="center">OpenVPN-LogMonitor</h1>
<h3>Требования</h3>
<p>Этот проект требует <strong>Python 3.x</strong> и модуль <code>web.py</code>. Вы можете установить его с помощью следующей команды:</p>
<pre><code>pip3 install web.py</code></pre>

<h3>Установка</h3>
<p>Чтобы установить OpenVPN-LogMonitor на вашем сервере, выполните следующие шаги:</p>
<ol>
  <li>Клонируйте репозиторий:
    <pre><code>git clone https://github.com/Dylariz/OpenVPN-LogMonitor.git
cd OpenVPN-LogMonitor</code></pre>
  </li>
  <li>Убедитесь, что файл журнала состояния OpenVPN находится по адресу <code>/var/log/openvpn/status.log</code>. Если он находится в другом месте, измените переменную <code>STATUS</code> в обоих файлах сценариев или укажите путь к журналу в вашем файле <code>server.conf</code>, используя:
    <pre><code>status /var/log/openvpn/status.log</code></pre>
  </li>
  <li>Запустите скрипт настройки для создания и включения служб systemd:
    <pre><code>bash setup_openvpn_services.sh</code></pre>
  </li>
  <li>(Опционально) Чтобы перезагрузить службы мониторинга, вы можете использовать следующие команды:
    <pre><code>systemctl disable --now openvpn_stats.service
systemctl disable --now openvpn_display_html.service
systemctl enable --now openvpn_stats.service
systemctl enable --now openvpn_display_html.service</code></pre>
  </li>
</ol>

<h3>Конфигурация</h3>
<p>Вы можете изменить определенные настройки в начале файлов сценариев:</p>
<ul>
  <li><strong>openvpn_stats.py</strong> и <strong>openvpn_display_html.py</strong>:
    <pre><code>STATUS = "/var/log/openvpn/status.log"  # Путь к журналу состояния OpenVPN
LOG_UPDATE_INTERVAL = 60  # Интервал резервного копирования</code></pre>
  </li>
  <li><strong>setup_openvpn_services.sh</strong>:
    <pre><code>SERVICE_NAME_HTML="openvpn_display_html"
SERVICE_NAME_STATS="openvpn_stats"
SCRIPT_HTML_PATH="$SCRIPT_DIR/openvpn_display_html.py"
SCRIPT_STATS_PATH="$SCRIPT_DIR/openvpn_stats.py"
PYTHON_PATH="/usr/bin/python3"</code></pre>
  </li>
</ul>
