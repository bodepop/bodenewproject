import scapy.all as scapy
import requests
import socket
import nmap
import logging
import sys
import os
from typing import Dict, List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NetworkScanner:
    def __init__(self):
        try:
            self.nm = nmap.PortScanner()
        except nmap.PortScannerError:
            logger.error("Nmap is not installed. Please install nmap first.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error initializing scanner: {e}")
            sys.exit(1)

    def verify_nmap_installation(self):
        """Verify nmap is installed and accessible"""
        try:
            # Try to execute nmap version command
            self.nm.scan('127.0.0.1', arguments='-V')
            return True
        except nmap.PortScannerError:
            logger.error("""
Nmap is not installed or not found in PATH. 
Please install nmap:
- Windows: Download from https://nmap.org/download.html
- Linux: sudo apt-get install nmap
- macOS: brew install nmap
""")
            return False

    def scan(self, ip: str) -> List[Dict]:
        """
        Scan network and return detailed device information
        """
        if not self.verify_nmap_installation():
            return []

        try:
            logger.info(f"Scanning IP range: {ip}")
            # Perform ARP scan to discover devices
            arp_request = scapy.ARP(pdst=ip)
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

            devices_list = []
            for element in answered_list:
                target_ip = element[1].psrc
                target_mac = element[1].hwsrc
                device_info = self.get_device_info(target_ip, target_mac)
                devices_list.append(device_info)

            return devices_list

        except Exception as e:
            logger.error(f"Error during network scan: {e}")
            return []

    def get_device_info(self, ip: str, mac: str) -> Dict:
        """
        Get detailed information about a device
        """
        device_info = {
            "ip": ip,
            "mac": mac,
            "vendor": self.get_vendor(mac),
            "hostname": self.get_hostname(ip),
            "device_type": "Unknown",
            "os_info": "Unknown",
            "open_ports": [],
            "services": []
        }

        try:
            logger.info(f"Scanning device at {ip}")
            # Basic scan first
            scan_arguments = '-sS -sV -O --version-intensity 5'
            self.nm.scan(ip, arguments=scan_arguments)
            
            if ip in self.nm.all_hosts():
                # Get OS information
                if 'osmatch' in self.nm[ip]:
                    os_matches = self.nm[ip]['osmatch']
                    if os_matches:
                        device_info['os_info'] = os_matches[0]['name']
                        
                # Get ports and services
                for proto in self.nm[ip].all_protocols():
                    ports = self.nm[ip][proto].keys()
                    for port in ports:
                        port_info = self.nm[ip][proto][port]
                        service_info = {
                            'port': port,
                            'name': port_info.get('name', 'unknown'),
                            'product': port_info.get('product', ''),
                            'version': port_info.get('version', '')
                        }
                        device_info['open_ports'].append(port)
                        device_info['services'].append(service_info)

                # Determine device type
                device_info['device_type'] = self.determine_device_type(device_info)

        except Exception as e:
            logger.error(f"Error scanning device {ip}: {e}")

        return device_info

    def get_vendor(self, mac: str) -> str:
        """Get vendor information from MAC address"""
        try:
            mac = mac.replace(':', '').upper()[:6]
            response = requests.get(f'https://api.macvendors.com/{mac}')
            if response.status_code == 200:
                return response.text
            return "Unknown vendor"
        except Exception as e:
            logger.error(f"Error getting vendor info: {e}")
            return "Unknown vendor"

    def get_hostname(self, ip: str) -> str:
        """Get hostname from IP address"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "Unknown hostname"

    def determine_device_type(self, device_info: Dict) -> str:
        """Determine device type based on ports and services"""
        ports = device_info['open_ports']
        services = [s['name'].lower() for s in device_info['services']]
        
        patterns = {
            'Printer': {'ports': [9100, 515, 631], 'services': ['ipp', 'printer']},
            'Router': {'ports': [80, 443, 23, 22], 'services': ['telnet', 'ssh', 'http']},
            'Switch': {'ports': [23, 22, 161], 'services': ['snmp', 'telnet', 'ssh']},
            'Server': {'ports': [80, 443, 21, 22, 3389], 'services': ['http', 'https', 'ftp', 'ssh', 'rdp']},
            'Storage Device': {'ports': [445, 139], 'services': ['netbios', 'smb']},
            'IoT Device': {'ports': [1883, 8883], 'services': ['mqtt']},
            'Camera': {'ports': [554, 80], 'services': ['rtsp', 'onvif']},
            'Desktop/Workstation': {'ports': [135, 139, 445], 'services': ['netbios-ssn', 'microsoft-ds']}
        }

        for device_type, pattern in patterns.items():
            if any(port in ports for port in pattern['ports']) or \
               any(service in services for service in pattern['services']):
                return device_type

        return "Unknown Device"

def print_result(results_list: List[Dict]):
    """Print scan results in a formatted way"""
    if not results_list:
        print("\nNo devices found or scan failed.")
        return

    print("\n" + "="*80)
    print("NETWORK DEVICE SCAN RESULTS")
    print("="*80)

    for device in results_list:
        print(f"\nDevice at {device['ip']}")
        print("-" * 40)
        print(f"MAC Address: {device['mac']}")
        print(f"Vendor: {device['vendor']}")
        print(f"Hostname: {device['hostname']}")
        print(f"Device Type: {device['device_type']}")
        print(f"OS Info: {device['os_info']}")
        
        if device['open_ports']:
            print("\nOpen Ports:")
            for service in device['services']:
                print(f"  Port {service['port']}: {service['name']} "
                      f"({service['product']} {service['version']})")
        
        print("-" * 40)

def main():
    scanner = NetworkScanner()
    try:
        ip_range = input("Enter the IP range to scan (e.g., 192.168.1.0/24): ")
        scan_result = scanner.scan(ip_range)
        print_result(scan_result)
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()


