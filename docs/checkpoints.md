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

# Checkpoint 2

## Architecture

User

→ API Gateway

→ Lambda (secure-upload-pipeline-get-upload-url)

├── Generate pre-signed URL

├── Write DynamoDB record

└── Return upload URL

→ User uploads directly to S3

## Resources Created

### DynamoDB

Table:

secure-upload-pipeline-records

Partition Key:

image_id

Billing Mode:

On-Demand

## Lambda Enhancements

Added DynamoDB integration.

Lambda now:

* Generates image_id
* Generates pre-signed URL
* Creates DynamoDB record
* Returns upload URL

## Validation Performed

Verified:

* DynamoDB record created successfully
* Upload URL generated successfully
* File uploaded successfully to S3
* Object appears in uploads/ prefix
* Record appears in DynamoDB

## Lessons Learned

* S3 stores files, not application metadata.
* DynamoDB stores upload metadata.
* image_id is a better primary key than file_name.
* One user can have many uploads, so user_id alone is not a good partition key.
* Metadata and file storage are commonly separated in cloud architectures.

# Checkpoint 3

## Architecture

S3 upload

→ SQS queue

→ Processor Lambda

→ DynamoDB status update

## Resources Created

### SQS

Main queue:

secure-upload-pipeline-queue

Dead-letter queue:

secure-upload-pipeline-dlq

Redrive policy:

- Max receives: 3
- Failed messages move to DLQ

### Lambda

Processor function:

secure-upload-pipeline-processor

Responsibilities:

- Read SQS messages
- Parse S3 upload event
- Extract image_id from S3 object key
- Update DynamoDB record status to UPLOADED

### S3 Event Notification

Bucket:

secure-upload-pipeline-uploads-654375431894-us-east-1-an

Event:

- Object created
- Prefix: uploads/
- Suffix: .jpg

Destination:

secure-upload-pipeline-queue

## Validation Performed

Verified:

- File uploaded to S3
- S3 sent event to SQS
- SQS triggered processor Lambda
- Processor Lambda updated DynamoDB
- Record status changed to UPLOADED

## Lessons Learned

- SQS buffers events between S3 and Lambda.
- Queues protect systems from broken or slow processors.
- A DLQ is just another queue used for failed messages.
- The receiving service controls access with a resource policy.
- SQS queue policy allowed S3 events to be accepted.

## Template Validation

Created and deployed a test rebuild template:

cloudformation/checkpoint-templates/checkpoint-3-test.yaml

Test stack:

secure-upload-pipeline-test

Validated:

- SAM build succeeded
- CloudFormation stack deployed successfully
- API Gateway output URL was created
- Lambda initially failed due to hardcoded DynamoDB table name
- Fixed Lambda code to use environment variable RECORDS_TABLE
- Redeployed from GitHub/SAM
- API returned upload URL successfully

Important lesson:

The template can deploy successfully even if the application code still has a runtime error. Deployment success does not always mean application success.

Rebuild status:

Checkpoint 3 can now be rebuilt from GitHub using SAM/CloudFormation.
