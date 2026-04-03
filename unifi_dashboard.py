import streamlit as st
import requests
import urllib3
import pandas as pd
import os
import json
import io
import boto3
import subprocess
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Configuration ---
GATEWAY_IP = "192.168.1.1"
BASE_URL = f"https://{GATEWAY_IP}/proxy/network/integration/v1"
CLASSIC_URL = f"https://{GATEWAY_IP}/proxy/network/api"
API_KEY = os.getenv("UNIFI_API_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "unifi-network-snapshots")
ENABLE_AWS = os.getenv("ENABLE_AWS", "false").lower() == "true"
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "eu.anthropic.claude-sonnet-4-20250514-v1:0")
AUTO_REFRESH_SECONDS = int(os.getenv("AUTO_REFRESH_SECONDS", "30"))
UPTIME_LOG_FILE = ".device_uptime_log.json"
DASHBOARD_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "")
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "false").lower() == "true"

# --- Page Config ---
st.set_page_config(page_title="UniFi Network Dashboard", layout="wide", page_icon="🌐")

# --- Colorful Theme CSS ---
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(180deg, #f0f4ff 0%, #ffffff 100%);
    }
    
    /* Header */
    h1 { 
        font-size: 1.5em !important; 
        margin-bottom: 0.5rem !important;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto;
        flex-wrap: nowrap;
        -webkit-overflow-scrolling: touch;
        gap: 2px;
        scrollbar-width: none;
        background: linear-gradient(135deg, #e8eaf6 0%, #f3e5f5 100%);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
    .stTabs [data-baseweb="tab"] {
        white-space: nowrap;
        font-size: 0.8em;
        padding: 0.4rem 0.7rem;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Metric cards with colors */
    [data-testid="stMetric"] {
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: none;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] label,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] label,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #fc5c7d 0%, #6a82fb 100%);
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] label,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] label,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"] label,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(6) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(6) [data-testid="stMetric"] label,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(6) [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stAlert {
        background: rgba(255,255,255,0.15);
        border: none;
    }
    [data-testid="stSidebar"] input {
        background: rgba(255,255,255,0.2) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    /* Buttons */
    .stButton button {
        min-height: 44px;
        min-width: 44px;
        border-radius: 10px;
        font-weight: 500;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transform: translateY(-1px);
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Subheaders */
    h2, h3 {
        color: #4a4a6a !important;
    }
    
    /* Dividers */
    hr { border-color: #e8eaf6 !important; }
    
    /* Success/Warning/Error messages */
    .stAlert [data-testid="stAlertContentSuccess"] { border-radius: 10px; }
    .stAlert [data-testid="stAlertContentWarning"] { border-radius: 10px; }
    .stAlert [data-testid="stAlertContentError"] { border-radius: 10px; }
    
    /* Charts */
    .stChart {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Mobile */
    @media (max-width: 768px) {
        .block-container { padding: 1rem 0.5rem !important; }
        
        [data-testid="stMetric"] {
            padding: 8px 10px;
            text-align: center;
        }
        [data-testid="stMetric"] label { font-size: 0.65em !important; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.1em !important; }
        
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
        [data-testid="stColumn"] { min-width: 45% !important; }
        
        .stMarkdown p { font-size: 0.9em; }
        h2 { font-size: 1.2em !important; }
        h3 { font-size: 1.1em !important; }
        
        .stDataFrame { font-size: 0.75em; }
        .stDataFrame [data-testid="stDataFrameResizable"] {
            overflow-x: auto !important;
            max-width: 100vw;
        }
        
        [data-testid="stSidebar"] { min-width: 200px !important; max-width: 250px !important; }
        
        .stButton button {
            min-height: 48px;
            width: 100%;
            font-size: 0.85em;
        }
        
        .stChart { max-width: 100vw; overflow-x: auto; }
        .stSelectbox, .stTextInput { font-size: 0.85em; }
        .streamlit-expanderHeader { font-size: 0.85em !important; }
        
        .stTabs .stTabs [data-baseweb="tab"] {
            font-size: 0.75em;
            padding: 0.3rem 0.4rem;
        }
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] { overflow-x: auto; }
    
    @media (max-width: 768px) {
        #MainMenu { display: none; }
        footer { display: none; }
        header { display: none; }
    }
</style>
""", unsafe_allow_html=True)

# --- Authentication ---
def check_auth():
    """Simple password authentication."""
    if not DASHBOARD_PASSWORD or DISABLE_AUTH:
        return True  # No password set or auth disabled, skip

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔐 UniFi Dashboard Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary")

        if submitted:
            if username == DASHBOARD_USERNAME and password == DASHBOARD_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid username or password")
    return False


if not check_auth():
    st.stop()

st.title("🌐 UniFi Network Dashboard")

# --- Sidebar Config ---
if "api_key" not in st.session_state:
    st.session_state.api_key = API_KEY

# Only show API key input if not set via environment
if API_KEY:
    api_key = API_KEY
    st.sidebar.success("API Key loaded from environment")
else:
    api_key = st.sidebar.text_input("UniFi API Key", type="password", value=st.session_state.api_key)
    st.session_state.api_key = api_key

# Auto-refresh toggle
auto_refresh = st.sidebar.toggle("Auto-refresh", value=False)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 10, 120, AUTO_REFRESH_SECONDS)
    st.sidebar.caption(f"Refreshing every {refresh_interval}s")
    time.sleep(0.1)  # Small delay to prevent race
    st.rerun() if "last_refresh" not in st.session_state else None
    if "last_refresh" in st.session_state:
        elapsed = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if elapsed >= refresh_interval:
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    else:
        st.session_state.last_refresh = datetime.now()

HEADERS = {"X-API-KEY": api_key, "Accept": "application/json"}


# --- API Functions (cached for 10 seconds) ---
@st.cache_data(ttl=10, show_spinner=False)
def api_get_cached(_api_key, endpoint):
    try:
        headers = {"X-API-KEY": _api_key, "Accept": "application/json"}
        resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, verify=False, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return None


@st.cache_data(ttl=10, show_spinner=False)
def classic_api_get_cached(_api_key, endpoint):
    try:
        headers = {"X-API-KEY": _api_key, "Accept": "application/json"}
        resp = requests.get(f"{CLASSIC_URL}{endpoint}", headers=headers, verify=False, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        return None


def api_get(endpoint):
    result = api_get_cached(api_key, endpoint)
    if result is None:
        st.error(f"API Error: Failed to fetch {endpoint}")
    return result


def classic_api_get(endpoint):
    return classic_api_get_cached(api_key, endpoint)


def classic_api_post(endpoint, data):
    try:
        resp = requests.post(f"{CLASSIC_URL}{endpoint}", headers=HEADERS, json=data, verify=False, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def block_client(mac):
    """Block a client device via the classic API."""
    return classic_api_post("/s/default/cmd/stamgr", {"cmd": "block-sta", "mac": mac.lower()})


def unblock_client(mac):
    """Unblock a client device via the classic API."""
    return classic_api_post("/s/default/cmd/stamgr", {"cmd": "unblock-sta", "mac": mac.lower()})

# --- AWS Functions ---
def get_aws_clients():
    try:
        session = boto3.Session(region_name=AWS_REGION)
        return {
            "cloudwatch": session.client("cloudwatch"),
            "sns": session.client("sns"),
            "dynamodb": session.resource("dynamodb"),
        }
    except Exception as e:
        st.sidebar.warning(f"AWS init failed: {e}")
        return None


def push_cloudwatch_metrics(cw, count, wired, tx, rx):
    try:
        now = datetime.now(timezone.utc)
        cw.put_metric_data(Namespace="UniFi/Network", MetricData=[
            {"MetricName": "ConnectedClients", "Value": count, "Unit": "Count", "Timestamp": now},
            {"MetricName": "WiredClients", "Value": wired, "Unit": "Count", "Timestamp": now},
            {"MetricName": "WirelessClients", "Value": count - wired, "Unit": "Count", "Timestamp": now},
            {"MetricName": "TotalTxMB", "Value": tx, "Unit": "Megabytes", "Timestamp": now},
            {"MetricName": "TotalRxMB", "Value": rx, "Unit": "Megabytes", "Timestamp": now},
        ])
        return True
    except ClientError as e:
        st.sidebar.error(f"CloudWatch error: {e}")
        return False


def check_new_devices_and_alert(sns, clients_list):
    known_file = ".known_devices.json"
    known = set(json.load(open(known_file))) if os.path.exists(known_file) else set()
    current = {c.get("MAC", "").lower() for c in clients_list if c.get("MAC")}
    new_macs = current - known
    if new_macs and SNS_TOPIC_ARN:
        new_devs = [c for c in clients_list if c.get("MAC", "").lower() in new_macs]
        msg = "🚨 New devices:\n\n" + "\n".join(
            f"  • {d['Name']} — IP: {d['IP']}, MAC: {d['MAC']}" for d in new_devs)
        try:
            sns.publish(TopicArn=SNS_TOPIC_ARN, Subject="UniFi: New Device", Message=msg)
        except ClientError:
            pass
    json.dump(list(known | current), open(known_file, "w"))
    return new_macs


def save_snapshot(dynamodb, clients_list, dev_count):
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        now = datetime.now(timezone.utc)
        tx = sum(c.get("TX (MB)", 0) for c in clients_list)
        rx = sum(c.get("RX (MB)", 0) for c in clients_list)
        table.put_item(Item={
            "timestamp": now.isoformat(), "date": now.strftime("%Y-%m-%d"),
            "client_count": len(clients_list), "device_count": dev_count,
            "total_tx_mb": int(tx), "total_rx_mb": int(rx),
            "clients": json.dumps([{"name": c["Name"], "ip": c["IP"], "mac": c["MAC"],
                                     "tx_mb": c["TX (MB)"], "rx_mb": c["RX (MB)"]} for c in clients_list]),
        })
        return True
    except ClientError as e:
        st.sidebar.error(f"DynamoDB error: {e}")
        return False


def get_historical_data(dynamodb, days=7):
    """Fetch historical snapshots from DynamoDB."""
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        # Scan all items and filter in Python to avoid DynamoDB filter expression issues
        resp = table.scan()
        items = resp.get("Items", [])
        # Handle pagination
        while "LastEvaluatedKey" in resp:
            resp = table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
            items.extend(resp.get("Items", []))
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        filtered = []
        for item in items:
            ts = item.get("timestamp", "")
            try:
                item_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if item_time >= cutoff:
                    filtered.append(item)
            except (ValueError, TypeError):
                pass
        return sorted(filtered, key=lambda x: x.get("timestamp", ""))
    except Exception as e:
        return []

# --- Bedrock AI Functions ---
def get_bedrock_client():
    try:
        return boto3.client("bedrock-runtime", region_name=AWS_REGION)
    except Exception:
        return None


def build_network_context(cl, dl):
    tx = sum(c.get("TX (MB)", 0) for c in cl)
    rx = sum(c.get("RX (MB)", 0) for c in cl)
    w = sum(1 for c in cl if c.get("Type") == "WIRED")
    top = sorted(cl, key=lambda x: x.get("RX (MB)", 0), reverse=True)[:10]
    top_str = "\n".join(f"  - {c['Name']} (IP:{c['IP']}, Vendor:{c.get('Vendor','N/A')}) TX:{c['TX (MB)']}MB RX:{c['RX (MB)']}MB" for c in top)
    all_str = "\n".join(f"  - {c['Name']}|IP:{c['IP']}|MAC:{c['MAC']}|Type:{c['Type']}|Vendor:{c.get('Vendor','N/A')}|TX:{c['TX (MB)']}MB|RX:{c['RX (MB)']}MB" for c in cl)
    dev_str = "\n".join(f"  - {d['Name']}|Model:{d['Model']}|IP:{d['IP']}|State:{d['State']}|FW:{d['Firmware']}" for d in dl) if dl else "N/A"
    return f"""Network Status ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):
Clients: {len(cl)} (Wired:{w}, Wireless:{len(cl)-w}), TX:{tx:.1f}MB, RX:{rx:.1f}MB
DEVICES:\n{dev_str}
TOP CONSUMERS:\n{top_str}
ALL CLIENTS:\n{all_str}"""


def call_bedrock(bc, system, user_msg, ctx):
    try:
        body = json.dumps({"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1500,
                           "system": system, "messages": [{"role": "user", "content": f"{ctx}\n\n{user_msg}"}]})
        resp = bc.invoke_model(modelId=BEDROCK_MODEL_ID, body=body,
                               contentType="application/json", accept="application/json")
        return json.loads(resp["body"].read())["content"][0]["text"]
    except Exception as e:
        return f"Bedrock error: {e}"


def ai_summary(bc, ctx):
    return call_bedrock(bc, "You are a network monitoring AI. Give a concise friendly summary of network status in 3-4 paragraphs.", "Summarize my network.", ctx)

def ai_anomalies(bc, ctx):
    return call_bedrock(bc, "You are a network security analyst. Identify unusual bandwidth patterns, unauthorized devices, suspicious names/vendors, unusual connections. Be specific.", "Analyze for anomalies.", ctx)

def ai_security(bc, ctx):
    return call_bedrock(bc, "You are a network security advisor. Give 5-6 actionable recommendations considering IoT isolation, VLANs, vulnerabilities, best practices.", "Security recommendations?", ctx)

def ai_categorize(bc, ctx):
    return call_bedrock(bc, """You are a network analyst. Categorize each device into: IoT, Entertainment, Work, Security, Network Infrastructure, Mobile, or Other. 
    Return as a markdown table with columns: Device Name, IP, Category, Reasoning. Then show bandwidth totals per category.""",
    "Categorize all devices on my network by type.", ctx)

def ai_chat(bc, ctx, q):
    return call_bedrock(bc, "You are a helpful network assistant with real-time data. Answer concisely, reference specific devices/IPs.", q, ctx)

# --- Uptime Monitoring ---
def load_uptime_log():
    if os.path.exists(UPTIME_LOG_FILE):
        with open(UPTIME_LOG_FILE) as f:
            return json.load(f)
    return {}


def update_uptime_log(current_clients):
    log = load_uptime_log()
    now = datetime.now().isoformat()
    current_macs = {c["MAC"].lower() for c in current_clients if c.get("MAC")}

    for mac in current_macs:
        name = next((c["Name"] for c in current_clients if c.get("MAC", "").lower() == mac), "Unknown")
        if mac not in log:
            log[mac] = {"name": name, "events": [], "last_seen": now, "status": "online"}
        if log[mac]["status"] == "offline":
            log[mac]["events"].append({"type": "online", "time": now})
        log[mac]["status"] = "online"
        log[mac]["last_seen"] = now
        log[mac]["name"] = name

    for mac, info in log.items():
        if mac not in current_macs and info["status"] == "online":
            info["status"] = "offline"
            info["events"].append({"type": "offline", "time": now})
            # Keep only last 50 events
            info["events"] = info["events"][-50:]

    with open(UPTIME_LOG_FILE, "w") as f:
        json.dump(log, f)
    return log


# --- Speed Test ---
def run_speed_test():
    """Run a network speed test to the NAS."""
    results = {}
    try:
        # Write test
        start = time.time()
        subprocess.run(["dd", "if=/dev/zero", "of=/Volumes/file/speedtest", "bs=1m", "count=256"],
                       capture_output=True, text=True, timeout=60)
        write_time = time.time() - start
        results["write_mbps"] = round((256 / write_time) * 8, 1)

        # Small delay to reduce caching effect
        time.sleep(2)

        # Read test
        start = time.time()
        subprocess.run(["dd", "if=/Volumes/file/speedtest", "of=/dev/null", "bs=1m"],
                       capture_output=True, text=True, timeout=60)
        read_time = time.time() - start
        results["read_mbps"] = round((256 / read_time) * 8, 1)

        # Cleanup
        subprocess.run(["rm", "/Volumes/file/speedtest"], capture_output=True)
        results["success"] = True
    except Exception as e:
        results["success"] = False
        results["error"] = str(e)
        subprocess.run(["rm", "-f", "/Volumes/file/speedtest"], capture_output=True)
    return results


def run_internet_speed_test():
    """Run an internet speed test using speedtest-cli."""
    try:
        import speedtest
        s = speedtest.Speedtest()
        s.get_best_server()
        s.download()
        s.upload()
        r = s.results.dict()
        return {
            "success": True,
            "download_mbps": round(r["download"] / 1_000_000, 1),
            "upload_mbps": round(r["upload"] / 1_000_000, 1),
            "ping_ms": round(r["ping"], 1),
            "server": r.get("server", {}).get("name", "N/A"),
            "isp": r.get("client", {}).get("isp", "N/A"),
        }
    except ImportError:
        return {"success": False, "error": "speedtest-cli not installed. Run: pip install speedtest-cli"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- Export Functions ---
def export_csv(df):
    return df.to_csv(index=False).encode("utf-8")


def export_json_report(client_list, device_list_data):
    report = {
        "generated_at": datetime.now().isoformat(),
        "gateway": GATEWAY_IP,
        "summary": {
            "total_clients": len(client_list),
            "wired": sum(1 for c in client_list if c.get("Type") == "WIRED"),
            "wireless": sum(1 for c in client_list if c.get("Type") != "WIRED"),
            "total_tx_mb": round(sum(c.get("TX (MB)", 0) for c in client_list), 1),
            "total_rx_mb": round(sum(c.get("RX (MB)", 0) for c in client_list), 1),
        },
        "devices": device_list_data,
        "clients": client_list,
    }
    return json.dumps(report, indent=2).encode("utf-8")


# --- Bandwidth Alerts ---
BANDWIDTH_THRESHOLD_MB = int(os.getenv("BANDWIDTH_THRESHOLD_MB", "1000"))

def get_bandwidth_alerts(client_list, threshold_mb=BANDWIDTH_THRESHOLD_MB):
    """Find devices exceeding bandwidth threshold."""
    alerts = []
    for c in client_list:
        total_mb = c.get("TX (MB)", 0) + c.get("RX (MB)", 0)
        if total_mb >= threshold_mb:
            alerts.append({
                "Name": c["Name"], "IP": c["IP"], "MAC": c["MAC"],
                "TX (MB)": c["TX (MB)"], "RX (MB)": c["RX (MB)"],
                "Total (MB)": round(total_mb, 1),
                "Total (GB)": round(total_mb / 1000, 2),
            })
    return sorted(alerts, key=lambda x: x["Total (MB)"], reverse=True)


# --- Network Map ---
def build_network_map(device_list_data, client_list, classic_data):
    """Build a text-based network topology."""
    gateway = None
    switches = []
    aps = []
    for d in device_list_data:
        model = d.get("Model", "").lower()
        if "gateway" in model or "ugw" in model or "ucg" in model or "dream" in model:
            gateway = d
        elif "switch" in model or "usw" in model:
            switches.append(d)
        elif "ap" in model or "uap" in model or "u6" in model:
            aps.append(d)

    if not gateway and device_list_data:
        gateway = device_list_data[0]

    # Group clients by uplink
    uplink_groups = {}
    if classic_data:
        cl = classic_data.get("data", classic_data) if isinstance(classic_data, dict) else classic_data
        for c in (cl or []):
            uplink = c.get("last_uplink_name", "Unknown")
            if uplink not in uplink_groups:
                uplink_groups[uplink] = []
            uplink_groups[uplink].append({
                "name": c.get("hostname", c.get("name", "Unknown")),
                "ip": c.get("ip", "N/A"),
                "mac": c.get("mac", "N/A"),
            })

    return gateway, switches, aps, uplink_groups


# --- Firmware Checker ---
def check_firmware(device_list_data, devices_raw):
    """Check for firmware update availability."""
    fw_status = []
    raw_list = devices_raw if isinstance(devices_raw, list) else (devices_raw.get("data", []) if isinstance(devices_raw, dict) else [])
    for d in raw_list:
        fw_status.append({
            "Name": d.get("name", "Unknown"),
            "Model": d.get("model", "N/A"),
            "Current FW": d.get("firmwareVersion", "N/A"),
            "Update Available": "🔴 Yes" if d.get("firmwareUpdatable", False) else "🟢 Up to date",
            "Supported": "✅" if d.get("supported", True) else "⚠️ Unsupported",
        })
    return fw_status


# --- Guest Network ---
def get_guest_clients(classic_data):
    """Extract guest network clients."""
    guests = []
    if not classic_data:
        return guests
    cl = classic_data.get("data", classic_data) if isinstance(classic_data, dict) else classic_data
    for c in (cl or []):
        if c.get("is_guest", False):
            guests.append({
                "Name": c.get("hostname", c.get("name", "Unknown")),
                "IP": c.get("ip", "N/A"),
                "MAC": c.get("mac", "N/A"),
                "TX (MB)": round((c.get("wired-tx_bytes", c.get("tx_bytes", 0)) or 0) / 1_000_000, 1),
                "RX (MB)": round((c.get("wired-rx_bytes", c.get("rx_bytes", 0)) or 0) / 1_000_000, 1),
                "Network": c.get("network", c.get("essid", "N/A")),
            })
    return guests


# --- Scheduled Reports (SES) ---
SES_SENDER = os.getenv("SES_SENDER", "")
SES_RECIPIENT = os.getenv("SES_RECIPIENT", "")
SES_REGION = os.getenv("SES_REGION", "us-east-1")

def send_email_report(bedrock_client, ses_client, client_list, device_list_data, ctx):
    """Generate and send a weekly network report via SES."""
    if not SES_SENDER or not SES_RECIPIENT:
        return False, "SES_SENDER and SES_RECIPIENT not configured in .env"
    try:
        report = call_bedrock(bedrock_client,
            "Generate a comprehensive weekly network report with: Executive Summary, Device Inventory, "
            "Bandwidth Analysis (top consumers), Security Assessment, Uptime Summary, and Recommendations. "
            "Format in clean HTML suitable for email. Use tables where appropriate.",
            "Generate a weekly network report for email.", ctx)

        ses_client.send_email(
            Source=SES_SENDER,
            Destination={"ToAddresses": [SES_RECIPIENT]},
            Message={
                "Subject": {"Data": f"UniFi Weekly Network Report — {datetime.now().strftime('%Y-%m-%d')}"},
                "Body": {"Html": {"Data": report}},
            },
        )
        return True, "Report sent"
    except Exception as e:
        return False, str(e)

# --- Main App Logic ---
if not api_key:
    st.warning("Enter your UniFi API key in the sidebar to get started.")
    st.stop()

# Fetch data
with st.spinner("Fetching network data..."):
    sites_data = api_get("/sites")

if not sites_data:
    st.error("Failed to fetch sites. Check your API key and gateway connection.")
    st.stop()

sites_list = sites_data.get("data", sites_data) if isinstance(sites_data, dict) else sites_data

# Multi-site support
if isinstance(sites_list, list) and len(sites_list) > 1:
    site_options = {s.get("name", s.get("id", "default")): s.get("id", s.get("name", "default")) for s in sites_list}
    selected_site = st.sidebar.selectbox("Select Site", list(site_options.keys()))
    site_id = site_options[selected_site]
elif isinstance(sites_list, list) and sites_list:
    site_id = sites_list[0].get("id", sites_list[0].get("name", "default"))
else:
    site_id = "default"

st.sidebar.caption(f"Site: {site_id}")

with st.spinner("Fetching clients and devices..."):
    clients_data = api_get(f"/sites/{site_id}/clients")
    devices_data = api_get(f"/sites/{site_id}/devices")
    classic_clients = classic_api_get("/s/default/stat/sta")

clients = clients_data.get("data", clients_data) if isinstance(clients_data, dict) else (clients_data or [])
devices = devices_data.get("data", devices_data) if isinstance(devices_data, dict) else (devices_data or [])

# Build stats lookup (wired + wireless)
stats_by_mac = {}
if classic_clients:
    for c in (classic_clients.get("data", classic_clients) if isinstance(classic_clients, dict) else classic_clients) or []:
        mac = c.get("mac", "").lower()
        if mac:
            is_wired = c.get("is_wired", False)
            if is_wired:
                tx = c.get("wired-tx_bytes", c.get("tx_bytes", 0))
                rx = c.get("wired-rx_bytes", c.get("rx_bytes", 0))
                tx_r = c.get("wired-tx_bytes-r", 0)
                rx_r = c.get("wired-rx_bytes-r", 0)
                link = c.get("wired_rate_mbps", 0)
            else:
                tx = c.get("tx_bytes", 0)
                rx = c.get("rx_bytes", 0)
                tx_r = c.get("tx_bytes-r", 0)
                rx_r = c.get("rx_bytes-r", 0)
                link = c.get("tx_rate", 0)  # WiFi TX rate in kbps
                if link:
                    link = round(link / 1000, 0)  # Convert to Mbps
            stats_by_mac[mac] = {
                "tx_bytes": tx, "rx_bytes": rx,
                "tx_rate": tx_r, "rx_rate": rx_r,
                "hostname": c.get("hostname", ""), "oui": c.get("oui", ""),
                "link_speed": link, "is_guest": c.get("is_guest", False),
                "is_wired": is_wired,
                "essid": c.get("essid", ""),
                "channel": c.get("channel", ""),
                "signal": c.get("signal", c.get("rssi", "")),
                "satisfaction": c.get("satisfaction", ""),
                "uptime": c.get("uptime", 0),
                "first_seen": c.get("first_seen", 0),
                "last_seen": c.get("last_seen", 0),
            }

# Build device list
device_list = []
if devices:
    for d in (devices if isinstance(devices, list) else [devices]):
        device_list.append({
            "Name": d.get("name", "Unknown"), "Model": d.get("model", "N/A"),
            "MAC": d.get("macAddress", d.get("mac", "N/A")),
            "IP": d.get("ipAddress", d.get("ip", "N/A")),
            "State": d.get("state", "N/A"), "Firmware": d.get("firmwareVersion", "N/A"),
        })

# Build client list — use classic API as primary (has all clients), merge with integration API data
client_list = []
integration_by_mac = {}
if clients:
    for c in (clients if isinstance(clients, list) else [clients]):
        mac = c.get("macAddress", c.get("mac", "")).lower()
        integration_by_mac[mac] = c

# Use classic API clients as the source of truth (shows all connected devices)
classic_list = []
if classic_clients:
    classic_list = (classic_clients.get("data", classic_clients) if isinstance(classic_clients, dict) else classic_clients) or []

if classic_list:
    for c in classic_list:
        mac = c.get("mac", "").lower()
        integration = integration_by_mac.get(mac, {})
        is_wired = c.get("is_wired", False)

        if is_wired:
            tx_bytes = c.get("wired-tx_bytes", c.get("tx_bytes", 0)) or 0
            rx_bytes = c.get("wired-rx_bytes", c.get("rx_bytes", 0)) or 0
            tx_rate = c.get("wired-tx_bytes-r", 0) or 0
            rx_rate = c.get("wired-rx_bytes-r", 0) or 0
            link = c.get("wired_rate_mbps", 0)
        else:
            tx_bytes = c.get("tx_bytes", 0) or 0
            rx_bytes = c.get("rx_bytes", 0) or 0
            tx_rate = c.get("tx_bytes-r", 0) or 0
            rx_rate = c.get("rx_bytes-r", 0) or 0
            link = c.get("tx_rate", 0)
            if link:
                link = round(link / 1000, 0)

        conn_type = "WIRED" if is_wired else "WIRELESS"
        client_list.append({
            "Name": integration.get("name", c.get("hostname", c.get("name", "Unknown"))),
            "IP": c.get("ip", integration.get("ipAddress", "N/A")),
            "MAC": mac,
            "Type": conn_type, "Vendor": c.get("oui", "N/A"),
            "Link (Mbps)": link,
            "SSID": c.get("essid", ""),
            "Channel": c.get("channel", ""),
            "Signal": c.get("signal", c.get("rssi", "")),
            "TX (MB)": round(tx_bytes / 1_000_000, 1), "RX (MB)": round(rx_bytes / 1_000_000, 1),
            "TX Rate (KB/s)": round(tx_rate / 1_000, 1),
            "RX Rate (KB/s)": round(rx_rate / 1_000, 1),
            "Connected At": integration.get("connectedAt", "N/A"),
        })
elif clients:
    # Fallback to integration API if classic API unavailable
    for c in (clients if isinstance(clients, list) else [clients]):
        mac = c.get("macAddress", c.get("mac", "")).lower()
        stats = stats_by_mac.get(mac, {})
        tx_bytes = stats.get("tx_bytes", 0) or 0
        rx_bytes = stats.get("rx_bytes", 0) or 0
        conn_type = c.get("type", "N/A")
        client_list.append({
            "Name": c.get("name", c.get("hostname", stats.get("hostname", "Unknown"))),
            "IP": c.get("ipAddress", c.get("ip", "N/A")),
            "MAC": c.get("macAddress", c.get("mac", "N/A")),
            "Type": conn_type, "Vendor": stats.get("oui", "N/A"),
            "Link (Mbps)": stats.get("link_speed", "N/A"),
            "SSID": "", "Channel": "", "Signal": "",
            "TX (MB)": round(tx_bytes / 1_000_000, 1), "RX (MB)": round(rx_bytes / 1_000_000, 1),
            "TX Rate (KB/s)": round((stats.get("tx_rate", 0) or 0) / 1_000, 1),
            "RX Rate (KB/s)": round((stats.get("rx_rate", 0) or 0) / 1_000, 1),
            "Connected At": c.get("connectedAt", "N/A"),
        })

# Update uptime log
uptime_log = update_uptime_log(client_list)

wired = sum(1 for c in client_list if c.get("Type") == "WIRED")
total_tx = sum(c.get("TX (MB)", 0) for c in client_list)
total_rx = sum(c.get("RX (MB)", 0) for c in client_list)

# --- Dashboard Metrics ---
# Dynamic page title with client count
st.markdown(f"<script>document.title='{len(client_list)} clients | UniFi Dashboard'</script>", unsafe_allow_html=True)

# Gateway status
gw_device = next((d for d in device_list if "gateway" in d.get("Model", "").lower() or "ucg" in d.get("Model", "").lower()), None)
if gw_device:
    st.caption(f"🌐 {gw_device['Name']} ({gw_device['Model']}) — FW {gw_device['Firmware']} — {gw_device['State']}")

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("🖥️ Total", len(client_list))
col2.metric("🔌 Wired", wired)
col3.metric("📶 WiFi", len(client_list) - wired)
col4.metric("⬆️ TX", f"{total_tx/1000:.1f} GB" if total_tx > 1000 else f"{total_tx:.0f} MB")
col5.metric("⬇️ RX", f"{total_rx/1000:.1f} GB" if total_rx > 1000 else f"{total_rx:.0f} MB")
col6.metric("📡 Devices", len(device_list))

# --- Main Tabs ---
tab_devices, tab_clients, tab_wifi, tab_alerts, tab_map, tab_firmware, tab_guests, tab_device_hist, tab_heatmap, tab_parental, tab_block, tab_speed, tab_uptime, tab_history, tab_aws, tab_ai, tab_export = st.tabs([
    "Devices", "Clients", "WiFi", "Alerts", "Map", "Firmware",
    "Guests", "Device History", "Peak Hours", "Parental",
    "Block", "Speed",
    "Uptime", "Trends", "AWS", "AI", "Export"
])

with tab_devices:
    if device_list:
        st.dataframe(pd.DataFrame(device_list), width="stretch", hide_index=True)
    else:
        st.info("No network devices found.")

# --- Clients Tab ---
with tab_clients:
    if client_list:
        df_clients = pd.DataFrame(client_list)
        search = st.text_input("Search clients", placeholder="Filter by name, IP, or MAC...")
        if search:
            mask = df_clients.apply(lambda row: search.lower() in str(row).lower(), axis=1)
            df_clients = df_clients[mask]
        st.dataframe(df_clients.sort_values("RX (MB)", ascending=False), width="stretch", hide_index=True)

        st.subheader("📊 Top 10 Clients by Data Usage")
        top = df_clients.nlargest(10, "RX (MB)")
        st.bar_chart(top.set_index("Name")[["TX (MB)", "RX (MB)"]])
    else:
        st.info("No clients found.")

# --- Bandwidth Alerts Tab ---
with tab_alerts:
    st.subheader("🚨 Bandwidth Alerts")
    threshold = st.slider("Alert threshold (MB)", 100, 10000, BANDWIDTH_THRESHOLD_MB, step=100, key="bw_thresh")
    alerts = get_bandwidth_alerts(client_list, threshold)
    if alerts:
        st.error(f"{len(alerts)} device(s) exceeding {threshold} MB ({threshold/1000:.1f} GB)")
        df_alerts = pd.DataFrame(alerts)
        st.dataframe(df_alerts, width="stretch", hide_index=True)

        st.subheader("📊 High Bandwidth Devices")
        st.bar_chart(df_alerts.set_index("Name")[["TX (MB)", "RX (MB)"]])
    else:
        st.success(f"No devices exceeding {threshold} MB threshold")

# --- Network Map Tab ---
with tab_map:
    st.subheader("🗺️ Network Topology")
    gw, switches, aps, uplink_groups = build_network_map(device_list, client_list, classic_clients)

    if gw:
        st.markdown(f"### 🌐 Gateway: {gw['Name']}")
        st.caption(f"Model: {gw['Model']} | IP: {gw['IP']} | FW: {gw['Firmware']} | State: {gw['State']}")
        st.markdown("---")

        if switches:
            for sw in switches:
                st.markdown(f"  ├── 🔀 Switch: {sw['Name']} ({sw['Model']}) — {sw['IP']}")
        if aps:
            for ap in aps:
                st.markdown(f"  ├── 📶 AP: {ap['Name']} ({ap['Model']}) — {ap['IP']}")

        st.markdown("---")
        st.markdown("### Connected Devices by Uplink")
        if uplink_groups:
            for uplink, devs in uplink_groups.items():
                with st.expander(f"📡 {uplink} ({len(devs)} devices)"):
                    for d in devs:
                        st.caption(f"  └── {d['name']} — IP: {d['ip']} | MAC: {d['mac']}")
        else:
            st.markdown("### All Clients")
            for c in client_list[:30]:
                st.caption(f"  └── {c['Name']} — IP: {c['IP']} | MAC: {c['MAC']} | {c['Type']}")
    else:
        st.info("No gateway device found.")

# --- Firmware Tab ---
with tab_firmware:
    st.subheader("🔄 Firmware Status")
    devices_raw = devices_data.get("data", devices_data) if isinstance(devices_data, dict) else (devices_data or [])
    fw_list = check_firmware(device_list, devices_raw)
    if fw_list:
        df_fw = pd.DataFrame(fw_list)
        updates_needed = sum(1 for f in fw_list if "Yes" in f["Update Available"])
        if updates_needed:
            st.warning(f"{updates_needed} device(s) have firmware updates available")
        else:
            st.success("All devices are up to date")
        st.dataframe(df_fw, width="stretch", hide_index=True)
    else:
        st.info("No device firmware data available.")

# --- Guest Network Tab ---
with tab_guests:
    st.subheader("👤 Guest Network Management")
    guests = get_guest_clients(classic_clients)
    if guests:
        st.metric("Guest Clients", len(guests))
        df_guests = pd.DataFrame(guests)
        st.dataframe(df_guests, width="stretch", hide_index=True)

        total_guest_tx = sum(g.get("TX (MB)", 0) for g in guests)
        total_guest_rx = sum(g.get("RX (MB)", 0) for g in guests)
        g1, g2 = st.columns(2)
        g1.metric("Guest TX", f"{total_guest_tx:.1f} MB")
        g2.metric("Guest RX", f"{total_guest_rx:.1f} MB")

        # Block guest option
        if guests:
            guest_names = {f"{g['Name']} ({g['IP']} - {g['MAC']})": g['MAC'] for g in guests}
            sel_guest = st.selectbox("Select guest to block", list(guest_names.keys()), key="guest_sel")
            if st.button("🔴 Block Guest", key="block_guest"):
                result = block_client(guest_names[sel_guest])
                if "error" not in result:
                    st.success(f"Blocked {sel_guest}")
                else:
                    st.error(f"Failed: {result['error']}")
    else:
        st.info("No guest clients currently connected.")

# --- WiFi Clients Tab ---
with tab_wifi:
    st.subheader("📶 WiFi Clients")
    wifi_clients = [c for c in client_list if c.get("Type") not in ("WIRED", True)]
    wired_clients = [c for c in client_list if c.get("Type") in ("WIRED", True)]

    w1, w2 = st.columns(2)
    w1.metric("WiFi Clients", len(wifi_clients))
    w2.metric("Wired Clients", len(wired_clients))

    if wifi_clients:
        df_wifi = pd.DataFrame(wifi_clients)
        # Show WiFi-specific columns
        wifi_cols = ["Name", "IP", "MAC", "SSID", "Channel", "Signal", "Link (Mbps)", "TX (MB)", "RX (MB)", "TX Rate (KB/s)", "RX Rate (KB/s)"]
        available_cols = [c for c in wifi_cols if c in df_wifi.columns]
        st.dataframe(df_wifi[available_cols].sort_values("RX (MB)", ascending=False), width="stretch", hide_index=True)

        # WiFi vs Wired bandwidth comparison
        st.subheader("📊 WiFi vs Wired Bandwidth")
        wifi_tx = sum(c.get("TX (MB)", 0) for c in wifi_clients)
        wifi_rx = sum(c.get("RX (MB)", 0) for c in wifi_clients)
        wired_tx = sum(c.get("TX (MB)", 0) for c in wired_clients)
        wired_rx = sum(c.get("RX (MB)", 0) for c in wired_clients)
        comp_df = pd.DataFrame({
            "Type": ["WiFi", "Wired"],
            "TX (MB)": [wifi_tx, wired_tx],
            "RX (MB)": [wifi_rx, wired_rx],
        })
        st.bar_chart(comp_df.set_index("Type"))

        # Signal strength distribution
        signals = [c.get("Signal", "") for c in wifi_clients if c.get("Signal")]
        if signals:
            st.subheader("📡 Signal Strength")
            sig_nums = [int(s) for s in signals if str(s).lstrip("-").isdigit()]
            if sig_nums:
                sig_df = pd.DataFrame({"Signal (dBm)": sig_nums})
                st.bar_chart(sig_df.value_counts().sort_index())
    else:
        st.info("No WiFi clients connected.")

# --- Per-Device Bandwidth History Tab ---
with tab_device_hist:
    st.subheader("📊 Per-Device Bandwidth History")
    if client_list and ENABLE_AWS:
        aws_h = get_aws_clients()
        if aws_h:
            device_select = st.selectbox("Select device",
                [f"{c['Name']} ({c['IP']})" for c in client_list], key="dev_hist_sel")
            sel_mac = client_list[[f"{c['Name']} ({c['IP']})" for c in client_list].index(device_select)]["MAC"]

            days_hist = st.slider("Days", 1, 30, 7, key="dev_hist_days")
            history = get_historical_data(aws_h["dynamodb"], days_hist)

            if history:
                dev_history = []
                for h in history:
                    try:
                        snap_clients = json.loads(h.get("clients", "[]"))
                        for sc in snap_clients:
                            if sc.get("mac", "").lower() == sel_mac.lower():
                                dev_history.append({
                                    "Time": h.get("timestamp", "")[:16],
                                    "TX (MB)": sc.get("tx_mb", 0),
                                    "RX (MB)": sc.get("rx_mb", 0),
                                })
                    except (json.JSONDecodeError, TypeError):
                        pass

                if dev_history:
                    df_dev = pd.DataFrame(dev_history)
                    st.line_chart(df_dev.set_index("Time")[["TX (MB)", "RX (MB)"]])
                    st.dataframe(df_dev, width="stretch", hide_index=True)
                else:
                    st.info("No historical data for this device yet.")
            else:
                st.info("No snapshots found. Save snapshots from the AWS tab first.")
    elif not ENABLE_AWS:
        st.info("Enable AWS in .env to use device history.")
    else:
        st.info("No clients to show.")

# --- Peak Hours Heatmap Tab ---
with tab_heatmap:
    st.subheader("🕐 Network Usage by Time of Day")
    if ENABLE_AWS:
        aws_hm = get_aws_clients()
        if aws_hm:
            days_hm = st.slider("Days of data", 1, 30, 7, key="heatmap_days")
            history_hm = get_historical_data(aws_hm["dynamodb"], days_hm)

            if history_hm:
                hm_data = []
                for h in history_hm:
                    ts = h.get("timestamp", "")
                    if len(ts) >= 16:
                        try:
                            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            hm_data.append({
                                "Hour": dt.hour,
                                "Day": dt.strftime("%a"),
                                "Clients": int(h.get("client_count", 0)),
                                "TX (MB)": int(h.get("total_tx_mb", 0)),
                                "RX (MB)": int(h.get("total_rx_mb", 0)),
                            })
                        except (ValueError, TypeError):
                            pass

                if hm_data:
                    hm_df = pd.DataFrame(hm_data)

                    # Average by hour
                    hourly = hm_df.groupby("Hour").agg({
                        "Clients": "mean", "TX (MB)": "mean", "RX (MB)": "mean"
                    }).round(1)

                    st.subheader("📊 Average Clients by Hour")
                    st.bar_chart(hourly[["Clients"]])

                    st.subheader("📊 Average Bandwidth by Hour")
                    st.bar_chart(hourly[["TX (MB)", "RX (MB)"]])

                    # Day of week breakdown
                    daily = hm_df.groupby("Day").agg({
                        "Clients": "mean", "RX (MB)": "sum"
                    }).round(1)
                    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                    daily = daily.reindex([d for d in day_order if d in daily.index])

                    st.subheader("📊 Usage by Day of Week")
                    st.bar_chart(daily[["RX (MB)"]])

                    # Peak hour identification
                    peak_hour = hourly["Clients"].idxmax()
                    peak_bw_hour = hourly["RX (MB)"].idxmax()
                    st.info(f"Peak client hour: {peak_hour}:00 | Peak bandwidth hour: {peak_bw_hour}:00")
                else:
                    st.info("Not enough data to generate heatmap.")
            else:
                st.info("No snapshots found. Save snapshots from the AWS tab first.")
    else:
        st.info("Enable AWS in .env to use peak hours analysis.")

# --- Parental Controls Tab ---
with tab_parental:
    st.subheader("👨‍👩‍👧 Parental Controls")
    st.caption("Schedule internet access per device")

    PARENTAL_FILE = ".parental_rules.json"

    def load_parental_rules():
        if os.path.exists(PARENTAL_FILE):
            with open(PARENTAL_FILE) as f:
                return json.load(f)
        return {}

    def save_parental_rules(rules):
        with open(PARENTAL_FILE, "w") as f:
            json.dump(rules, f, indent=2)

    rules = load_parental_rules()

    if client_list:
        # Add new rule
        st.markdown("### Add Schedule")
        p_device = st.selectbox("Device", [f"{c['Name']} ({c['MAC']})" for c in client_list], key="parental_dev")
        p_mac = p_device.split("(")[-1].rstrip(")")

        pc1, pc2 = st.columns(2)
        with pc1:
            p_start = st.time_input("Block from", value=None, key="p_start")
        with pc2:
            p_end = st.time_input("Block until", value=None, key="p_end")

        p_days = st.multiselect("Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                                default=["Mon", "Tue", "Wed", "Thu", "Fri"], key="p_days")

        if st.button("➕ Add Rule", key="add_parental"):
            if p_start and p_end and p_days:
                if p_mac not in rules:
                    rules[p_mac] = []
                rules[p_mac].append({
                    "device": p_device.split(" (")[0],
                    "start": p_start.strftime("%H:%M"),
                    "end": p_end.strftime("%H:%M"),
                    "days": p_days,
                    "active": True,
                })
                save_parental_rules(rules)
                st.success(f"Rule added for {p_device.split(' (')[0]}")
            else:
                st.warning("Please set start time, end time, and days.")

        # Show existing rules
        if rules:
            st.markdown("### Active Rules")
            for mac, mac_rules in rules.items():
                for i, rule in enumerate(mac_rules):
                    status = "🟢 Active" if rule.get("active", True) else "🔴 Disabled"
                    st.markdown(f"**{rule.get('device', mac)}** — {rule['start']} to {rule['end']} on {', '.join(rule['days'])} {status}")

                    rc1, rc2, rc3 = st.columns(3)
                    with rc1:
                        if st.button("🔴 Block Now", key=f"pblock_{mac}_{i}"):
                            result = block_client(mac)
                            if "error" not in result:
                                st.success(f"Blocked {rule.get('device', mac)}")
                    with rc2:
                        if st.button("🟢 Unblock", key=f"punblock_{mac}_{i}"):
                            result = unblock_client(mac)
                            if "error" not in result:
                                st.success(f"Unblocked {rule.get('device', mac)}")
                    with rc3:
                        if st.button("🗑️ Delete Rule", key=f"pdel_{mac}_{i}"):
                            rules[mac].pop(i)
                            if not rules[mac]:
                                del rules[mac]
                            save_parental_rules(rules)
                            st.rerun()

            # Auto-enforce check
            now_time = datetime.now()
            now_day = now_time.strftime("%a")
            now_hm = now_time.strftime("%H:%M")
            enforced = []
            for mac, mac_rules in rules.items():
                for rule in mac_rules:
                    if rule.get("active") and now_day in rule.get("days", []):
                        if rule["start"] <= now_hm <= rule["end"]:
                            enforced.append(rule.get("device", mac))
            if enforced:
                st.warning(f"Devices currently in blocked schedule: {', '.join(enforced)}")
                st.caption("Use the Block Now buttons above to enforce, or set up automation via EventBridge + Lambda.")
    else:
        st.info("No clients available.")

# --- Block/Unblock Tab (original) ---
with tab_block:
    st.subheader("🚫 Device Access Control")
    if client_list:
        device_names = {f"{c['Name']} ({c['IP']} - {c['MAC']})": c['MAC'] for c in client_list}
        selected = st.selectbox("Select a device", list(device_names.keys()))
        sel_mac = device_names[selected]

        col_block, col_unblock = st.columns(2)
        with col_block:
            if st.button("🔴 Block Device", type="primary"):
                result = block_client(sel_mac)
                if "error" not in result:
                    st.success(f"Blocked {selected}")
                else:
                    st.error(f"Failed: {result['error']}")
        with col_unblock:
            if st.button("🟢 Unblock Device"):
                result = unblock_client(sel_mac)
                if "error" not in result:
                    st.success(f"Unblocked {selected}")
                else:
                    st.error(f"Failed: {result['error']}")
    else:
        st.info("No clients to manage.")

# --- Speed Test Tab ---
with tab_speed:
    st.subheader("⚡ Speed Tests")

    # Detect if running on ECS (no /Volumes/file)
    is_local = os.path.exists("/Volumes/file")

    if is_local:
        sp1, sp2 = st.columns(2)

        with sp1:
            st.markdown("**🌐 Internet Speed Test**")
            st.caption("Tests your home internet download/upload speed")
            if st.button("Run Internet Speed Test", key="inet_speed"):
                with st.spinner("Testing internet speed (this takes ~30 seconds)..."):
                    inet = run_internet_speed_test()
                    if inet.get("success"):
                        st.metric("Download", f"{inet['download_mbps']} Mbps")
                        st.metric("Upload", f"{inet['upload_mbps']} Mbps")
                        st.metric("Ping", f"{inet['ping_ms']} ms")
                        st.caption(f"Server: {inet['server']} | ISP: {inet['isp']}")
                    else:
                        st.error(inet.get("error"))

        with sp2:
            st.markdown("**💾 NAS Speed Test**")
            st.caption("Tests read/write speed to /Volumes/file")
            if st.button("Run NAS Speed Test", key="nas_speed"):
                with st.spinner("Testing NAS speed (~30 seconds)..."):
                    nas = run_speed_test()
                    if nas.get("success"):
                        st.metric("Write Speed", f"{nas['write_mbps']} Mbps")
                        st.metric("Read Speed", f"{nas['read_mbps']} Mbps")
                    else:
                        st.error(nas.get("error"))
    else:
        # Running on ECS — show VPN health test instead
        st.markdown("**🔗 VPN Health Check**")
        st.caption("Tests connectivity and latency from AWS to your home gateway via VPN")

        if st.button("Run VPN Health Check", key="vpn_health"):
            with st.spinner("Testing VPN connectivity..."):
                try:
                    # Test HTTPS connectivity to gateway
                    start = time.time()
                    resp = requests.get(f"https://{GATEWAY_IP}/proxy/network/integration/v1/sites",
                                       headers=HEADERS, verify=False, timeout=10)
                    latency = round((time.time() - start) * 1000, 1)

                    if resp.status_code == 200:
                        st.success(f"VPN is healthy — Gateway reachable")
                        v1, v2, v3 = st.columns(3)
                        v1.metric("API Latency", f"{latency} ms")
                        v2.metric("Status Code", resp.status_code)
                        v3.metric("Gateway", GATEWAY_IP)
                    else:
                        st.warning(f"Gateway responded with status {resp.status_code} ({latency} ms)")

                    # Multiple pings for average
                    latencies = []
                    for _ in range(5):
                        s = time.time()
                        try:
                            requests.get(f"https://{GATEWAY_IP}", verify=False, timeout=5)
                            latencies.append(round((time.time() - s) * 1000, 1))
                        except Exception:
                            latencies.append(None)

                    valid = [l for l in latencies if l is not None]
                    if valid:
                        st.markdown("**Latency over 5 requests:**")
                        l1, l2, l3 = st.columns(3)
                        l1.metric("Min", f"{min(valid)} ms")
                        l2.metric("Avg", f"{round(sum(valid)/len(valid), 1)} ms")
                        l3.metric("Max", f"{max(valid)} ms")
                        failed = len(latencies) - len(valid)
                        if failed:
                            st.warning(f"{failed}/5 requests failed")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach gateway — VPN may be down")
                except requests.exceptions.Timeout:
                    st.error("Gateway timed out — VPN may be experiencing issues")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- Uptime Monitor Tab ---
with tab_uptime:
    st.subheader("⏱️ Device Uptime Monitor")
    if uptime_log:
        uptime_data = []
        now_ts = datetime.now()
        for mac, info in uptime_log.items():
            last_event = info["events"][-1] if info["events"] else None
            # Calculate uptime percentage from events
            online_time = 0
            offline_time = 0
            events = info.get("events", [])
            for i, evt in enumerate(events):
                evt_time = datetime.fromisoformat(evt["time"])
                if i + 1 < len(events):
                    next_time = datetime.fromisoformat(events[i + 1]["time"])
                else:
                    next_time = now_ts
                duration = (next_time - evt_time).total_seconds()
                if evt["type"] == "online":
                    online_time += duration
                else:
                    offline_time += duration
            total_time = online_time + offline_time
            uptime_pct = round((online_time / total_time) * 100, 1) if total_time > 0 else 100.0 if info["status"] == "online" else 0.0
            offline_events = sum(1 for e in events if e["type"] == "offline")

            uptime_data.append({
                "Device": info.get("name", mac),
                "MAC": mac,
                "Status": "🟢 Online" if info["status"] == "online" else "🔴 Offline",
                "Uptime %": uptime_pct,
                "Offline Events": offline_events,
                "Last Seen": info.get("last_seen", "N/A")[:19],
                "Last Event": f"{last_event['type']} at {last_event['time'][:19]}" if last_event else "N/A",
            })

        df_uptime = pd.DataFrame(uptime_data).sort_values("Uptime %", ascending=True)
        
        # Summary stats
        total_devices = len(uptime_data)
        online_count = sum(1 for d in uptime_data if "Online" in d["Status"])
        offline_count = total_devices - online_count
        avg_uptime = round(sum(d["Uptime %"] for d in uptime_data) / total_devices, 1) if total_devices else 0

        u1, u2, u3, u4 = st.columns(4)
        u1.metric("Tracked Devices", total_devices)
        u2.metric("Online Now", online_count)
        u3.metric("Offline Now", offline_count)
        u4.metric("Avg Uptime", f"{avg_uptime}%")

        st.dataframe(df_uptime, width="stretch", hide_index=True)

        # Uptime chart
        st.subheader("📊 Uptime by Device")
        chart_df = df_uptime.set_index("Device")[["Uptime %"]].sort_values("Uptime %")
        st.bar_chart(chart_df)

        # Offline alerts
        offline = [d for d in uptime_data if "Offline" in d["Status"]]
        if offline:
            st.warning(f"{len(offline)} device(s) currently offline")
            for d in offline:
                st.caption(f"  🔴 {d['Device']} ({d['MAC']}) — last seen {d['Last Seen']} — uptime {d['Uptime %']}%")

        # Least reliable devices
        unreliable = [d for d in uptime_data if d["Offline Events"] > 0]
        if unreliable:
            st.subheader("⚠️ Least Reliable Devices")
            unreliable_sorted = sorted(unreliable, key=lambda x: x["Uptime %"])[:5]
            for d in unreliable_sorted:
                st.caption(f"  {d['Device']} — {d['Uptime %']}% uptime, {d['Offline Events']} offline event(s)")
    else:
        st.info("No uptime data yet. Data will accumulate as the dashboard runs.")

# --- History Tab ---
with tab_history:
    st.subheader("📈 Historical Network Data")
    if ENABLE_AWS:
        aws = get_aws_clients()
        if aws:
            days = st.slider("Days of history", 1, 30, 7, key="hist_days")
            history = get_historical_data(aws["dynamodb"], days)
            if history:
                hist_df = pd.DataFrame([{
                    "Time": h.get("timestamp", "")[:16],
                    "Clients": int(h.get("client_count", 0)),
                    "TX (MB)": int(h.get("total_tx_mb", 0)),
                    "RX (MB)": int(h.get("total_rx_mb", 0)),
                } for h in history])
                st.line_chart(hist_df.set_index("Time")[["Clients"]])
                st.line_chart(hist_df.set_index("Time")[["TX (MB)", "RX (MB)"]])
                st.dataframe(hist_df, width="stretch", hide_index=True)
            else:
                st.info("No historical data yet. Use 'Save Snapshot to DynamoDB' in the AWS tab to start collecting.")
    else:
        st.info("Enable AWS in .env to view historical data.")

# --- AWS Tab ---
with tab_aws:
    st.subheader("☁️ AWS Integration")
    if ENABLE_AWS:
        aws = get_aws_clients()
        if aws and client_list:
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("📊 Push to CloudWatch"):
                    if push_cloudwatch_metrics(aws["cloudwatch"], len(client_list), wired, total_tx, total_rx):
                        st.success("Metrics pushed")
            with c2:
                if st.button("🔔 Check New Devices"):
                    new = check_new_devices_and_alert(aws["sns"], client_list)
                    if new:
                        st.success(f"Found {len(new)} new device(s)")
                    else:
                        st.success("No new devices")
            with c3:
                if st.button("💾 Save Snapshot"):
                    if save_snapshot(aws["dynamodb"], client_list, len(device_list)):
                        st.success("Snapshot saved")

            with st.expander("AWS Status"):
                st.write(f"Region: {AWS_REGION}")
                st.write(f"SNS Topic: {SNS_TOPIC_ARN or 'Not configured'}")
                st.write(f"DynamoDB Table: {DYNAMODB_TABLE}")

            # Auto-save snapshot every refresh
            if "last_snapshot" not in st.session_state:
                st.session_state.last_snapshot = None
            now = datetime.now()
            if st.session_state.last_snapshot is None or (now - st.session_state.last_snapshot).total_seconds() >= 300:
                save_snapshot(aws["dynamodb"], client_list, len(device_list))
                st.session_state.last_snapshot = now
    else:
        st.info("Set `ENABLE_AWS=true` in .env to enable.")

# --- AI Intelligence Tab ---
with tab_ai:
    st.subheader("🤖 AI Network Intelligence (Amazon Bedrock)")
    if ENABLE_AWS:
        bedrock = get_bedrock_client()
        if bedrock and client_list:
            ctx = build_network_context(client_list, device_list)

            ai1, ai2, ai3, ai4, ai5 = st.tabs([
                "📝 Summary", "🔍 Anomalies", "🛡️ Security", "🏷️ Categorize", "💬 Chat"
            ])

            with ai1:
                if st.button("Generate Summary", key="ai_sum"):
                    with st.spinner("Analyzing..."):
                        st.markdown(ai_summary(bedrock, ctx))

            with ai2:
                if st.button("Scan Anomalies", key="ai_anom"):
                    with st.spinner("Scanning..."):
                        st.markdown(ai_anomalies(bedrock, ctx))

            with ai3:
                if st.button("Get Recommendations", key="ai_sec"):
                    with st.spinner("Analyzing..."):
                        st.markdown(ai_security(bedrock, ctx))

            with ai4:
                if st.button("Categorize Devices", key="ai_cat"):
                    with st.spinner("Categorizing..."):
                        st.markdown(ai_categorize(bedrock, ctx))

            with ai5:
                if "ai_messages" not in st.session_state:
                    st.session_state.ai_messages = []
                for msg in st.session_state.ai_messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                if q := st.chat_input("Ask about your network..."):
                    st.session_state.ai_messages.append({"role": "user", "content": q})
                    with st.chat_message("user"):
                        st.markdown(q)
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            ans = ai_chat(bedrock, ctx, q)
                            st.markdown(ans)
                            st.session_state.ai_messages.append({"role": "assistant", "content": ans})
        else:
            st.warning("Bedrock not available. Check AWS credentials.")
    else:
        st.info("Enable AWS in .env to use AI features.")

# --- Export Tab ---
with tab_export:
    st.subheader("📄 Export Reports")
    if client_list:
        c1, c2 = st.columns(2)
        with c1:
            csv_data = export_csv(pd.DataFrame(client_list))
            st.download_button("📥 Download CSV", csv_data, "unifi_clients.csv", "text/csv")
        with c2:
            json_data = export_json_report(client_list, device_list)
            st.download_button("📥 Download JSON Report", json_data, "unifi_report.json", "application/json")

        if ENABLE_AWS:
            bedrock = get_bedrock_client()
            if bedrock:
                if st.button("📝 Generate AI Report"):
                    with st.spinner("Generating comprehensive report..."):
                        ctx = build_network_context(client_list, device_list)
                        report = call_bedrock(bedrock,
                            "Generate a comprehensive network report with sections: Executive Summary, Device Inventory, "
                            "Bandwidth Analysis, Security Assessment, and Recommendations. Format in clean markdown.",
                            "Generate a full network report.", ctx)
                        st.markdown(report)
                        st.download_button("📥 Download AI Report", report.encode("utf-8"),
                                           "unifi_ai_report.md", "text/markdown", key="dl_ai_report")

                st.divider()
                st.subheader("📧 Email Report (via SES)")
                if SES_SENDER and SES_RECIPIENT:
                    st.caption("✅ Email configured")
                    if st.button("📧 Send Weekly Report Now", key="send_email"):
                        with st.spinner("Generating and sending report..."):
                            try:
                                ses = boto3.client("ses", region_name=SES_REGION)
                                ctx = build_network_context(client_list, device_list)
                                ok, msg = send_email_report(bedrock, ses, client_list, device_list, ctx)
                                if ok:
                                    st.success("Report sent to " + SES_RECIPIENT)
                                else:
                                    st.error(f"Failed: {msg}")
                            except Exception as e:
                                st.error(f"SES error: {e}")
                else:
                    st.info("Add `SES_SENDER` and `SES_RECIPIENT` to your .env to enable email reports.")
    else:
        st.info("No data to export.")

# --- Footer ---
st.divider()
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Gateway: {GATEWAY_IP} | Site: {site_id}")
