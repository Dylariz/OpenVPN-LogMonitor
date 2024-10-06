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

def update_log(cn, vhost):
    fn = os.path.join(get_script_path(), db_folder, cn) + ".log"
    
    if os.path.exists(fn):    
        with open(fn, "rb") as f:
            old_host = pickle.load(f)
        
        for old_data in old_host:
            if old_data['real'] == vhost['real']:
                if old_data['since'] == vhost['since']:
                    old_data['recv'] = vhost['recv']
                    old_data['sent'] = vhost['sent']
                else:
                    old_data['recv'] += vhost['recv']
                    old_data['sent'] += vhost['sent']
                    old_data['since'] = vhost['since']
                break
        else:
            old_host.append(vhost)
        
        with open(fn, "wb") as f:
            pickle.dump(old_host, f)
    else:
        with open(fn, "wb") as f:
            pickle.dump([vhost], f)

if __name__ == '__main__':
    while True:
        hosts = read_stats()
        for h in hosts:
            update_log(h['cn'], h)
        
        time.sleep(LOG_UPDATE_INTERVAL)
