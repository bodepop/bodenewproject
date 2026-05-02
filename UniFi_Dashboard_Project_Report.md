# UniFi Network Dashboard — Project Report

## 1. Project Overview

This project involved the design, development, and deployment of a comprehensive real-time network monitoring dashboard. The dashboard connects to a UniFi Cloud Gateway Fiber via its API, collects data on all connected devices, and presents it through an interactive web interface built with Streamlit. The application integrates with multiple AWS services including Amazon Bedrock for AI-powered network intelligence, DynamoDB for historical data storage, CloudWatch for metrics, and is deployed on AWS ECS Fargate with an Application Load Balancer for production hosting.

The dashboard provides full visibility into a home network of 32+ devices, with features ranging from bandwidth monitoring and device management to AI-driven anomaly detection and automated reporting.

---

## 2. Technology Stack

| Component | Technology |
|-----------|-----------|
| Programming Language | Python 3.14 |
| Web Framework | Streamlit |
| Containerisation | Docker |
| Container Registry | Amazon ECR |
| Compute | AWS ECS Fargate |
| Load Balancer | AWS Application Load Balancer (ALB) |
| AI/ML | Amazon Bedrock (Claude Sonnet 4) |
| Database | Amazon DynamoDB |
| Monitoring | Amazon CloudWatch |
| Notifications | Amazon SNS |
| Email | Amazon SES |
| Networking | AWS Site-to-Site VPN, Transit Gateway |
| Workflow Orchestration | AWS Step Functions |
| Storage | Amazon S3 |
| Source Control | Git, GitHub |
| API | UniFi Integration API v1, UniFi Classic API |

---

## 3. Home Network Architecture

The dashboard monitors a home network built around the following infrastructure:

**Core Network Equipment:**
- UniFi Cloud Gateway Fiber (UCG Fiber) — primary router, firewall, and DHCP server running firmware 5.0.16
- TP-Link Deco BE95 — WiFi 7 mesh system operating in AP (Access Point) mode, providing wireless coverage across the home
- eero — additional WiFi mesh coverage in bridge mode
- Ugreen HomeCloud NAS — network-attached storage at 192.168.1.186, connected via 2.5GbE achieving approximately 288 MB/s read and write speeds

**Connected Devices (32+):**
The network serves a diverse range of devices including Apple iPhones, iPads, Apple Watch, Mac Mini, Samsung smart appliances (washer, dryer), Ring video doorbells and chime pros, Amazon Echo devices, Bose Smart Speaker 500, Marantz Cinema 60 AV receiver, LG webOS TV, Sky TV boxes, TP-Link smart plugs, and a Hive smart home hub.

**Network Design:**
The UniFi Cloud Gateway Fiber handles all routing, DHCP, and firewall duties. The Deco BE95 mesh nodes and eero operate in AP mode, meaning they provide WiFi coverage without running their own DHCP or NAT. This ensures all devices receive IP addresses from the UniFi gateway and appear in the UniFi controller for monitoring. The network operates on the 192.168.1.0/24 subnet.

---

## 4. AWS Cloud Architecture

### 4.1 VPC and Networking

The application is deployed in the default VPC (`vpc-1f39177b`) in the `eu-west-1` (Ireland) region. This VPC connects to the home network through the following path:

- **Transit Gateway** (`tgw-0f42bf4ebbe6f0289`) — central hub connecting the VPC and VPN
- **Site-to-Site VPN** (`vpn-0cdde910168d358a9`) — encrypted tunnel between AWS and the home network
- **Route Table** — contains a route for `192.168.1.0/24` pointing to the Transit Gateway

This architecture allows the ECS Fargate tasks running in AWS to reach the UniFi gateway at `192.168.1.1` through the VPN tunnel, enabling the dashboard to query the UniFi API from the cloud.

### 4.2 ECS Fargate Deployment

The application runs as a containerised service on ECS Fargate:

- **Cluster:** `unifi-dashboard`
- **Service:** `unifi-dashboard` with desired count of 1
- **Task Definition:** 0.5 vCPU, 1 GB RAM, Fargate launch type
- **Container Image:** Hosted in ECR at `672603477912.dkr.ecr.eu-west-1.amazonaws.com/unifi-dashboard`
- **Networking:** Deployed in subnets `subnet-02e3dc66` (eu-west-1a) and `subnet-27c3bb7f` (eu-west-1c) with public IP assignment enabled

