# Setup Guide

This guide explains how to set up the project environment, install dependencies, configure AWS credentials, and deploy or run the system locally.

---

# 1. Prerequisites

Before starting, ensure you have the following installed on your machine:

## **Required Tools**

* **Terraform ≥ 1.5**
* **Python ≥ 3.11**
* **pip** (Python package manager)
* **AWS CLI v2**
* **Git**
* **Docker** (optional for LocalStack or local testing)

---

# 2. Clone the Repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

---

# 3. Configure AWS Credentials

You need valid AWS IAM credentials with permissions for Lambda, SQS, IAM, DynamoDB, CloudWatch, and API Gateway.

## **Option A – Configure via AWS CLI**

```bash
aws configure
```

This will prompt:

* AWS Access Key
* AWS Secret Key
* Region (default: `us-east-1`)
* Output format (json)

## **Option B – Environment Variables**

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

---

# 4. Install Python Dependencies (for Lambdas)

If your Lambda functions require packages, install them inside their folders.

### Example (Producer Lambda):

```bash
cd lambda/producer
pip install -r requirements.txt -t .
cd ../..
```

### Example (Consumer Lambda):

```bash
cd lambda/consumer
pip install -r requirements.txt -t .
cd ../..
```

After installing dependencies, zip the functions:

```bash
cd lambda/producer
zip -r producer.zip .
cd ../../lambda/consumer
zip -r consumer.zip .
cd ../..
```

---

# 5. Terraform Setup

Initialize Terraform modules and providers.

```bash
terraform init
```

Plan changes:

```bash
terraform plan
```

Apply to deploy resources:

```bash
terraform apply -auto-approve
```

This creates:

* SQS Queue + DLQ
* DynamoDB table
* IAM roles
* Lambda functions
* API Gateway REST API
* CloudWatch log groups

---

# 6. Test the API After Deployment

Get the API Gateway endpoint from Terraform outputs or AWS Console.

Send a test request:

```bash
curl -sS -X POST 'https://yorledc60d.execute-api.us-east-1.amazonaws.com/producer' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Atomic Habits",
    "author": "James Clear"
  }'
```

Expected flow:

1. API Gateway triggers Producer Lambda
2. Producer sends message to SQS
3. Consumer Lambda processes SQS message
4. DynamoDB stores the record

---

# 7. Cleanup

To delete AWS resources created by Terraform:

```bash
terraform destroy -auto-approve
```

---

# Summary

This setup guide ensures you can:

* Prepare your environment
* Configure AWS credentials
* Build Lambdas
* Deploy all AWS resources with Terraform
* Run and test the entire event-driven pipeline
* Build and deploy documentation
