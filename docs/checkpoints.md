# Checkpoint 1

## Architecture

User

→ API Gateway

→ Lambda (secure-upload-pipeline-get-upload-url)

→ S3 Private Upload Bucket

## Resources Created

### S3

Bucket:

secure-upload-pipeline-uploads-654375431894-us-east-1-an

Security:

* Block Public Access enabled
* Private bucket

### Lambda

Function:

secure-upload-pipeline-get-upload-url

Responsibilities:

* Generate image_id
* Generate S3 object key
* Generate pre-signed upload URL
* Return upload URL to caller

### IAM

Lambda execution role granted:

* s3:PutObject

Scope:

uploads/*

Principle:

Least Privilege

### API Gateway

API:

secure-upload-pipeline-api

Endpoint:

POST /upload-url

Integration:

API Gateway → Lambda

## Validation Performed

Verified:

* API Gateway invokes Lambda
* Lambda generates pre-signed URL
* Upload URL returned successfully
* File uploaded successfully to S3
* uploads/ prefix created automatically

## Lessons Learned

* S3 does not use real folders.
* uploads/ is an object key prefix.
* Lambda generates the pre-signed URL.
* The pre-signed URL uses Lambda role permissions.
* Users upload directly to S3.
* API Gateway provides the public endpoint for Lambda.