### 4.3 Application Load Balancer

- **ALB:** `unifi-dashboard-alb` (internet-facing)
- **DNS:** `unifi-dashboard-alb-598094223.eu-west-1.elb.amazonaws.com`
- **Listener:** HTTP on port 80 forwarding to the target group
- **Target Group:** `unifi-dashboard-tg` targeting port 8501 (Streamlit) with health checks on `/_stcore/health`
- **Sticky Sessions:** Enabled with load balancer cookies (86400 second duration) — required for Streamlit's WebSocket connections

### 4.4 IAM Roles

Three IAM roles support the deployment:

- **ecsTaskExecutionRole** — allows ECS to pull container images from ECR and write logs to CloudWatch
- **ecsUnifiDashboardTaskRole** — grants the running application access to DynamoDB, CloudWatch, SNS, SES, and Bedrock
- **unifi-report-lambda-role** — grants the weekly report Lambda function access to DynamoDB (read), Bedrock, SES, and CloudWatch Logs

### 4.5 Security Group

Security group `sg-04b69162` controls access:
- Inbound port 80 restricted to home public IP only (IP-locked access)
- Inbound all traffic from `192.168.1.0/24` (home network via VPN)
- Inbound all traffic from `172.31.0.0/16` (VPC internal)
- Inbound port 3389 from specific AWS IP ranges (RDP access)

### 4.6 Automated Weekly Reports (Lambda + EventBridge)

A serverless pipeline generates and emails AI-powered network reports every Monday at 9am UTC:

- **Lambda Function:** `unifi-weekly-report` (Python 3.12, 256MB, 300s timeout)
- **EventBridge Rule:** `unifi-weekly-report` with cron expression `cron(0 9 ? * MON *)`
- **Architecture:** The Lambda runs outside the VPC (no NAT Gateway needed), reads the latest network snapshot from DynamoDB, generates a comprehensive HTML report using Amazon Bedrock (Claude Sonnet 4), and sends it via Amazon SES (us-east-1)
- **Cost:** Approximately $0.10-0.20/month (Bedrock tokens only; Lambda, EventBridge, and SES fall within free tier)

### 4.7 Amazon SES Configuration

- **Region:** us-east-1
- **Sender:** admin@bodeconsulting.com (verified identity)
- **Recipient:** bode@bodeconsulting.com (verified identity)
- **Usage:** Weekly automated reports and on-demand report generation from the dashboard

### 4.8 Automated Incident Response (Step Functions)

An automated network incident response system monitors the network every 15 minutes using AWS Step Functions:

- **State Machine:** `unifi-incident-response`
- **EventBridge Rule:** `unifi-incident-check` with schedule `cron(0 9 * * ? *)` (daily at 9am UTC)
- **Architecture:** A 4-step serverless workflow:

```
EventBridge (daily at 9am UTC) → Step Function:
  Step 1: Scan Network (Lambda) → Read latest snapshot from DynamoDB
  Step 2: Detect Anomalies (Lambda) → Compare with known devices, check bandwidth
  Step 3: Decision: Anomaly found?
     ├── Yes → Analyze with Bedrock AI (Lambda) → Get risk assessment
     │         ├── HIGH severity → SNS alert + email + save to S3
     │         └── MEDIUM severity → email + save to S3
     └── No → Log "all clear" and stop
  Step 4: Respond (Lambda) → Save incident report to S3, send alerts
```

- **Lambda Functions:**
  - `unifi-scan-network` — reads latest network snapshot from DynamoDB
  - `unifi-detect-anomalies` — compares current devices against known devices, checks bandwidth thresholds
  - `unifi-analyze-bedrock` — sends anomaly data to Claude Sonnet 4 for AI risk assessment
  - `unifi-respond-incident` — saves incident report to S3, sends SNS/SES alerts based on severity

- **Anomaly Detection:**
  - Unknown device detection — alerts when a MAC address not in the known devices list appears
  - Bandwidth threshold — alerts when any device exceeds 5GB of data usage
  - De-duplication — uses DynamoDB table `unifi-alerted-incidents` with 24-hour TTL to prevent repeat alerts for the same incident

- **Incident Reports:** Stored in S3 bucket `unifi-incident-reports-672603477912` organised by date (`incidents/YYYY/MM/DD/`)

