"""TP-Link Deco BE95 Network Dashboard"""
import streamlit as st
import pandas as pd
import os
import re
import json
import time
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

DECO_HOST = os.getenv("DECO_HOST", "192.168.2.1")
DECO_PASSWORD = os.getenv("DECO_PASSWORD", "")
AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "eu.anthropic.claude-sonnet-4-20250514-v1:0")
DECO_DYNAMODB_TABLE = os.getenv("DECO_DYNAMODB_TABLE", "deco-network-snapshots")
ENABLE_AWS = os.getenv("ENABLE_AWS", "false").lower() == "true"
PARENTAL_FILE = ".deco_parental_rules.json"
HISTORY_FILE = ".deco_history.json"
KNOWN_DEVICES_FILE = ".deco_known_devices.json"

st.set_page_config(page_title="Deco Dashboard", layout="wide", page_icon="🏠")

# --- CSS ---
st.markdown("""
<style>
    /* Background */
    .stApp { background: linear-gradient(180deg, #f0f4ff 0%, #ffffff 100%); }
    
    /* Title gradient - rainbow */
    h1 { 
        font-size: 1.5em !important;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 30%, #f093fb 60%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 0.3rem;
    }
    
    /* Tabs - swipeable on mobile */
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none;
        background: linear-gradient(135deg, #e8eaf6 0%, #f3e5f5 50%, #fce4ec 100%);
        border-radius: 12px; padding: 5px; gap: 3px;
        -webkit-overflow-scrolling: touch;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
    .stTabs [data-baseweb="tab"] {
        white-space: nowrap; font-size: 0.82em; padding: 0.5rem 0.8rem; border-radius: 8px;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.35);
        font-weight: 600;
    }
    /* Nested tabs */
    .stTabs .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #e3f2fd 0%, #e8eaf6 100%);
    }
    .stTabs .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #42a5f5 0%, #1565c0 100%);
    }
    
    /* Metric cards - each a unique vibrant color */
    [data-testid="stMetric"] {
        border-radius: 14px; padding: 16px 18px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        transition: transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover { transform: translateY(-2px); }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #fc5c7d 0%, #6a82fb 100%);
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: white !important; }
    [data-testid="stMetric"] label { font-weight: 500; letter-spacing: 0.3px; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { font-weight: 700; }
    
    /* Sidebar - purple gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4a148c 0%, #7b1fa2 50%, #9c27b0 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stAlert { background: rgba(255,255,255,0.15); border: none; border-radius: 10px; }
    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.2) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    /* Buttons - gradient with glow */
    .stButton button {
        border-radius: 10px; font-weight: 600; min-height: 44px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none;
        transition: all 0.3s ease;
        letter-spacing: 0.3px;
    }
    .stButton button:hover {
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.5);
        transform: translateY(-2px);
    }
    .stButton button:active { transform: translateY(0); }
    
    /* Dataframes */
    .stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.06); }
    
    /* Charts */
    .stChart { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.04); }
    
    /* Subheaders */
    h2 { color: #5e35b1 !important; font-size: 1.3em !important; }
    h3 { color: #7c4dff !important; font-size: 1.1em !important; }
    
    /* Captions */
    .stCaption { line-height: 1.6; }
    
    /* Dividers */
    hr { border-color: #e8eaf6 !important; }
    
    /* Expanders */
    .streamlit-expanderHeader { border-radius: 8px; }
    
    /* Checkboxes */
    .stCheckbox label { font-size: 0.95em; }
    
    /* Progress bar */
    .stProgress > div > div { background: linear-gradient(90deg, #667eea, #764ba2, #f093fb); border-radius: 10px; }
    
    /* Selectbox */
    .stSelectbox > div > div { border-radius: 8px; }
    
    /* Text input */
    .stTextInput > div > div > input { border-radius: 8px; }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .block-container { padding: 0.8rem 0.4rem !important; }
        
        h1 { font-size: 1.3em !important; text-align: center; }
        h2 { font-size: 1.1em !important; }
        h3 { font-size: 1em !important; }
        
        /* Metrics - 2 per row */
        [data-testid="stMetric"] { padding: 10px 8px; text-align: center; }
        [data-testid="stMetric"] label { font-size: 0.6em !important; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1em !important; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: 4px; }
        [data-testid="stColumn"] { min-width: 30% !important; flex: 1 1 30% !important; }
        
        /* Full width buttons */
        .stButton button { min-height: 50px; width: 100%; font-size: 0.9em; }
        
        /* Compact tables */
        .stDataFrame { font-size: 0.7em; }
        .stDataFrame [data-testid="stDataFrameResizable"] {
            overflow-x: auto !important; max-width: 100vw;
        }
        
        /* Tabs compact */
        .stTabs [data-baseweb="tab"] { font-size: 0.72em; padding: 0.35rem 0.5rem; }
        .stTabs .stTabs [data-baseweb="tab"] { font-size: 0.68em; padding: 0.3rem 0.4rem; }
        
        /* Sidebar */
        [data-testid="stSidebar"] { min-width: 180px !important; max-width: 220px !important; }
        
        /* Charts */
        .stChart { max-width: 100vw; overflow-x: auto; }
        
        /* Hide clutter */
        #MainMenu, footer, header { display: none; }
        
        /* Selectbox compact */
        .stSelectbox, .stTextInput, .stMultiSelect { font-size: 0.85em; }
        
        /* Captions readable */
        .stCaption { font-size: 0.8em !important; line-height: 1.5; }
    }
    
    /* Small phones */
    @media (max-width: 400px) {
        [data-testid="stColumn"] { min-width: 45% !important; flex: 1 1 45% !important; }
        .stTabs [data-baseweb="tab"] { font-size: 0.65em; padding: 0.3rem 0.4rem; }
    }
</style>
""", unsafe_allow_html=True)

st.title("🏠 TP-Link Deco BE95 Dashboard")

# Sidebar controls
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

