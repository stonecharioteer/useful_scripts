"""
Script to list who is connected to the network.

"""

import os
import subprocess

def get_ips():
    output = subprocess.check_output("ifconfig").decode("ascii").split("\n\n")
    connections = {}
    ip_lines = []
    for segment in output:
        if segment.strip() == "":
            pass
        else:
            connection_type = segment.split()[0]
            mac_address = segment[segment.find("HWaddr")+7:segment.find("\n")].strip()
            segment = segment[segment.find("\n")+1:]
            ip_addr = segment[segment.find("inet addr")+10:]
            ip_addr = ip_addr[:ip_addr.find(" ")]
            if ip_addr.count(".")==3:
                ip_lines.append([connection_type, mac_address, ip_addr])
    return ip_lines

def get_clients(ip):
    import subprocess
    ip_to_sniff = ip[:ip.rfind(".")]
    
    output = subprocess.check_output(["nmap","-sn", "{}.0/24".format(ip_to_sniff)])
    output = output.decode("ascii")
    clients = []
    for line in output.split("\n"):
        if "nmap scan report" in line.lower():
            clients.append(line[line.find("for ")+4:].strip())
    return sorted(clients)

if __name__ == "__main__":
    import pprint
    ips = get_ips()
    clients = {}
    for connection in ips:
        if "eth" in connection[0].lower() or "wlan" in connection[0].lower():
            clients[" ".join(connection)] = get_clients(connection[-1])
    
    for connection in sorted(clients.keys()):
        print("Clients on {}:".format(connection))
        pprint.pprint(clients[connection])