- **IAM Roles:**
  - `unifi-incident-lambda-role` — grants Lambda functions access to DynamoDB, Bedrock, S3, SNS, SES
  - `unifi-stepfunctions-role` — allows Step Functions to invoke Lambda functions
  - `unifi-eventbridge-sfn-role` — allows EventBridge to start Step Function executions

- **Cost:** Approximately $1-3/month (mostly Bedrock tokens when anomalies are detected; Lambda, Step Functions, EventBridge, and S3 fall within free tier)

### 4.9 New Device Detection (Dashboard)

The dashboard automatically detects new devices on every page load:
- Maintains a local file (`.known_macs.json`) of all previously seen MAC addresses
- Compares current clients against known MACs on each refresh
- Displays a warning banner at the top of the dashboard when new devices are detected
- Optionally sends SNS alerts if configured

### 4.10 Dark Theme Interface

The dashboard features a modern dark "network operations center" theme:
- Dark gradient background (deep purple/navy)
- Glass-morphism tabs with blur effect
- Neon glow buttons with hover animations
- Vibrant metric cards (indigo, cyan, pink, amber, emerald, blue) with lift-on-hover effect
- Dark sidebar with purple tones
- Rainbow gradient title
- Glass-effect tables and charts
- Mobile-responsive with 3 metrics per row on phones

---

## 5. Application Features

### 5.1 Dashboard Tabs (21 Total)

**Devices Tab**
Displays all UniFi network infrastructure devices with name, model, MAC address, IP address, state, and firmware version.

**Clients Tab**
Shows all connected clients with comprehensive details including name, IP, MAC, connection type, vendor, link speed, TX/RX bandwidth in megabytes, real-time TX/RX rates in KB/s, and connection time. Includes search/filter functionality and a bar chart of the top 10 clients by data usage.

**WiFi Tab**
Dedicated view for wireless clients showing SSID, channel, signal strength, and link speed. Includes a WiFi vs Wired bandwidth comparison chart and signal strength distribution analysis.

**Bandwidth Alerts Tab**
Configurable threshold slider (100 MB to 10 GB) that highlights devices exceeding the bandwidth limit. Displays alert count, detailed table of offending devices, and a bandwidth chart.

**Network Map Tab**
Visual text-based network topology showing the gateway at the top, followed by switches and access points, with all clients grouped by their uplink device. Each device shows name, IP, and MAC address.

**Firmware Tab**
Checks all network devices for available firmware updates. Flags devices with updates available and shows current firmware version and support status.

**Guests Tab**
Separate view for guest network clients with bandwidth stats and the ability to block guest devices directly from the dashboard.

**Device History Tab**
Per-device bandwidth tracking over time. Select any device and a time range to see its TX/RX usage plotted from DynamoDB snapshots.

**Peak Hours Tab**
Network usage analysis by time of day and day of week. Shows average client count by hour, bandwidth by hour, usage by day of week, and identifies peak hours for both client count and bandwidth.

**Parental Controls Tab**
Schedule-based internet access control per device. Create rules specifying block times and days of the week. Includes manual block/unblock buttons and rule management (add/delete). Rules persist in a local JSON file.

**Block/Unblock Tab**
Direct device access control. Select any connected device from a dropdown and block or unblock it via the UniFi classic API's station manager endpoint.

**Speed Test Tab**
Environment-aware speed testing:
- When running locally: Internet speed test using `speedtest-cli` (download, upload, ping, server, ISP) and NAS speed test using `dd` to measure read/write speeds to the mounted NAS share
- When running on ECS: VPN Health Check that tests gateway reachability, API response latency, and runs 5-request latency analysis (min/avg/max) to monitor VPN tunnel health

**Uptime Monitor Tab**
Tracks device online/offline transitions over time. Calculates uptime percentage per device, counts offline events, and identifies the least reliable devices. Includes summary metrics and an uptime bar chart.

**History Tab**
Historical network data from DynamoDB snapshots. Shows client count over time and bandwidth trends with configurable date range (1-30 days). Auto-saves snapshots every 5 minutes.

**AWS Tab**
Manual controls for AWS integrations:
- Push metrics to CloudWatch (client count, wired/wireless split, TX/RX totals)
- Check for new devices and send SNS alerts
- Save network snapshots to DynamoDB
- Displays AWS configuration status

