import json
import os
from datetime import datetime, timezone
from urllib.parse import unquote_plus

import boto3

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["RECORDS_TABLE"]

table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    for record in event["Records"]:
        message_body = json.loads(record["body"])

        for s3_record in message_body["Records"]:
            s3_key = unquote_plus(s3_record["s3"]["object"]["key"])

            # Expected key format:
            # uploads/{user_id}/{image_id}.jpg
            key_parts = s3_key.split("/")

            if len(key_parts) < 3:
                print(f"Unexpected S3 key format: {s3_key}")
                continue

            user_id = key_parts[1]
            filename = key_parts[2]
            image_id = filename.replace(".jpg", "")

            processed_at = datetime.now(timezone.utc).isoformat()

            table.update_item(
                Key={
                    "image_id": image_id
                },
                UpdateExpression="""
                    SET #status = :status,
                        processed_at = :processed_at,
                        processor_user_id = :user_id
                """,
                ExpressionAttributeNames={
                    "#status": "status"
                },
                ExpressionAttributeValues={
                    ":status": "UPLOADED",
                    ":processed_at": processed_at,
                    ":user_id": user_id
                }
            )

            print(f"Updated image_id={image_id}, user_id={user_id}, key={s3_key}")

    return {
        "statusCode": 200,
        "body": json.dumps("Processed S3 upload event")
    }
