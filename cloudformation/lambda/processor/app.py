import json
import os
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["RECORDS_TABLE"]

table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    for record in event["Records"]:
        message_body = json.loads(record["body"])

        for s3_record in message_body["Records"]:
            s3_key = s3_record["s3"]["object"]["key"]
            image_id = s3_key.replace("uploads/", "").replace(".jpg", "")
            processed_at = datetime.now(timezone.utc).isoformat()

            table.update_item(
                Key={
                    "image_id": image_id
                },
                UpdateExpression="SET #status = :status, processed_at = :processed_at",
                ExpressionAttributeNames={
                    "#status": "status"
                },
                ExpressionAttributeValues={
                    ":status": "UPLOADED",
                    ":processed_at": processed_at
                }
            )

    return {
        "statusCode": 200,
        "body": json.dumps("Processed S3 upload event")
    }