**AI Intelligence Tab (5 Sub-tabs)**
Powered by Amazon Bedrock (Claude Sonnet 4 via EU inference profile):
- Smart Summary — generates a plain English network status overview
- Anomaly Detection — identifies unusual bandwidth patterns, unknown devices, and suspicious activity
- Security Recommendations — provides actionable advice on VLANs, IoT isolation, and best practices
- Device Categorisation — AI categorises each device into IoT, Entertainment, Work, Security, Network Infrastructure, Mobile, or Other with reasoning
- Chat — natural language Q&A interface for asking questions about the network

**Export Tab**
Multiple export options:
- CSV download of all client data
- JSON report with full network summary
- AI-generated comprehensive markdown report
- Email report via Amazon SES with HTML formatting

### 5.2 Additional Features

- **Auto-refresh** — configurable toggle in the sidebar (10-120 second intervals)
- **Multi-site support** — dropdown selector in the sidebar when multiple UniFi sites are detected
- **Mobile responsive** — comprehensive CSS for scrollable tabs, touch-friendly buttons (48px minimum), stacked layouts on small screens, hidden scrollbars, compact metrics, and hidden header/footer on mobile
- **Auto-snapshot** — automatically saves DynamoDB snapshots every 5 minutes when AWS is enabled
- **Local always-on** — macOS Launch Agent for automatic startup and crash recovery
- **API response caching** — 30-second TTL cache on API calls using `@st.cache_data`, significantly improving dashboard responsiveness when switching tabs or interacting with controls
- **Dynamic page title** — browser tab shows live client count (e.g., "25 clients | UniFi Dashboard")
- **Authentication** — built-in login page with username/password, configurable via environment variables, with option to disable when IP restriction is in place
- **IP-restricted access** — ALB security group locked to home public IP only, preventing unauthorised access
- **Automated weekly reports** — Lambda + EventBridge sends AI-generated network reports every Monday at 9am via SES
- **WiFi client support** — full wireless client statistics including SSID, channel, signal strength, with WiFi vs Wired bandwidth comparison

---

## 6. API Integration

### 6.1 UniFi Integration API v1

The primary API used for fetching sites, clients, and devices:
- `GET /proxy/network/integration/v1/sites` — list all sites
- `GET /proxy/network/integration/v1/sites/{site_id}/clients` — list connected clients
- `GET /proxy/network/integration/v1/sites/{site_id}/devices` — list network devices

Authentication is via the `X-API-KEY` header.

### 6.2 UniFi Classic API

The classic API provides detailed per-client statistics not available in the integration API:
- `GET /proxy/network/api/s/default/stat/sta` — detailed client statistics including `wired-tx_bytes`, `wired-rx_bytes`, real-time rates, signal strength, SSID, channel, uptime, and vendor information
- `POST /proxy/network/api/s/default/cmd/stamgr` — device management commands (block/unblock)

The classic API was essential because the integration API v1 does not include bandwidth data per client.

---

## 7. Development Journey

### 7.1 Environment Setup

The project began with Python 3.9 on macOS, which triggered boto3 deprecation warnings. Python was upgraded to 3.14 via Homebrew, and a virtual environment was created to manage dependencies. The `python-dotenv` library was used for environment variable management, keeping sensitive data like the UniFi API key out of source code.

### 7.2 Initial Development

The dashboard started as a simple Streamlit app fetching data from the UniFi integration API. Early testing revealed that the integration API didn't include TX/RX bandwidth data, leading to the addition of the classic API endpoint which provided comprehensive per-client statistics.

### 7.3 AWS Integration

AWS services were added incrementally:
1. CloudWatch custom metrics for network monitoring
2. DynamoDB for historical snapshot storage
3. SNS for new device alerts
4. Amazon Bedrock for AI-powered network intelligence
5. SES for automated email reports

### 7.4 Containerisation

The application was containerised using Docker with a `python:3.12-slim` base image. A `.dockerignore` file excludes virtual environments, IDE files, private keys, and git history. The Streamlit configuration file is copied into the container for headless operation.

### 7.5 First Deployment Attempt — AWS App Runner

The initial cloud deployment used AWS App Runner for its simplicity. However, this approach failed because:
- App Runner does not support WebSocket connections, which Streamlit requires for its interactive features
- The dashboard loaded but displayed a blank page because the JavaScript frontend couldn't establish WebSocket connections to the backend
- A VPC connector was added to enable connectivity to the home network, but the WebSocket issue remained

App Runner was abandoned in favour of ECS Fargate.

### 7.6 Successful Deployment — ECS Fargate

