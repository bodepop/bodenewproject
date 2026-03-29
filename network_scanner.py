import socket
import subprocess
import ipaddress
import threading
from concurrent.futures import ThreadPoolExecutor

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "192.168.1.1"

def ping_host(ip):
    """Ping a single host to check if it's alive"""
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                              capture_output=True, text=True, timeout=2)
        return ip if result.returncode == 0 else None
    except:
        return None

def get_hostname(ip):
    """Get hostname for an IP address"""
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except:
        return "Unknown"

def scan_network():
    """Scan the local network for connected devices"""
    local_ip = get_local_ip()
    network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    
    print(f"Scanning network: {network}")
    print("This may take a moment...\n")
    
    alive_hosts = []
    
    # Use ThreadPoolExecutor for faster scanning
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(ping_host, network.hosts())
        alive_hosts = [ip for ip in results if ip is not None]
    
    if alive_hosts:
        print(f"Found {len(alive_hosts)} connected devices:\n")
        print(f"{'IP Address':<15} {'Hostname':<30} {'Status'}")
        print("-" * 55)
        
        for ip in sorted(alive_hosts, key=lambda x: ipaddress.IPv4Address(x)):
            hostname = get_hostname(ip)
            status = "Your Device" if str(ip) == local_ip else "Connected"
            print(f"{str(ip):<15} {hostname:<30} {status}")
    else:
        print("No devices found on the network.")

if __name__ == "__main__":
    print("Network Device Scanner")
    print("=" * 30)
    scan_network()