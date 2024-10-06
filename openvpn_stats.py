#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import pickle
import time

STATUS = "/var/log/openvpn/status.log"  # OpenVPN status log path
LOG_UPDATE_INTERVAL = 60  # Backup time interval
db_folder = "db"

def byte2str(size):
    sizes = [
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'KB'),
        (1, 'B')
    ]
    for f, suf in sizes:
        if size >= f:
            break
    return "%.2f %s" % (size / float(f), suf)

def read_stats():
    with open(STATUS, 'r') as status_file:
        stats = status_file.readlines()

    hosts = []

    for line in stats:  
        cols = line.split(',')

        if len(cols) == 5 and not line.startswith('Common Name'):
            if cols[0].strip() == 'UNDEF':
                continue
            host = {
                'cn': cols[0].strip(),
                'real': cols[1].split(':')[0],
                'recv': int(cols[2]),
                'sent': int(cols[3]),
                'since': cols[4].strip()
            }
            hosts.append(host)

    return hosts

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def update_log(current_connections, vhost):
    if not any(all(vhost[k] == conn[k] for k in vhost if k not in ['recv', 'sent']) for conn in current_connections):
        fn = os.path.join(get_script_path(), db_folder, vhost['cn']) + ".log"
        
        if os.path.exists(fn):    
            with open(fn, "rb") as f:
                old_connections = pickle.load(f)
            
            for old_data in old_connections:
                if old_data['real'] == vhost['real']:
                    old_data['recv'] += vhost['recv']
                    old_data['sent'] += vhost['sent']
                    old_data['since'] = vhost['since']
                    break
            else:
                old_connections.append(vhost)
            
            with open(fn, "wb") as f:
                pickle.dump(old_connections, f)
        else:
            with open(fn, "wb") as f:
                pickle.dump([vhost], f)
            
if __name__ == '__main__':
    connections = read_stats()
    while True:
        hosts = read_stats()
        for h in connections:
            update_log(hosts, h)
            
        connections = hosts
        time.sleep(LOG_UPDATE_INTERVAL)
