import json
import uuid
import os
from datetime import datetime, timezone

import boto3

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

BUCKET_NAME = os.environ["UPLOAD_BUCKET"]
TABLE_NAME = os.environ["RECORDS_TABLE"]

table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    image_id = str(uuid.uuid4())
    key = f"uploads/{image_id}.jpg"
    created_at = datetime.now(timezone.utc).isoformat()

    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": key,
            "ContentType": "image/jpeg"
        },
        ExpiresIn=300
    )

    table.put_item(
        Item={
            "image_id": image_id,
            "s3_key": key,
            "status": "UPLOAD_URL_CREATED",
            "created_at": created_at
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "image_id": image_id,
            "key": key,
            "upload_url": upload_url
        })
    }
