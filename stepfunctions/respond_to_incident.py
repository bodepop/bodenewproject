"""Step 4: Respond - save to S3, send alerts based on severity."""
import json
import os
import boto3
from datetime import datetime, timezone

S3_BUCKET = os.environ.get("S3_BUCKET", "unifi-incident-reports")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
SES_SENDER = os.environ.get("SES_SENDER", "")
SES_RECIPIENT = os.environ.get("SES_RECIPIENT", "")
SES_REGION = os.environ.get("SES_REGION", "us-east-1")
S3_REGION = os.environ.get("S3_REGION", "eu-west-1")


def lambda_handler(event, context):
    analysis = event.get("analysis", "")
    anomalies = event.get("anomalies", [])
    severity = event.get("max_severity", "LOW")
    timestamp = event.get("timestamp", datetime.now(timezone.utc).isoformat())
    actions_taken = []

    now = datetime.now(timezone.utc)

    # Save incident report to S3
    try:
        s3 = boto3.client("s3", region_name=S3_REGION)
        report = {
            "timestamp": timestamp,
            "generated_at": now.isoformat(),
            "severity": severity,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "ai_analysis": analysis,
        }
        key = f"incidents/{now.strftime('%Y/%m/%d')}/{now.strftime('%H%M%S')}-{severity}.json"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(report, indent=2),
            ContentType="application/json",
        )
        actions_taken.append(f"Report saved to S3: {key}")
    except Exception as e:
        actions_taken.append(f"S3 save failed: {e}")

    # Send SNS alert for HIGH severity
    if severity == "HIGH" and SNS_TOPIC_ARN:
        try:
            sns = boto3.client("sns", region_name=S3_REGION)
            message = f"🚨 NETWORK INCIDENT - {severity}\n\n"
            message += f"Anomalies: {len(anomalies)}\n\n"
            for a in anomalies:
                message += f"  [{a['severity']}] {a['detail']}\n"
            message += f"\nAI Analysis:\n{analysis[:500]}"

            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"UniFi Alert: {severity} - {len(anomalies)} anomalies detected",
                Message=message,
            )
            actions_taken.append("SNS alert sent")
        except Exception as e:
            actions_taken.append(f"SNS failed: {e}")

    # Send email for HIGH and MEDIUM severity
    if severity in ("HIGH", "MEDIUM") and SES_SENDER and SES_RECIPIENT:
        try:
            ses = boto3.client("ses", region_name=SES_REGION)
            html = f"""<h2>🚨 Network Incident Report - {severity}</h2>
            <p><strong>Time:</strong> {timestamp}</p>
            <p><strong>Anomalies:</strong> {len(anomalies)}</p>
            <h3>Anomalies:</h3><ul>"""
            for a in anomalies:
                html += f"<li><strong>[{a['severity']}]</strong> {a['detail']}</li>"
            html += f"</ul><h3>AI Analysis:</h3><pre>{analysis}</pre>"

            ses.send_email(
                Source=SES_SENDER,
                Destination={"ToAddresses": [SES_RECIPIENT]},
                Message={
                    "Subject": {"Data": f"UniFi Incident: {severity} - {now.strftime('%Y-%m-%d %H:%M')}"},
                    "Body": {"Html": {"Data": html}},
                },
            )
            actions_taken.append("Email sent")
        except Exception as e:
            actions_taken.append(f"SES failed: {e}")

    return {
        "status": "responded",
        "severity": severity,
        "anomaly_count": len(anomalies),
        "actions_taken": actions_taken,
    }