ECS Fargate with an Application Load Balancer resolved all issues:
- The ALB properly handles WebSocket upgrade requests
- Sticky sessions ensure consistent routing for Streamlit sessions
- The Fargate tasks run inside the VPC with direct access to the VPN tunnel
- The deployment supports rolling updates with zero downtime

---

## 8. Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| Boto3 Python 3.9 deprecation warning | Upgraded to Python 3.14 via Homebrew |
| Homebrew PEP 668 blocking pip installs | Used Python virtual environments |
| UniFi integration API missing bandwidth data | Added classic API endpoint for detailed stats |
| App Runner blank page | Switched to ECS Fargate + ALB (WebSocket support) |
| DNS resolution failures for App Runner URL | Changed Mac DNS to Google (8.8.8.8), added /etc/hosts entry |
| ECR push 403 Forbidden | Re-authenticated with `aws ecr get-login-password` |
| ECR repository not found | Recreated repository after accidental deletion during cleanup |
| DynamoDB NoCredentialsError in ECS | Created dedicated task role with proper IAM permissions |
| Bedrock legacy model error | Switched to EU inference profile for Claude Sonnet 4 |
| Bedrock on-demand throughput not supported | Used inference profile ID instead of model ID |
| ALB connection timeout | Added port 80 inbound rule to security group |
| ALB listener missing after redeployment | Recreated HTTP listener on port 80 |
| SSM patch baseline lock conflict | Waited for previous patching operation to complete |
| NAS speed test sudo purge timeout | Removed sudo purge from automated test, added delay instead |
| Task definition API key placeholder | Updated environment variable and redeployed |
| Apple devices showing unknown vendor | Identified as Private Wi-Fi Address (randomised MAC) feature |
| Streamlit inline if/else dumping DeltaGenerator | Replaced with proper if/else blocks |
| Speed test on ECS testing AWS bandwidth not home | Added environment detection, shows VPN health check on ECS instead |
| Lambda in VPC cannot reach DynamoDB/Bedrock/SES | Removed Lambda from VPC, reads DynamoDB snapshots instead of calling UniFi API directly |
| Lambda `AWS_REGION` reserved environment variable | Renamed to `BEDROCK_REGION` |
| Lambda missing `requests` module | Rewrote Lambda to use only boto3 (built-in), eliminating external dependencies |
| ALB listener repeatedly disappearing | Identified cause as service recreation; switched to `--force-new-deployment` only |
| ECS task missing SES permissions | Added `AmazonSESFullAccess` to task role |
| DynamoDB scan filter not returning results | Replaced DynamoDB FilterExpression with Python-side filtering to handle timezone format mismatches |
| API key visible in sidebar | Hidden when loaded from environment variable, only shows input field as fallback |
| Step Functions incident alerts repeating every 15 min | Added DynamoDB `unifi-alerted-incidents` table with 24-hour TTL for de-duplication |
| Lambda `AWS_REGION` reserved variable | Renamed to `BEDROCK_REGION` for Lambda environment variables |
| NAS IP changing after router swap | Set static IP reservation in UniFi controller DHCP settings |
| Mac trying to connect to old Deco IP (192.168.2.31) | Cleared `com.apple.NetAuthAgent` cache and restarted Finder |
| AWS credentials exposed in chat | Rotated access keys immediately, session tokens auto-expired |

---

## 9. EC2 Patch Management

As part of the broader infrastructure management, AWS Systems Manager was used to patch two EC2 instances:

**Linux Instance (i-06a5a216414589c14):**
- Amazon Linux 2023 running in eu-west-1
- Scan completed successfully identifying installed packages
- Patch install completed successfully after resolving a lock conflict with a concurrent scan operation

**Windows Instance (i-0831679412502f831):**
- Windows Server running in eu-west-1
- Scan identified 1 missing patch: KB5078740
- Patch install completed successfully with automatic reboot

Both instances were patched using the `AWS-RunPatchBaseline` SSM document with the default patch baselines.

---

## 10. NAS Performance Testing

The Ugreen HomeCloud NAS at 192.168.1.186 was benchmarked using `dd` for sequential read/write performance:

| Test | Speed |
|------|-------|
| Write | 288 MB/s (2,304 Mbps) |
| Read | 285 MB/s (2,280 Mbps) |

