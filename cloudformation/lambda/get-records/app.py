import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["RECORDS_TABLE"]
INDEX_NAME = os.environ["USER_INDEX_NAME"]

table = dynamodb.Table(TABLE_NAME)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def lambda_handler(event, context):
    claims = event["requestContext"]["authorizer"]["claims"]
    user_id = claims["sub"]

    response = table.query(
        IndexName=INDEX_NAME,
        KeyConditionExpression=Key("user_id").eq(user_id),
        ScanIndexForward=False
    )

    records = response.get("Items", [])

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "user_id": user_id,
            "count": len(records),
            "records": records
        }, cls=DecimalEncoder)
    }
