"""Step 1: Scan network - read latest snapshot from DynamoDB."""
import json
import os
import boto3

DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "unifi-network-snapshots")
KNOWN_DEVICES_TABLE = os.environ.get("KNOWN_DEVICES_TABLE", "unifi-known-devices")
DYNAMODB_REGION = os.environ.get("DYNAMODB_REGION", "eu-west-1")


def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb", region_name=DYNAMODB_REGION)

    # Get latest snapshot
    table = dynamodb.Table(DYNAMODB_TABLE)
    resp = table.scan()
    items = resp.get("Items", [])
    if not items:
        return {"status": "no_data", "clients": [], "known_macs": []}

    latest = max(items, key=lambda x: x.get("timestamp", ""))
    clients = json.loads(latest.get("clients", "[]"))

    # Get known devices
    known_macs = []
    try:
        known_table = dynamodb.Table(KNOWN_DEVICES_TABLE)
        known_resp = known_table.scan()
        known_macs = [item["mac"] for item in known_resp.get("Items", [])]
    except Exception:
        pass

    return {
        "status": "ok",
        "timestamp": latest.get("timestamp", ""),
        "client_count": len(clients),
        "clients": clients,
        "known_macs": known_macs,
    }
