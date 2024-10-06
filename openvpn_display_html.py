#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import web
import pickle
import glob
import time

STATUS = "/var/log/openvpn/status.log" # OpenVPN status log path
db_folder = "db"

web.config.debug = False
urls = ('/', 'vpn')
app = web.application(urls, globals(), autoreload=True)

sizes = [
    (1 << 50, 'PB'),
    (1 << 40, 'TB'),
    (1 << 30, 'GB'),
    (1 << 20, 'MB'),
    (1 << 10, 'KB'),
    (1, 'B')
]

headers = {
    'cn': 'Common Name',
    'real': 'Real Address',
    'virt_v4': 'Virtual Ip4',
    'virt_v6': 'Virtual Ip6',
    'sent': 'Download',
    'recv': 'Upload',
    'since': 'Connected Since',
    'sent_speed': 'Avg Download',
    'recv_speed': 'Avg Upload'
}

headers_total_ip = {
    'cn': 'Common Name',
    'real': 'Real Address',
    'sent': 'Download',
    'recv': 'Upload',
    'since': 'Last Online'
}

headers_total = {
    'cn': 'Common Name',
    'sent': 'Download',
    'recv': 'Upload'
}

def byte2str(size):
    for f, suf in sizes:
        if size >= f:
            break
    return "%.2f %s" % (size / float(f), suf)

def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def calculate_speeds(sent, recv, duration):
    if duration > 0:
        sent_speed = sent / duration
        recv_speed = recv / duration
        return byte2str(sent_speed), byte2str(recv_speed)
    return "0 B", "0 B"

def print_current():
    with open(STATUS, 'r') as status_file:
        stats = status_file.readlines()

    hosts = []
    start_time = time.time()
    
    routing_v4 = dict()
    routing_v6 = dict()
    
    for line in stats:
        cols = line.split(',')
        
        if len(cols) == 4 and not line.startswith('Virtual Address'):
            if ':' in cols[0]:
                routing_v6[cols[2].strip()] = cols[0].strip()
            else:
                routing_v4[cols[2].strip()] = cols[0].strip()
        
    for line in stats:
        cols = line.split(',')

        if len(cols) == 5 and not line.startswith('Common Name'):
            host = {
                'cn': cols[0].strip(),
                'real': cols[1].strip().split(':')[0],
                'virt_v4': routing_v4.get(cols[1].strip(), 'N/A'),
                'virt_v6': routing_v6.get(cols[1].strip(), 'N/A'),
                'recv': int(cols[2]),
                'sent': int(cols[3]),
                'since': cols[4].strip()
            }

            try:
                duration = start_time - time.mktime(time.strptime(host['since'], "%Y-%m-%d %H:%M:%S"))
            except ValueError as e:
                print(f"Error in timestamp conversion: {e}")
                duration = 0

            sent_speed, recv_speed = calculate_speeds(host['sent'], host['recv'], duration)
            host['sent_speed'] = sent_speed
            host['recv_speed'] = recv_speed
            hosts.append(host)

    hosts.sort(key=lambda x: x['sent'], reverse=True)

    current_table = "<table class='current-stats'><tr>"
    for i, key in enumerate(headers.keys()):
        current_table += f"<th onclick='sortTable(0, {i})' data-order='asc'>{headers[key]} <span class='sort-indicator'></span></th>"
    current_table += "</tr>"

    for host in hosts:
        current_table += "<tr>"
        for key in headers.keys():
            value = host[key] if key not in ['sent', 'recv'] else byte2str(host[key])
            current_table += f"<td>{value}</td>"
        current_table += "</tr>"
    current_table += "</table>"
    
    return current_table

def print_total_ip():
    log_files = glob.glob(os.path.join(getScriptPath(), db_folder) + "/*.log")
    hosts = []

    for lf in log_files:
        with open(lf, "rb") as f:
            stats = pickle.load(f)

        for host in stats:
            host['recv'] = host['recv']
            host['sent'] = host['sent']
            host['since'] = host['since']
            host['real'] = host['real']
            hosts.append(host)

    hosts.sort(key=lambda x: x['since'], reverse=True)

    total_table = "<table class='total-ip-stats'><tr>"
    for i, key in enumerate(headers_total_ip.keys()):
        total_table += f"<th onclick='sortTable(1, {i})' data-order='asc'>{headers_total_ip[key]} <span class='sort-indicator'></span></th>"
    total_table += "</tr>"

    for host in hosts:
        total_table += "<tr>"
        for key in headers_total_ip.keys():
            value = host[key] if key not in ['sent', 'recv'] else byte2str(host[key])
            total_table += f"<td>{value}</td>"
        total_table += "</tr>"
    total_table += "</table>"

    return total_table
    
