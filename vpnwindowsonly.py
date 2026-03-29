import json 

def lambda_handler(event, context): 

    if event["platform"] == "win": 

        return { 

            "allow": True, 

            "error-msg-on-failed-posture-compliance": "Your device is compliant", 

            "posture-compliance-statuses": ["Compliant"], 

            "schema-version": "v1"         

        } 

    return { 

        "allow": False, 

        "error-msg-on-failed-posture-compliance": "Your device is not compliant", 

        "posture-compliance-statuses": ["QUARANTINED"], 

        "schema-version": "v1"         

    } 