auto_refresh = st.sidebar.toggle("Auto-refresh", value=False)
if auto_refresh:
    interval = st.sidebar.slider("Interval (sec)", 10, 120, 30)
    if "deco_last_refresh" not in st.session_state:
        st.session_state.deco_last_refresh = datetime.now()
    elapsed = (datetime.now() - st.session_state.deco_last_refresh).total_seconds()
    if elapsed >= interval:
        st.session_state.deco_last_refresh = datetime.now()
        st.cache_resource.clear()
        st.rerun()


def get_deco_data():
    """Launch browser, login, fetch data, close browser."""
    from deco_browser import DecoBrowser
    deco = DecoBrowser(DECO_HOST, DECO_PASSWORD)
    deco.start()
    try:
        deco.login()

        # Get home page for node info
        deco.page.click('text=Network Map', timeout=5000)
        time.sleep(3)
        deco.page.wait_for_load_state("networkidle")
        time.sleep(2)
        home_text = deco.page.evaluate("() => document.body.innerText")

        # Navigate to full clients page
        deco.page.click('text=Clients', timeout=5000)
        time.sleep(3)
        deco.page.wait_for_load_state("networkidle")
        time.sleep(2)
        client_text = deco.page.evaluate("() => document.body.innerText")

        return client_text, home_text, {}
    finally:
        deco.stop()


# --- Main ---
if not DECO_PASSWORD:
    st.warning("Set DECO_PASSWORD in .env to get started.")
    st.stop()

# Fetch data (cached for 60 seconds to reduce browser launches)
@st.cache_data(ttl=60, show_spinner=False)
def fetch_data():
    return get_deco_data()


# --- Local History Functions ---
def save_deco_snapshot(clients):
    """Save a network snapshot to local JSON file."""
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE) as f:
                history = json.load(f)

        now = datetime.now()
        total_down = sum(c.get("Down (KB/s)", 0) for c in clients)
        total_up = sum(c.get("Up (KB/s)", 0) for c in clients)
        history.append({
            "timestamp": now.isoformat(),
            "client_count": len(clients),
            "total_down_kbps": int(total_down),
            "total_up_kbps": int(total_up),
            "clients": [{
                "name": c["Name"], "ip": c["IP"], "mac": c["MAC"],
                "down": c["Down (KB/s)"], "up": c["Up (KB/s)"],
                "connection": c["Connection"],
            } for c in clients],
        })

        # Keep last 2000 snapshots (~7 days at 5 min intervals)
        history = history[-2000:]

        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
        return True
    except Exception as e:
        return False


