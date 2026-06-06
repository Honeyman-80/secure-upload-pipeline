import json
import os
import uuid
from datetime import datetime, timezone

import boto3

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

BUCKET_NAME = os.environ["UPLOAD_BUCKET"]
TABLE_NAME = os.environ["RECORDS_TABLE"]

table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    claims = event["requestContext"]["authorizer"]["claims"]
    user_id = claims["sub"]
    user_email = claims.get("email", "")

    image_id = str(uuid.uuid4())
    key = f"uploads/{user_id}/{image_id}.jpg"
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
            "user_id": user_id,
            "user_email": user_email,
            "s3_key": key,
            "status": "UPLOAD_URL_CREATED",
            "created_at": created_at
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "image_id": image_id,
            "user_id": user_id,
            "key": key,
            "upload_url": upload_url
        })
    }
