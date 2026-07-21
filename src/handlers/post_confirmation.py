import boto3
import json

def lambda_handler(event, context):
    events = boto3.client("events")

    events.put_events(
        Entries=[
            {
                "Source": "learnhub.identity",
                "DetailType": "UserConfirmed",
                "EventBusName": "learnhub",
                "Details": json.dumps({
                    
                })
            }
        ]
    )
