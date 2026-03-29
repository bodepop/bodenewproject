import socket
import subprocess
import ipaddress
import re
from concurrent.futures import ThreadPoolExecutor

def get_local_ip():
    """Get the local IP address and network info"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "192.168.1.1"

def get_arp_table():
    """Get ARP table to find MAC addresses"""
    arp_info = {}
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)', line)
            if match:
                ip, mac = match.groups()
                arp_info[ip] = mac
    except:
        pass
    return arp_info

def ping_host(ip):
    """Ping a single host to check if it's alive"""
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                              capture_output=True, text=True, timeout=3)
        return ip if result.returncode == 0 else None
    except:
        return None

def get_hostname(ip):
    """Get hostname for an IP address"""
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except:
        return "Unknown"

def scan_common_ports(ip):
    """Scan common ports to identify device type"""
    common_ports = {
        22: "SSH", 23: "Telnet", 53: "DNS", 80: "HTTP", 
        443: "HTTPS", 445: "SMB", 3389: "RDP", 5900: "VNC"
    }
    
    open_ports = []
    for port, service in common_ports.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((str(ip), port))
            if result == 0:
                open_ports.append(f"{port}({service})")
            sock.close()
        except:
            pass
    
    return ", ".join(open_ports) if open_ports else "No common ports"

def detailed_scan():
    """Perform detailed network scan"""
    local_ip = get_local_ip()
    network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    
    print(f"Detailed Network Scan: {network}")
    print("Scanning for devices and services...\n")
    
    # Get ARP table for MAC addresses
    arp_table = get_arp_table()
    
    alive_hosts = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(ping_host, network.hosts())
        alive_hosts = [ip for ip in results if ip is not None]
    
    if alive_hosts:
        print(f"Found {len(alive_hosts)} connected devices:\n")
        print(f"{'IP Address':<15} {'Hostname':<25} {'MAC Address':<18} {'Open Ports'}")
        print("-" * 85)
        
        for ip in sorted(alive_hosts, key=lambda x: ipaddress.IPv4Address(x)):
            hostname = get_hostname(ip)
            mac = arp_table.get(str(ip), "Unknown")
            
            # Mark your device
            if str(ip) == local_ip:
                hostname += " (Your Device)"
            
            print(f"{str(ip):<15} {hostname:<25} {mac:<18} Scanning...")
            
            # Scan ports (this will take longer)
            ports = scan_common_ports(ip)
            
            # Update the line with port info
            print(f"\r{str(ip):<15} {hostname:<25} {mac:<18} {ports}")
    else:
        print("No devices found on the network.")

if __name__ == "__main__":
    print("Advanced Network Device Scanner")
    print("=" * 40)
    print("Choose scan type:")
    print("1. Quick scan (ping only)")
    print("2. Detailed scan (includes ports)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        detailed_scan()
    else:
        # Import and run basic scan
        exec(open('network_scanner.py').read())