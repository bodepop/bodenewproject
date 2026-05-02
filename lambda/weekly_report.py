import json
import os
import boto3
from datetime import datetime, timezone

BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "eu.anthropic.claude-sonnet-4-20250514-v1:0")
SES_SENDER = os.environ.get("SES_SENDER", "")
SES_RECIPIENT = os.environ.get("SES_RECIPIENT", "")
SES_REGION = os.environ.get("SES_REGION", "us-east-1")
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "eu-west-1")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "unifi-network-snapshots")
DYNAMODB_REGION = os.environ.get("DYNAMODB_REGION", "eu-west-1")


def get_latest_snapshot():
    """Get the most recent network snapshot from DynamoDB."""
    dynamodb = boto3.resource("dynamodb", region_name=DYNAMODB_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE)
    resp = table.scan()
    items = resp.get("Items", [])
    while "LastEvaluatedKey" in resp:
        resp = table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))

    if not items:
        return None

    # Get the most recent snapshot
    latest = max(items, key=lambda x: x.get("timestamp", ""))
    return latest


def build_context_from_snapshot(snapshot):
    """Build network context from a DynamoDB snapshot."""
    clients = json.loads(snapshot.get("clients", "[]"))
    client_count = int(snapshot.get("client_count", 0))
    total_tx = int(snapshot.get("total_tx_mb", 0))
    total_rx = int(snapshot.get("total_rx_mb", 0))
    timestamp = snapshot.get("timestamp", "Unknown")

    client_lines = "\n".join(
        f"  - {c.get('name', 'Unknown')} | IP: {c.get('ip', 'N/A')} | TX: {c.get('tx_mb', 0)}MB | RX: {c.get('rx_mb', 0)}MB"
        for c in clients
    )

    # Top consumers
    top = sorted(clients, key=lambda x: x.get("rx_mb", 0), reverse=True)[:10]
    top_lines = "\n".join(
        f"  - {c.get('name', 'Unknown')} | TX: {c.get('tx_mb', 0)}MB | RX: {c.get('rx_mb', 0)}MB"
        for c in top
    )

    return f"""Weekly Network Report Data (snapshot from {timestamp}):

SUMMARY:
- Total clients: {client_count}
- Total TX: {total_tx} MB
- Total RX: {total_rx} MB

TOP 10 BANDWIDTH CONSUMERS:
{top_lines}

ALL CLIENTS:
{client_lines}"""


def lambda_handler(event, context):
    print("Starting weekly report generation...")

    snapshot = get_latest_snapshot()
    if not snapshot:
        print("No snapshots found in DynamoDB")
        return {"statusCode": 500, "body": "No network data available"}

    network_ctx = build_context_from_snapshot(snapshot)

    # Generate report with Bedrock
    bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "system": "Generate a comprehensive weekly network report with: Executive Summary, "
                  "Device Inventory, Bandwidth Analysis (top consumers), Security Assessment, "
                  "and Recommendations. Format in clean HTML suitable for email with inline CSS. "
                  "Use tables where appropriate. Make it professional and visually clean.",
        "messages": [{"role": "user", "content": f"{network_ctx}\n\nGenerate the weekly report."}],
    })

    print("Calling Bedrock...")
    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID, body=body,
        contentType="application/json", accept="application/json"
    )
    report_html = json.loads(response["body"].read())["content"][0]["text"]
    print("Report generated")

    # Send via SES
    ses = boto3.client("ses", region_name=SES_REGION)
    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [SES_RECIPIENT]},
        Message={
            "Subject": {"Data": f"UniFi Weekly Network Report — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"},
            "Body": {"Html": {"Data": report_html}},
        },
    )

    print(f"Report sent to {SES_RECIPIENT}")
    return {"statusCode": 200, "body": "Report sent"}