These results are near the theoretical maximum for a 2.5GbE connection (312 MB/s theoretical, ~280-300 MB/s real-world). The NAS is connected via SMB protocol. Initial ping tests showed 40% packet loss which was attributed to the NAS waking from sleep mode — subsequent tests showed 0% packet loss with ~1.3ms average latency.

---

## 11. Configuration Files

### 11.1 Environment Variables (.env)
```
UNIFI_API_KEY=<redacted>
ENABLE_AWS=true
AWS_REGION=eu-west-1
SNS_TOPIC_ARN=
DYNAMODB_TABLE=unifi-network-snapshots
BEDROCK_MODEL_ID=eu.anthropic.claude-sonnet-4-20250514-v1:0
BANDWIDTH_THRESHOLD_MB=1000
SES_SENDER=admin@bodeconsulting.com
SES_RECIPIENT=bode@bodeconsulting.com
SES_REGION=us-east-1
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=<redacted>
DISABLE_AUTH=true
```

### 11.2 Dockerfile
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements-dashboard.txt .
RUN pip install --no-cache-dir -r requirements-dashboard.txt
COPY unifi_dashboard.py .
COPY .streamlit/config.toml /app/.streamlit/config.toml
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1
ENTRYPOINT ["streamlit", "run", "unifi_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

### 11.3 Dependencies (requirements-dashboard.txt)
```
streamlit
requests
pandas
urllib3
boto3
python-dotenv
speedtest-cli
```

---

## 12. Access Points

| Access Method | URL | Notes |
|--------------|-----|-------|
| Local (Mac Mini) | http://192.168.1.187:8501 | Direct, no auth required |
| Local Network | http://192.168.1.187:8501 | Any device on home WiFi |
| AWS (IP-restricted) | http://unifi-dashboard-alb-598094223.eu-west-1.elb.amazonaws.com | Restricted to home public IP only |

---

## 13. Cost Estimate

| Resource | Monthly Cost |
|----------|-------------|
| ECS Fargate (0.5 vCPU, 1GB RAM, 24/7) | ~$18 |
| Application Load Balancer | ~$18 |
| DynamoDB (on-demand, snapshots + incidents) | ~$1-2 |
| ECR (image storage) | ~$0.10 |
| CloudWatch Logs | ~$0.50 |
| Lambda - Weekly Report (4/month) | Free tier |
| Lambda - Incident Response (1/day) | Free tier |
| Step Functions (1 execution/day) | Free tier |
| EventBridge (2 events/day) | Free tier |
| S3 (incident reports) | ~$0.01 |
| SES (alerts + reports) | Free tier |
| SNS (alerts) | Free tier |
| Bedrock (AI features + reports + incidents) | ~$2-5 |
| **Total** | **~$40-44/month** |

---

## 14. Future Improvements

The following enhancements are recommended for future iterations:

- **HTTPS** — ACM certificate with HTTPS listener on the ALB
- **WAF** — AWS WAF on the ALB for additional security
- **Custom Domain** — Route 53 DNS with a friendly domain name
- **CI/CD Pipeline** — GitHub Actions or CodePipeline for automated deployments
- **Fargate Spot** — Reduce compute costs by approximately 70%
- **CloudWatch Alarms** — Automated alerts for network anomalies
- **Slack Integration** — Send notifications to a Slack channel
- **DNS Query Logging** — Monitor what domains devices are accessing

---

## 15. Conclusion

This project demonstrates a complete end-to-end solution for network monitoring, combining local network APIs with cloud services and AI. The dashboard evolved from a simple local Streamlit app into a fully-featured, cloud-deployed monitoring platform with 21 interactive tabs, AI-powered intelligence, historical analytics, device management capabilities, and automated weekly reporting. The use of AWS ECS Fargate with an ALB provides reliable hosting with WebSocket support, while the Site-to-Site VPN enables secure connectivity between the cloud deployment and the home network. Security is enforced through IP-restricted ALB access and optional password authentication. The serverless Lambda + EventBridge pipeline delivers AI-generated network reports every Monday morning without any manual intervention. The addition of AWS Step Functions provides an automated incident response system that continuously monitors the network every 15 minutes, detects anomalies using AI, and alerts only when genuine threats are identified — with built-in de-duplication to prevent alert fatigue. The project integrates 14 AWS services in total: ECS Fargate, ALB, ECR, DynamoDB, CloudWatch, SNS, SES, Lambda, EventBridge, Step Functions, S3, Bedrock, IAM, and Site-to-Site VPN.