def get_deco_history(days=7):
    """Fetch historical snapshots from local file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
        cutoff = datetime.now() - timedelta(days=days)
        filtered = []
        for item in history:
            try:
                ts = datetime.fromisoformat(item["timestamp"])
                if ts >= cutoff:
                    filtered.append(item)
            except Exception:
                pass
        return filtered
    except Exception:
        return []


# --- Export Functions ---
def export_csv(clients):
    return pd.DataFrame(clients).to_csv(index=False).encode("utf-8")


def export_json_report(clients, nodes):
    report = {
        "generated_at": datetime.now().isoformat(),
        "deco_host": DECO_HOST,
        "summary": {
            "total_clients": len(clients),
            "wired": sum(1 for c in clients if "Wired" in c.get("Connection", "")),
            "wireless": len(clients) - sum(1 for c in clients if "Wired" in c.get("Connection", "")),
        },
        "nodes": nodes,
        "clients": clients,
    }
    return json.dumps(report, indent=2).encode("utf-8")


# --- Parental Controls ---
def load_parental_rules():
    if os.path.exists(PARENTAL_FILE):
        with open(PARENTAL_FILE) as f:
            return json.load(f)
    return {}


def save_parental_rules(rules):
    with open(PARENTAL_FILE, "w") as f:
        json.dump(rules, f, indent=2)


# --- Known Devices ---
def load_known_devices():
    if os.path.exists(KNOWN_DEVICES_FILE):
        with open(KNOWN_DEVICES_FILE) as f:
            return json.load(f)
    return {}


def update_known_devices(clients):
    """Track all devices ever seen."""
    known = load_known_devices()
    now = datetime.now().isoformat()
    current_macs = set()

    for c in clients:
        mac = c["MAC"].upper()
        current_macs.add(mac)
        if mac not in known:
            known[mac] = {
                "name": c["Name"],
                "ip": c["IP"],
                "mac": mac,
                "connection": c.get("Connection", "Unknown"),
                "first_seen": now,
                "last_seen": now,
                "status": "online",
                "times_seen": 1,
            }
        else:
            known[mac]["last_seen"] = now
            known[mac]["status"] = "online"
            known[mac]["name"] = c["Name"]
            known[mac]["ip"] = c["IP"]
            known[mac]["connection"] = c.get("Connection", "Unknown")
            known[mac]["times_seen"] = known[mac].get("times_seen", 0) + 1

    # Mark disconnected devices
    for mac, info in known.items():
        if mac not in current_macs and info["status"] == "online":
            info["status"] = "offline"

    with open(KNOWN_DEVICES_FILE, "w") as f:
        json.dump(known, f, indent=2)
    return known


# --- Block Device via Browser ---
def block_device_browser(device_name):
    from deco_browser import DecoBrowser
    deco = DecoBrowser(DECO_HOST, DECO_PASSWORD)
    deco.start()
    try:
        deco.login()
        return deco.block_device(device_name)
    finally:
        deco.stop()


def unblock_device_browser(device_name):
    from deco_browser import DecoBrowser
    deco = DecoBrowser(DECO_HOST, DECO_PASSWORD)
    deco.start()
    try:
        deco.login()
        return deco.unblock_device(device_name)
    finally:
        deco.stop()

with st.spinner("Connecting to Deco..."):
    try:
        result = fetch_data()
        client_text, home_text = result[0], result[1]
        node_clients = result[2] if len(result) > 2 else {}
    except Exception as e:
        st.error(f"Connection error: {e}. Click Refresh Data in the sidebar.")
        st.cache_data.clear()
        st.stop()


def parse_client_text(text):
    """Parse the client list from page text."""
    clients = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Look for MAC address pattern (XX-XX-XX-XX-XX-XX)
        if re.match(r'^[0-9A-F]{2}(-[0-9A-F]{2}){5}$', line, re.IGNORECASE):
            mac = line
            name = lines[i - 1].strip() if i > 0 else "Unknown"
            ip = ""
            down_speed = 0
            up_speed = 0
            conn_type = "Unknown"

            # Scan next lines for IP, speeds, connection type
            for j in range(i + 1, min(i + 10, len(lines))):
                l = lines[j].strip()
                # IP address
                if re.match(r'^192\.168\.\d+\.\d+$', l):
                    ip = l
                # Speed pattern: "0KB/s" on its own or combined
                speed_matches = re.findall(r'(\d+)\s*KB/s', l)
                if speed_matches:
                    if len(speed_matches) >= 2:
                        down_speed = int(speed_matches[0])
                        up_speed = int(speed_matches[1])
                    elif len(speed_matches) == 1 and down_speed == 0:
                        down_speed = int(speed_matches[0])
                    elif len(speed_matches) == 1:
                        up_speed = int(speed_matches[0])
                # Connection type - check for Wireless or Wired
                if "Wireless" in l:
                    conn_type = l
                    break  # Connection type is usually the last field
                elif l == "Wired":
                    conn_type = "Wired"
                    break

            # Skip header rows
            if name in ["Type", "Information", "Real-time Rate", "Connection", "",
                        "Connected Clients(All Deco's)", "Connected Clients"]:
                i += 1
                continue

            clients.append({
                "Name": name,
                "MAC": mac,
                "IP": ip,
                "Down (KB/s)": down_speed,
                "Up (KB/s)": up_speed,
                "Connection": conn_type,
            })
        i += 1
    return clients


def parse_deco_nodes(text):
    """Parse Deco node info from home page text."""
    nodes = []
    lines = text.split("\n")
    # Find all Deco node names from the "All Deco Map" section
    deco_names = []
    in_map = False
    for i, line in enumerate(lines):
        line = line.strip()
        if "All Deco Map" in line or "Deco Map" in line:
            in_map = True
            continue
        if in_map and line and line not in ["", "Deco Information", "BACK TO TOP"]:
            # Node names appear between "All Deco Map" and "Deco Information"
            if "Deco Information" in line:
                in_map = False
                continue
            if len(line) > 1 and len(line) < 30 and not line.startswith("("):
                deco_names.append(line)

    # Also find MAC addresses and IPs associated with nodes
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("Device Name:"):
            name = line.replace("Device Name:", "").strip()
            mac = ""
            ip = ""
            model = ""
            for j in range(i + 1, min(i + 10, len(lines))):
                l = lines[j].strip()
                if l.startswith("MAC Address:"):
                    mac = l.replace("MAC Address:", "").strip()
                elif "IPv4" in l and "IP:" in l:
                    ip = l.split("IP:")[-1].strip()
                elif "192.168." in l:
                    ip = l.strip()
                elif "BE95" in l or "Deco" in l:
                    model = l.strip()
            nodes.append({"Name": name, "MAC": mac, "IP": ip, "Model": model or "BE95"})

    # If we didn't find structured data, use the names from the map
    if not nodes and deco_names:
        for name in deco_names:
            nodes.append({"Name": name, "MAC": "", "IP": "", "Model": "BE95"})

    return nodes


DECO_UPTIME_FILE = ".deco_uptime.json"


def load_uptime_data():
    if os.path.exists(DECO_UPTIME_FILE):
        with open(DECO_UPTIME_FILE) as f:
            return json.load(f)
    return {}


def update_uptime_data(clients):
    """Track when devices come online and go offline."""
    data = load_uptime_data()
    now = datetime.now().isoformat()
    current_macs = {c["MAC"].lower() for c in clients if c.get("MAC")}

    for c in clients:
        mac = c["MAC"].lower()
        if mac not in data:
            data[mac] = {
                "name": c["Name"],
                "first_seen": now,
                "last_seen": now,
                "status": "online",
                "online_since": now,
            }
        data[mac]["last_seen"] = now
        data[mac]["name"] = c["Name"]
        if data[mac]["status"] == "offline":
            data[mac]["online_since"] = now
        data[mac]["status"] = "online"

    for mac, info in data.items():
        if mac not in current_macs and info["status"] == "online":
            info["status"] = "offline"

    with open(DECO_UPTIME_FILE, "w") as f:
        json.dump(data, f)
    return data


def format_duration(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"
    else:
        return f"{int(seconds // 86400)}d {int((seconds % 86400) // 3600)}h"


# Parse data
clients = parse_client_text(client_text)
nodes = parse_deco_nodes(home_text)

# Track uptime
uptime_data = update_uptime_data(clients)

# Track known devices
known_devices = update_known_devices(clients)

# Add uptime info to clients
now = datetime.now()
for c in clients:
    mac = c["MAC"].lower()
    if mac in uptime_data:
        online_since = datetime.fromisoformat(uptime_data[mac].get("online_since", now.isoformat()))
        duration = (now - online_since).total_seconds()
        c["Online For"] = format_duration(duration)
        c["First Seen"] = uptime_data[mac].get("first_seen", "")[:16]
    else:
        c["Online For"] = "Just now"
        c["First Seen"] = now.isoformat()[:16]


# --- Metrics ---
wired = sum(1 for c in clients if "Wired" in c.get("Connection", ""))
wireless = len(clients) - wired
total_down = sum(c.get("Down (KB/s)", 0) for c in clients)
total_up = sum(c.get("Up (KB/s)", 0) for c in clients)

st.markdown(f"<script>document.title='{len(clients)} clients | Deco Dashboard'</script>", unsafe_allow_html=True)

# Connection status
st.caption(f"🌐 Connected to Deco at {DECO_HOST} — {len(nodes) if nodes else 4} mesh nodes")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🖥️ Total", len(clients))
c2.metric("🔌 Wired", wired)
c3.metric("📶 WiFi", wireless)
c4.metric("⬇️ Down", f"{total_down} KB/s")
c5.metric("⬆️ Up", f"{total_up} KB/s")

# --- Tabs ---
tab_clients, tab_known, tab_nodes, tab_topo, tab_bands, tab_speeds, tab_steering, tab_security, tab_block, tab_parental, tab_uptime, tab_history, tab_export, tab_ai = st.tabs([
    "Clients", "Known Devices", "Nodes", "Topology", "WiFi Bands", "Bandwidth", "Band Steering", "Security",
    "Block/Unblock", "Parental", "Uptime", "History", "Export", "AI"
])

with tab_clients:
    if clients:
        df = pd.DataFrame(clients)
        search = st.text_input("Search", placeholder="Filter by name, IP, or MAC...")
        if search:
            mask = df.apply(lambda row: search.lower() in str(row).lower(), axis=1)
            df = df[mask]
        st.dataframe(df.sort_values("Down (KB/s)", ascending=False), width="stretch", hide_index=True)
    else:
        st.info("No clients found.")

# --- Known Devices Tab ---
with tab_known:
    st.subheader("📋 All Known Devices")
    st.caption("Every device ever connected to your network")

    if known_devices:
        online_count = sum(1 for d in known_devices.values() if d["status"] == "online")
        offline_count = len(known_devices) - online_count

        k1, k2, k3 = st.columns(3)
        k1.metric("Total Known", len(known_devices))
        k2.metric("🟢 Online", online_count)
        k3.metric("🔴 Offline", offline_count)

        # Filter
        status_filter = st.radio("Show", ["All", "Online", "Offline"], horizontal=True, key="known_filter")

        known_list = []
        for mac, info in known_devices.items():
            if status_filter == "Online" and info["status"] != "online":
                continue
            if status_filter == "Offline" and info["status"] != "offline":
                continue
            known_list.append({
                "Status": "🟢" if info["status"] == "online" else "🔴",
                "Name": info.get("name", "Unknown"),
                "IP": info.get("ip", "N/A"),
                "MAC": mac,
                "Connection": info.get("connection", "Unknown"),
                "First Seen": info.get("first_seen", "")[:16],
                "Last Seen": info.get("last_seen", "")[:16],
                "Times Seen": info.get("times_seen", 0),
            })

        if known_list:
            df_known = pd.DataFrame(known_list)
            search_known = st.text_input("Search devices", placeholder="Filter by name, IP, or MAC...", key="known_search")
            if search_known:
                mask = df_known.apply(lambda row: search_known.lower() in str(row).lower(), axis=1)
                df_known = df_known[mask]
            st.dataframe(df_known.sort_values("Status"), width="stretch", hide_index=True)

        # New devices alert
        now = datetime.now()
        recent = [info for info in known_devices.values()
                  if info.get("first_seen") and
                  (now - datetime.fromisoformat(info["first_seen"])).total_seconds() < 3600]
        if recent:
            st.warning(f"🆕 {len(recent)} new device(s) seen in the last hour")
            for d in recent:
                st.caption(f"  🆕 {d['name']} ({d['mac']}) — first seen {d['first_seen'][:16]}")
    else:
        st.info("Known devices will accumulate as the dashboard runs.")

with tab_nodes:
    st.subheader("📡 Deco Mesh Nodes")
    if nodes:
        st.dataframe(pd.DataFrame(nodes), width="stretch", hide_index=True)
    else:
        st.info("Parsing nodes from page...")

    # Always show node names from home text
    node_names = ["Hallway", "Main Deco", "Living Room", "Office"]
    found = [n for n in node_names if n in home_text]
    if found:
        st.markdown(f"**Detected {len(found)} Deco nodes:**")
        for name in found:
            st.markdown(f"- 📡 {name}")


# --- Topology Tab ---
with tab_topo:
    st.subheader("🗺️ Network Topology")

    detected_nodes = [n for n in ["Hallway", "Main Deco", "Living Room", "Office"] if n in home_text]
    if not detected_nodes:
        detected_nodes = ["Hallway", "Main Deco", "Living Room", "Office"]

    def get_icon(conn):
        conn = str(conn)
        if "Wired" in conn: return "🔌"
        if "6G" in conn: return "📶"
        if "5G" in conn: return "📡"
        if "2.4G" in conn: return "📻"
        return "❓"

    # Internet → Mesh
    st.markdown("### 🌐 Internet")
    st.markdown("│")
    st.markdown(f"### 🏠 Deco BE95 Mesh — {len(detected_nodes)} nodes, {len(clients)} clients")
    st.markdown("│")

    # Show nodes
    for idx, node in enumerate(detected_nodes):
        connector = "└──" if idx == len(detected_nodes) - 1 else "├──"
        st.markdown(f"**{connector} 📡 {node}**")

    # Group clients by connection type
    st.markdown("---")

    groups = [
        ("🔌 Wired", [c for c in clients if "Wired" in c.get("Connection", "")]),
        ("📶 WiFi 6 GHz", [c for c in clients if "6G" in c.get("Connection", "")]),
        ("📡 WiFi 5 GHz", [c for c in clients if "5G" in c.get("Connection", "") and "6G" not in c.get("Connection", "")]),
        ("📻 WiFi 2.4 GHz", [c for c in clients if "2.4G" in c.get("Connection", "")]),
    ]
    other = [c for c in clients if not any(c in g for _, g in groups)]
    if other:
        groups.append(("❓ Other", other))

    for group_name, group_clients in groups:
        if group_clients:
            st.markdown(f"### {group_name} ({len(group_clients)})")
            for c in sorted(group_clients, key=lambda x: x.get("Down (KB/s)", 0), reverse=True):
                speed = ""
                if c.get("Down (KB/s)", 0) > 0 or c.get("Up (KB/s)", 0) > 0:
                    speed = f" — ⬇️{c['Down (KB/s)']} ⬆️{c['Up (KB/s)']} KB/s"
                st.caption(f"  └── **{c['Name']}** — {c['IP']}{speed}")

    # Connection type chart
    st.markdown("---")
    st.subheader("📊 Connection Distribution")
    conn_data = pd.DataFrame([{"Type": name.split(" ", 1)[1], "Count": len(cls)} for name, cls in groups if cls])
    if not conn_data.empty:
        st.bar_chart(conn_data.set_index("Type"))

with tab_bands:
    if clients:
        df = pd.DataFrame(clients)

        def get_band(conn):
            conn = str(conn)
            if "2.4G" in conn or "2.4g" in conn: return "2.4 GHz"
            if ("5G" in conn or "5g" in conn) and "6G" not in conn and "6g" not in conn: return "5 GHz"
            if "6G" in conn or "6g" in conn: return "6 GHz"
            if "Wired" in conn or "wired" in conn: return "Wired"
            return "Unknown"

        df["Band"] = df["Connection"].apply(get_band)


        # Summary metrics per band
        st.subheader("📶 WiFi Band Distribution")
        b1, b2, b3, b4 = st.columns(4)
        band_24 = df[df["Band"] == "2.4 GHz"]
        band_5 = df[df["Band"] == "5 GHz"]
        band_6 = df[df["Band"] == "6 GHz"]
        band_wired = df[df["Band"] == "Wired"]
        b1.metric("📡 2.4 GHz", len(band_24))
        b2.metric("📡 5 GHz", len(band_5))
        b3.metric("📡 6 GHz", len(band_6))
        b4.metric("🔌 Wired", len(band_wired))

        # Band chart
        band_counts = df["Band"].value_counts()
        st.bar_chart(band_counts)

        # Separate tabs for each band
        bt1, bt2, bt3, bt4 = st.tabs(["2.4 GHz", "5 GHz", "6 GHz", "Wired"])

        with bt1:
            if not band_24.empty:
                st.markdown(f"**{len(band_24)} devices on 2.4 GHz**")
                st.caption("Longer range, lower speed — ideal for IoT devices")
                cols = [c for c in ["Name", "IP", "MAC", "Down (KB/s)", "Up (KB/s)", "Online For"] if c in band_24.columns]
                st.dataframe(band_24[cols], width="stretch", hide_index=True)
            else:
                st.info("No devices on 2.4 GHz")

        with bt2:
            if not band_5.empty:
                st.markdown(f"**{len(band_5)} devices on 5 GHz**")
                st.caption("Good balance of range and speed")
                cols = [c for c in ["Name", "IP", "MAC", "Down (KB/s)", "Up (KB/s)", "Online For"] if c in band_5.columns]
                st.dataframe(band_5[cols], width="stretch", hide_index=True)
            else:
                st.info("No devices on 5 GHz")

        with bt3:
            if not band_6.empty:
                st.markdown(f"**{len(band_6)} devices on 6 GHz**")
                st.caption("Fastest band — WiFi 6E/7 devices only")
                cols = [c for c in ["Name", "IP", "MAC", "Down (KB/s)", "Up (KB/s)", "Online For"] if c in band_6.columns]
                st.dataframe(band_6[cols], width="stretch", hide_index=True)
            else:
                st.info("No devices on 6 GHz")

        with bt4:
            if not band_wired.empty:
                st.markdown(f"**{len(band_wired)} wired devices**")
                st.caption("Direct ethernet connection")
                cols = [c for c in ["Name", "IP", "MAC", "Down (KB/s)", "Up (KB/s)", "Online For"] if c in band_wired.columns]
                st.dataframe(band_wired[cols], width="stretch", hide_index=True)
            else:
                st.info("No wired devices")

        # Bandwidth by band
        st.subheader("📊 Bandwidth by Band")
        band_bw = df.groupby("Band").agg({"Down (KB/s)": "sum", "Up (KB/s)": "sum"}).sort_values("Down (KB/s)", ascending=False)
        st.bar_chart(band_bw)

with tab_speeds:
    if clients:
        df = pd.DataFrame(clients)
        df["Band"] = df["Connection"].apply(get_band)
        df["Total (KB/s)"] = df["Down (KB/s)"] + df["Up (KB/s)"]

        # Active devices
        active = df[df["Total (KB/s)"] > 0].sort_values("Total (KB/s)", ascending=False)

        st.subheader("⚡ Real-Time Bandwidth")
        if not active.empty:
            a1, a2, a3 = st.columns(3)
            a1.metric("Active Devices", len(active))
            a2.metric("Total Down", f"{active['Down (KB/s)'].sum()} KB/s")
            a3.metric("Total Up", f"{active['Up (KB/s)'].sum()} KB/s")

            st.bar_chart(active.set_index("Name")[["Down (KB/s)", "Up (KB/s)"]])
            st.dataframe(active[["Name", "IP", "Band", "Down (KB/s)", "Up (KB/s)", "Total (KB/s)", "Online For"]],
                         width="stretch", hide_index=True)
        else:
            st.info("No active bandwidth usage right now. Speeds are real-time and fluctuate.")

        # Top consumers
        st.subheader("📊 All Devices")
        st.dataframe(df[["Name", "IP", "Band", "Down (KB/s)", "Up (KB/s)", "Total (KB/s)", "Connection"]].sort_values("Total (KB/s)", ascending=False),
                     width="stretch", hide_index=True)

# --- Band Steering Tab ---
with tab_steering:
    st.subheader("📡 Band Steering Recommendations")
    if clients:
        df = pd.DataFrame(clients)

        def get_band(conn):
            conn = str(conn)
            if "2.4G" in conn or "2.4g" in conn: return "2.4 GHz"
            if ("5G" in conn or "5g" in conn) and "6G" not in conn and "6g" not in conn: return "5 GHz"
            if "6G" in conn or "6g" in conn: return "6 GHz"
            if "Wired" in conn or "wired" in conn: return "Wired"
            return "Unknown"

        df["Band"] = df["Connection"].apply(get_band)

        # Devices that should move to a better band
        st.markdown("### 🔄 Suggested Band Changes")

        # High-performance devices stuck on 2.4GHz
        on_24 = df[df["Band"] == "2.4 GHz"]
        high_perf_on_24 = on_24[on_24["Name"].str.contains(
            "TV|Mac|iPhone|iPad|Tab|Fire|laptop|computer|LG|Samsung-TV|Marantz",
            case=False, na=False)]

        if not high_perf_on_24.empty:
            st.warning(f"⚠️ {len(high_perf_on_24)} high-performance device(s) on 2.4 GHz — should be on 5 GHz or 6 GHz")
            for _, d in high_perf_on_24.iterrows():
                st.markdown(f"- **{d['Name']}** ({d['IP']}) — Move to **5 GHz** or **6 GHz**")
        else:
            st.success("✅ No high-performance devices stuck on 2.4 GHz")

        # Streaming/media devices that could benefit from 5GHz or 6GHz
        on_24_media = on_24[on_24["Name"].str.contains(
            "Bose|Sonos|Speaker|Alexa|Echo|Sky|TV|Marantz",
            case=False, na=False)]
        if not on_24_media.empty:
            st.info(f"💡 {len(on_24_media)} media device(s) on 2.4 GHz — consider 5 GHz for better streaming")
            for _, d in on_24_media.iterrows():
                st.markdown(f"- **{d['Name']}** ({d['IP']}) — Could benefit from **5 GHz**")

        # IoT devices correctly on 2.4GHz
        iot_names = "Ring|Chime|Washer|Dryer|Lamp|Hive|Plug|Sensor|Door"
        iot_on_24 = on_24[on_24["Name"].str.contains(iot_names, case=False, na=False)]
        if not iot_on_24.empty:
            st.success(f"✅ {len(iot_on_24)} IoT device(s) correctly on 2.4 GHz")
            with st.expander("IoT devices on 2.4 GHz"):
                for _, d in iot_on_24.iterrows():
                    st.caption(f"  ✅ {d['Name']} ({d['IP']})")

        # 6GHz capable devices not on 6GHz
        on_5 = df[df["Band"] == "5 GHz"]
        could_be_6g = on_5[on_5["Name"].str.contains(
            "iPhone|Mac|iPad|Tab|Galaxy|Pixel",
            case=False, na=False)]
        if not could_be_6g.empty:
            st.info(f"📶 {len(could_be_6g)} device(s) on 5 GHz that may support 6 GHz")
            for _, d in could_be_6g.iterrows():
                st.markdown(f"- **{d['Name']}** ({d['IP']}) — Check if WiFi 6E/7 capable → move to **6 GHz**")

        # Summary
        st.markdown("---")
        st.markdown("### 📊 Current Band Distribution")
        band_summary = df["Band"].value_counts()
        st.bar_chart(band_summary)

        st.markdown("### 💡 Ideal Distribution")
        st.markdown("""
        | Band | Ideal Use | Target Devices |
        |------|-----------|---------------|
        | **6 GHz** | Fastest, lowest latency | Newer iPhones, Macs, WiFi 7 devices |
        | **5 GHz** | High speed, good range | TVs, tablets, streaming, gaming |
        | **2.4 GHz** | Long range, IoT | Smart plugs, sensors, Ring, old devices |
        | **Wired** | Most reliable | NAS, desktop, Sky Q, gaming consoles |
        """)

        st.markdown("### ⚙️ How to Enable Band Steering")
        st.markdown("""
        1. Open the **Deco/Tether app** on your phone
        2. Go to **WiFi Settings**
        3. Enable **Smart Connect** — this automatically steers devices to the best band
        4. Or via web admin: `https://192.168.2.1` → Advanced → Wireless → Smart Connect
        """)

# --- Security Checklist Tab ---
CHECKLIST_FILE = ".deco_security_checklist.json"

def load_checklist():
    if os.path.exists(CHECKLIST_FILE):
        with open(CHECKLIST_FILE) as f:
            return json.load(f)
    return {}

def save_checklist(data):
    with open(CHECKLIST_FILE, "w") as f:
        json.dump(data, f)

with tab_security:
    st.subheader("🛡️ Security Checklist")
    checklist = load_checklist()

    categories = {
        "🔴 Critical Priority": [
            ("iot_network", "Create separate IoT network/VLAN", "Move Ring, Alexa, smart appliances, Hive hub to IoT network"),
            ("guest_network", "Enable guest network", "For visitors and less-trusted devices"),
            ("wpa3", "Enable WPA3 encryption", "Advanced → Wireless → Security → WPA3"),
        ],
        "🟡 High Priority": [
            ("smart_connect", "Enable Smart Connect (band steering)", "Advanced → Wireless → Smart Connect"),
            ("auto_update", "Enable auto firmware updates", "Advanced → System → Auto Update"),
            ("strong_password", "Use strong WiFi password (20+ chars)", "Mixed case, numbers, symbols"),
            ("admin_password", "Change default admin password", "Use unique password for Deco admin"),
        ],
        "🟢 Recommended": [
            ("device_naming", "Name all devices properly", "Replace generic names like 'Mac', 'iPhone'"),
            ("mac_filtering", "Enable MAC filtering for critical devices", "Whitelist known devices"),
            ("remote_access", "Disable remote management if not needed", "Reduces attack surface"),
            ("upnp_disable", "Disable UPnP", "Prevents automatic port forwarding"),
            ("wps_disable", "Disable WPS", "WPS has known vulnerabilities"),
        ],
        "🔵 Monitoring": [
            ("monthly_audit", "Monthly device audit", "Review connected devices for unknowns"),
            ("firmware_check", "Monthly firmware check", "Verify all nodes are up to date"),
            ("password_rotation", "Quarterly password rotation", "Change WiFi and admin passwords"),
            ("traffic_review", "Weekly traffic review", "Check for unusual bandwidth patterns"),
        ],
    }

    changed = False
    total = 0
    completed = 0

    for category, items in categories.items():
        st.markdown(f"### {category}")
        for key, title, description in items:
            total += 1
            current = checklist.get(key, False)
            new_val = st.checkbox(title, value=current, key=f"sec_{key}", help=description)
            if new_val != current:
                checklist[key] = new_val
                changed = True
            if new_val:
                completed += 1
            st.caption(f"  ↳ {description}")

    if changed:
        save_checklist(checklist)

    # Progress
    st.markdown("---")
    pct = int((completed / total) * 100) if total > 0 else 0
    st.progress(pct / 100)
    st.markdown(f"**Security Score: {completed}/{total} ({pct}%)**")

    if pct < 30:
        st.error("🔴 Critical — implement priority items immediately")
    elif pct < 60:
        st.warning("🟡 Moderate — good progress, keep going")
    elif pct < 90:
        st.info("🟢 Good — most recommendations implemented")
    else:
        st.success("✅ Excellent — network is well secured")

# --- Block/Unblock Tab ---
with tab_block:
    st.subheader("🚫 Device Access Control")
    if clients:
        device_names = {f"{c['Name']} ({c['IP']})": c['Name'] for c in clients}
        selected = st.selectbox("Select device", list(device_names.keys()), key="block_sel")
        sel_name = device_names[selected]

        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("🔴 Block Device", type="primary", key="block_btn"):
                with st.spinner(f"Blocking {sel_name}..."):
                    result = block_device_browser(sel_name)
                    if result is True:
                        st.success(f"Blocked {sel_name}")
                        st.cache_data.clear()
                    else:
                        st.error(f"Failed: {result}")
        with bc2:
            if st.button("🟢 Unblock Device", key="unblock_btn"):
                with st.spinner(f"Unblocking {sel_name}..."):
                    result = unblock_device_browser(sel_name)
                    if result is True:
                        st.success(f"Unblocked {sel_name}")
                        st.cache_data.clear()
                    else:
                        st.error(f"Failed: {result}")

        st.caption("Note: Blocking launches a browser session to the Deco admin and may take 15-20 seconds.")
    else:
        st.info("No clients to manage.")

# --- Parental Controls Tab ---
with tab_parental:
    st.subheader("👨‍👩‍👧 Parental Controls")
    st.caption("Schedule internet access per device")

    rules = load_parental_rules()

    if clients:
        st.markdown("### Add Schedule")
        p_device = st.selectbox("Device", [f"{c['Name']} ({c['IP']})" for c in clients], key="parental_dev")
        p_name = p_device.split(" (")[0]

        pc1, pc2 = st.columns(2)
        with pc1:
            p_start = st.time_input("Block from", value=None, key="p_start")
        with pc2:
            p_end = st.time_input("Block until", value=None, key="p_end")

        p_days = st.multiselect("Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                                default=["Mon", "Tue", "Wed", "Thu", "Fri"], key="p_days")

        if st.button("➕ Add Rule", key="add_parental"):
            if p_start and p_end and p_days:
                if p_name not in rules:
                    rules[p_name] = []
                rules[p_name].append({
                    "start": p_start.strftime("%H:%M"),
                    "end": p_end.strftime("%H:%M"),
                    "days": p_days,
                    "active": True,
                })
                save_parental_rules(rules)
                st.success(f"Rule added for {p_name}")
            else:
                st.warning("Set start time, end time, and days.")

        if rules:
            st.markdown("### Active Rules")
            for name, name_rules in list(rules.items()):
                for i, rule in enumerate(name_rules):
                    status = "🟢 Active" if rule.get("active", True) else "🔴 Disabled"
                    st.markdown(f"**{name}** — {rule['start']} to {rule['end']} on {', '.join(rule['days'])} {status}")

                    rc1, rc2, rc3 = st.columns(3)
                    with rc1:
                        if st.button("🔴 Block Now", key=f"pblock_{name}_{i}"):
                            with st.spinner(f"Blocking {name}..."):
                                result = block_device_browser(name)
                                if result is True:
                                    st.success(f"Blocked {name}")
                                else:
                                    st.error(f"Failed: {result}")
                    with rc2:
                        if st.button("🟢 Unblock", key=f"punblock_{name}_{i}"):
                            with st.spinner(f"Unblocking {name}..."):
                                result = unblock_device_browser(name)
                                if result is True:
                                    st.success(f"Unblocked {name}")
                                else:
                                    st.error(f"Failed: {result}")
                    with rc3:
                        if st.button("🗑️ Delete", key=f"pdel_{name}_{i}"):
                            rules[name].pop(i)
                            if not rules[name]:
                                del rules[name]
                            save_parental_rules(rules)
                            st.rerun()

            # Check current schedule
            now_time = datetime.now()
            now_day = now_time.strftime("%a")
            now_hm = now_time.strftime("%H:%M")
            enforced = []
            for name, name_rules in rules.items():
                for rule in name_rules:
                    if rule.get("active") and now_day in rule.get("days", []):
                        if rule["start"] <= now_hm <= rule["end"]:
                            enforced.append(name)
            if enforced:
                st.warning(f"Devices in blocked schedule now: {', '.join(enforced)}")
    else:
        st.info("No clients available.")

# --- Uptime Tab ---
with tab_uptime:
    st.subheader("⏱️ Device Uptime")
    if uptime_data:
        uptime_list = []
        for mac, info in uptime_data.items():
            status = info.get("status", "unknown")
            online_since = info.get("online_since", "")
            if status == "online" and online_since:
                duration = (now - datetime.fromisoformat(online_since)).total_seconds()
                duration_str = format_duration(duration)
            else:
                duration_str = "Offline"
                duration = 0

            uptime_list.append({
                "Name": info.get("name", mac),
                "MAC": mac.upper(),
                "Status": "🟢 Online" if status == "online" else "🔴 Offline",
                "Online For": duration_str if status == "online" else "-",
                "Last Seen": info.get("last_seen", "")[:19],
                "First Seen": info.get("first_seen", "")[:19],
            })

        df_up = pd.DataFrame(uptime_list)
        online = sum(1 for u in uptime_list if "Online" in u["Status"])
        offline = len(uptime_list) - online

        u1, u2, u3 = st.columns(3)
        u1.metric("Tracked", len(uptime_list))
        u2.metric("Online", online)
        u3.metric("Offline", offline)

        st.dataframe(df_up.sort_values("Status", ascending=False), width="stretch", hide_index=True)

        if offline > 0:
            st.warning(f"{offline} device(s) previously seen but currently offline")
    else:
        st.info("Uptime data will accumulate as the dashboard runs.")

# --- History Tab ---
with tab_history:
    st.subheader("📈 Historical Network Data")
    days = st.slider("Days of history", 1, 30, 7, key="deco_hist_days")
    history = get_deco_history(days)
    if history:
        hist_df = pd.DataFrame([{
            "Time": h.get("timestamp", "")[:16],
            "Clients": int(h.get("client_count", 0)),
            "Down (KB/s)": int(h.get("total_down_kbps", 0)),
            "Up (KB/s)": int(h.get("total_up_kbps", 0)),
        } for h in history])

        st.line_chart(hist_df.set_index("Time")[["Clients"]])
        st.line_chart(hist_df.set_index("Time")[["Down (KB/s)", "Up (KB/s)"]])
        st.dataframe(hist_df, width="stretch", hide_index=True)
        st.caption(f"{len(history)} snapshots stored locally")
    else:
        st.info("No historical data yet. Snapshots are saved automatically every 5 minutes.")

    # Auto-save snapshot
    if "deco_last_snapshot" not in st.session_state:
        st.session_state.deco_last_snapshot = None
    now_snap = datetime.now()
    if st.session_state.deco_last_snapshot is None or (now_snap - st.session_state.deco_last_snapshot).total_seconds() >= 300:
        save_deco_snapshot(clients)
        st.session_state.deco_last_snapshot = now_snap

    if st.button("💾 Save Snapshot Now", key="save_snap"):
        if save_deco_snapshot(clients):
            st.success("Snapshot saved")

# --- Export Tab ---
with tab_export:
    st.subheader("📄 Export Reports")
    if clients:
        e1, e2 = st.columns(2)
        with e1:
            csv = export_csv(clients)
            st.download_button("📥 Download CSV", csv, "deco_clients.csv", "text/csv")
        with e2:
            json_data = export_json_report(clients, nodes)
            st.download_button("📥 Download JSON", json_data, "deco_report.json", "application/json")

        if st.button("📝 Generate AI Report", key="ai_report"):
            with st.spinner("Generating report..."):
                try:
                    ctx = build_deco_context(clients, home_text)
                    report = call_bedrock(
                        "Generate a comprehensive Deco mesh network report with: Executive Summary, "
                        "Device Inventory by band, Bandwidth Analysis, Mesh Node Coverage, "
                        "Security Assessment, and Recommendations. Format in clean markdown.",
                        "Generate full network report.", ctx)
                    st.markdown(report)
                    st.download_button("📥 Download AI Report", report.encode("utf-8"),
                                       "deco_ai_report.md", "text/markdown", key="dl_ai")
                except Exception as e:
                    st.error(f"AI report error: {e}")
    else:
        st.info("No data to export.")

# --- AI Intelligence Tab ---
def call_bedrock(system, user_msg, ctx):
    try:
        bc = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1500,
            "system": system,
            "messages": [{"role": "user", "content": f"{ctx}\n\n{user_msg}"}],
        })
        resp = bc.invoke_model(modelId=BEDROCK_MODEL_ID, body=body,
                               contentType="application/json", accept="application/json")
        return json.loads(resp["body"].read())["content"][0]["text"]
    except Exception as e:
        return f"Bedrock error: {e}"


def build_deco_context(clients, nodes_text):
    wired = sum(1 for c in clients if "Wired" in c.get("Connection", ""))
    bands = {}
    for c in clients:
        conn = c.get("Connection", "Unknown")
        bands[conn] = bands.get(conn, 0) + 1

    client_lines = "\n".join(
        f"  - {c['Name']} | IP:{c['IP']} | MAC:{c['MAC']} | {c['Connection']} | Down:{c['Down (KB/s)']}KB/s Up:{c['Up (KB/s)']}KB/s"
        for c in clients
    )
    band_lines = "\n".join(f"  - {k}: {v} clients" for k, v in bands.items())

    return f"""Deco BE95 Network ({datetime.now().strftime('%Y-%m-%d %H:%M')}):