def print_total():
    log_files = glob.glob(os.path.join(getScriptPath(), db_folder) + "/*.log")
    clients = {}

    for lf in log_files:
        with open(lf, "rb") as f:
            stats = pickle.load(f)

        for host in stats:
            cn = host['cn']
            recv = host['recv']
            sent = host['sent']

            if cn in clients:
                clients[cn]['recv'] += recv
                clients[cn]['sent'] += sent
            else:
                clients[cn] = {
                    'cn': cn,
                    'recv': recv,
                    'sent': sent
                }

    sorted_clients = sorted(clients.values(), key=lambda x: x['sent'], reverse=True)

    for client in sorted_clients:
        client['recv'] = byte2str(client['recv'])
        client['sent'] = byte2str(client['sent'])

    total_table = "<table class='total-stats'><tr>"
    for i, key in enumerate(headers_total.keys()):
        total_table += f"<th onclick='sortTable(2, {i})' data-order='asc'>{headers_total[key]} <span class='sort-indicator'></span></th>"
    total_table += "</tr>"

    for client in sorted_clients:
        total_table += "<tr>"
        for key in headers_total.keys():
            total_table += f"<td>{client[key]}</td>"
        total_table += "</tr>"
    total_table += "</table>"

    return total_table

class vpn:
    def GET(self):
        cur_stats = print_current()
        total_ip_stats = print_total_ip()
        total_stats = print_total()

        return f"""
        <html>
            <head>
                <style>
                    body {{
                        background-color: #e5e5e5;
                        font-family: Arial, sans-serif;
                        margin: 20px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 20px;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #4CAF50;
                        color: white;
                        cursor: pointer;
                        position: relative;
                    }}
                    th.active {{
                        background-color: #388E3C;
                    }}
                    .sort-indicator {{
                        margin-left: 10px;
                        font-size: 0.8em;
                    }}
                    th[data-order='asc'] .sort-indicator::after {{
                        content: '\\25B2'; /* Up arrow */
                    }}
                    th[data-order='desc'] .sort-indicator::after {{
                        content: '\\25BC'; /* Down arrow */
                    }}
                    tr:nth-child(even) {{
                        background-color: #f2f2f2;
                    }}
                    tr:hover {{
                        background-color: #ddd;
                    }}
                </style>
                <script>
                    function sizeToBytes(sizeStr) {{
                        var sizes = {{ "B": 1, "KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024, "TB": 1024 * 1024 * 1024 * 1024, "PB": 1024 * 1024 * 1024 * 1024 * 1024 }};
                        var parts = sizeStr.split(" ");
                        return parseFloat(parts[0]) * (sizes[parts[1]] || 1);
                    }}

                    function sortTable(tableIndex, colIndex) {{
                        var tableClass = ["current-stats", "total-ip-stats", "total-stats"][tableIndex];
                        var table = document.getElementsByClassName(tableClass)[0];
                        var rows = Array.from(table.rows).slice(1); // пропускаем заголовок
                        var ascending = table.rows[0].cells[colIndex].getAttribute("data-order") === "asc";
                        
                        rows.sort(function (rowA, rowB) {{
                            var cellA = rowA.cells[colIndex].innerText;
                            var cellB = rowB.cells[colIndex].innerText;

                            if (cellA.includes(" ")) {{
                                cellA = sizeToBytes(cellA);
                                cellB = sizeToBytes(cellB);
                            }}
                            return ascending ? (cellA > cellB ? 1 : -1) : (cellA < cellB ? 1 : -1);
                        }});

                        for (var i = 0; i < table.rows[0].cells.length; i++) {{
                            table.rows[0].cells[i].classList.remove("active");
                        }}
                        table.rows[0].cells[colIndex].classList.add("active");
                        table.rows[0].cells[colIndex].setAttribute("data-order", ascending ? "desc" : "asc");

                        for (var i = 0; i < rows.length; i++) {{
                            table.tBodies[0].appendChild(rows[i]);
                        }}
                    }}
                </script>
            </head>
            <body>
                <h2>------- Total --------</h2>
                <div>{total_stats}</div>
                <h2>------- Current --------</h2>
                <div>{cur_stats}</div>
                <h2>------- By IP --------</h2>
                <div>{total_ip_stats}</div>
            </body>
        </html>
        """

if __name__ == '__main__':
    web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0", 8075))