"""Step 2: Detect anomalies - compare current vs known devices, check bandwidth."""
import json
import os
import boto3

BANDWIDTH_THRESHOLD_MB = int(os.environ.get("BANDWIDTH_THRESHOLD_MB", "5000"))
DYNAMODB_REGION = os.environ.get("DYNAMODB_REGION", "eu-west-1")
ALERTED_TABLE = os.environ.get("ALERTED_TABLE", "unifi-alerted-incidents")


def lambda_handler(event, context):
    clients = event.get("clients", [])
    known_macs = [m.lower() for m in event.get("known_macs", [])]
    anomalies = []

    # Load already-alerted incidents (to avoid repeat alerts)
    alerted = set()
    try:
        dynamodb = boto3.resource("dynamodb", region_name=DYNAMODB_REGION)
        table = dynamodb.Table(ALERTED_TABLE)
        resp = table.scan()
        for item in resp.get("Items", []):
            alerted.add(item["incident_key"])
    except Exception:
        pass

    for client in clients:
        mac = client.get("mac", "").lower()
        name = client.get("name", "Unknown")
        tx = client.get("tx_mb", 0)
        rx = client.get("rx_mb", 0)
        total_mb = tx + rx

        # Check 1: Unknown device
        if mac and known_macs and mac not in known_macs:
            incident_key = f"new_device_{mac}"
            if incident_key not in alerted:
                anomalies.append({
                    "type": "new_device",
                    "severity": "HIGH",
                    "device": name,
                    "mac": mac,
                    "ip": client.get("ip", "N/A"),
                    "detail": f"Unknown device '{name}' detected (MAC: {mac})",
                    "incident_key": incident_key,
                })

        # Check 2: Excessive bandwidth
        if total_mb > BANDWIDTH_THRESHOLD_MB:
            incident_key = f"high_bw_{mac}"
            if incident_key not in alerted:
                anomalies.append({
                    "type": "high_bandwidth",
                    "severity": "MEDIUM",
                    "device": name,
                    "mac": mac,
                    "ip": client.get("ip", "N/A"),
                    "detail": f"'{name}' using {total_mb:.0f} MB (threshold: {BANDWIDTH_THRESHOLD_MB} MB)",
                    "tx_mb": tx,
                    "rx_mb": rx,
                    "incident_key": incident_key,
                })

    # Save new incidents as alerted
    if anomalies:
        try:
            dynamodb = boto3.resource("dynamodb", region_name=DYNAMODB_REGION)
            table = dynamodb.Table(ALERTED_TABLE)
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).isoformat()
            for a in anomalies:
                table.put_item(Item={
                    "incident_key": a["incident_key"],
                    "type": a["type"],
                    "device": a["device"],
                    "alerted_at": now,
                    "ttl": int(datetime.now(timezone.utc).timestamp()) + 86400,  # Expire after 24h
                })
        except Exception:
            pass

    has_anomalies = len(anomalies) > 0
    max_severity = "LOW"
    if any(a["severity"] == "HIGH" for a in anomalies):
        max_severity = "HIGH"
    elif any(a["severity"] == "MEDIUM" for a in anomalies):
        max_severity = "MEDIUM"

    return {
        "has_anomalies": has_anomalies,
        "anomaly_count": len(anomalies),
        "max_severity": max_severity,
        "anomalies": anomalies,
        "client_count": len(clients),
        "clients": clients,
        "timestamp": event.get("timestamp", ""),
    }
