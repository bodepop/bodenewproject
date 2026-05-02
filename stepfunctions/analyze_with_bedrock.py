"""Step 3: Analyze anomalies with Bedrock AI."""
import json
import os
import boto3

BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "eu.anthropic.claude-sonnet-4-20250514-v1:0")
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "eu-west-1")


def lambda_handler(event, context):
    anomalies = event.get("anomalies", [])
    clients = event.get("clients", [])

    # Build context
    anomaly_text = "\n".join(
        f"  - [{a['severity']}] {a['detail']}" for a in anomalies
    )
    client_text = "\n".join(
        f"  - {c.get('name', 'Unknown')} | IP: {c.get('ip', 'N/A')} | TX: {c.get('tx_mb', 0)}MB | RX: {c.get('rx_mb', 0)}MB"
        for c in clients[:20]
    )

    prompt = f"""Network Incident Analysis:

ANOMALIES DETECTED ({len(anomalies)}):
{anomaly_text}

CURRENT CLIENTS ({len(clients)}):
{client_text}

Provide:
1. Risk assessment (Critical/High/Medium/Low)
2. For each anomaly: Is it a real threat or false positive? Why?
3. Recommended immediate actions
4. Long-term recommendations

Be concise and actionable."""

    bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "system": "You are a network security incident responder. Analyze anomalies and provide actionable recommendations.",
        "messages": [{"role": "user", "content": prompt}],
    })

    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID, body=body,
        contentType="application/json", accept="application/json"
    )
    analysis = json.loads(response["body"].read())["content"][0]["text"]

    return {
        "analysis": analysis,
        "anomalies": anomalies,
        "max_severity": event.get("max_severity", "LOW"),
        "anomaly_count": len(anomalies),
        "timestamp": event.get("timestamp", ""),
    }