Clients: {len(clients)} (Wired: {wired}, Wireless: {len(clients) - wired})
WiFi Bands:\n{band_lines}
Mesh Nodes: 4 (Hallway, Main Deco, Living Room, Office)
All Clients:\n{client_lines}"""


with tab_ai:
    st.subheader("🤖 AI Network Intelligence")
    if clients:
        ctx = build_deco_context(clients, home_text)

        ai1, ai2, ai3, ai4 = st.tabs(["Summary", "Anomalies", "Security", "Chat"])

        with ai1:
            if st.button("Generate Summary", key="deco_sum"):
                with st.spinner("Analyzing..."):
                    st.markdown(call_bedrock(
                        "You are a WiFi network analyst. Give a concise summary of this Deco mesh network. "
                        "Highlight client distribution across bands, active devices, and mesh node coverage.",
                        "Summarize my Deco network.", ctx))

        with ai2:
            if st.button("Scan for Anomalies", key="deco_anom"):
                with st.spinner("Scanning..."):
                    st.markdown(call_bedrock(
                        "You are a network security analyst. Analyze this Deco mesh network for: "
                        "unusual devices, bandwidth anomalies, devices on wrong bands, potential issues.",
                        "Find anomalies.", ctx))

        with ai3:
            if st.button("Security Recommendations", key="deco_sec"):
                with st.spinner("Analyzing..."):
                    st.markdown(call_bedrock(
                        "You are a WiFi security advisor for a Deco BE95 mesh network. Provide recommendations on: "
                        "band steering, IoT isolation, guest network, WPA3, firmware updates, device placement.",
                        "Security recommendations?", ctx))

        with ai4:
            if "deco_messages" not in st.session_state:
                st.session_state.deco_messages = []
            for msg in st.session_state.deco_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            if q := st.chat_input("Ask about your Deco network..."):
                st.session_state.deco_messages.append({"role": "user", "content": q})
                with st.chat_message("user"):
                    st.markdown(q)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        ans = call_bedrock(
                            "You are a helpful Deco mesh network assistant. Answer questions using the network data provided.",
                            q, ctx)
                        st.markdown(ans)
                        st.session_state.deco_messages.append({"role": "assistant", "content": ans})
    else:
        st.info("No client data available for AI analysis.")

# --- Footer ---
st.divider()
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Deco: {DECO_HOST}")
