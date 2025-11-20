# [Specialization] Cloud Platform Engineer – Final Project

## Project: Library Book Request System (Serverless Architecture)

**Brief Description**

This project deploys a fully serverless application on AWS that allows users to request books to be added to a digital library catalog. Requests are received through a REST API (API Gateway → Producer Lambda), validated, and sent to an SQS queue. A Consumer Lambda processes each message, retrieves additional book data from a public API, and stores the final record in DynamoDB for librarian review.

**Author / Owner:** Isaac

---

# Objectives

* Design and deploy the entire AWS infrastructure using **Terraform**.
* Implement two Lambda functions (Producer and Consumer) using **Python**.
* Integrate **API Gateway**, **SQS** (with DLQ), **DynamoDB**, **CloudWatch**, and **IAM**.
* Implement CI/CD using **Jenkins** and/or **GitHub Actions**.
* Follow best practices for cloud security, branching strategy, and GitHub workflow (Issues, Projects, PRs).

---

# Architecture Diagram (ASCII Overview)

```
Client (curl / frontend) --> API Gateway (POST /requests)
                                   |
                                   v
                      Producer Lambda (validate + push to SQS)
                                   |
                               SQS Queue
                                   |
                           Consumer Lambda (trigger)
                                   |
               GET book info from public API (e.g., OpenLibrary)
                                   |
                              DynamoDB Table
                                   |
                             CloudWatch Logs
```

---

# Components and Responsibilities

## Producer Lambda

* REST endpoint via API Gateway to receive JSON input: `title`, `author`.
* Validates required fields, normalizes payload structure.
* Sends enriched message to SQS with metadata and a generated `request_id`.
* Returns `202 Accepted` with a tracking `request_id`.

**Example input payload (JSON)**

```json
curl -sS -X POST 'https://yorledc60d.execute-api.us-east-1.amazonaws.com/producer' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Atomic Habits",
    "author": "James Clear"
  }'
```

## Consumer Lambda

* Triggered automatically by SQS events.
* Fetches additional book metadata using a public API (OpenLibrary, Google Books Free API, etc.).
* Enriches the record with fields such as: ISBN, publisher, publish_date, cover_url.
* Stores the enriched item in **DynamoDB** using `request_id` as the primary key.
* Confirms message deletion from SQS upon successful processing.

## SQS + DLQ

* SQS Standard Queue.
* Dead-letter queue (DLQ) enabled.
* `maxReceiveCount = 5` before message is redirected to DLQ.

## DynamoDB

* Table name: `books-table`.
* Primary Key: `request_id` (String).
* Suggested attributes: `title`, `author`, `isbn`, `publisher`, `published_date`, `status`, `enriched_at`.

## IAM

* `producer_role`: permissions for `sqs:SendMessage` and CloudWatch logging.
* `consumer_role`: permissions for `dynamodb:PutItem`, SQS visibility actions, and CloudWatch logs.
* Follows principle of least privilege.

## CloudWatch

* Log groups for both Lambda functions.
* Retention: 14 days.
* Metrics/alerts recommended: Lambda errors, DLQ messages, queue age.

---

# Infrastructure (Terraform)

Recommended repository structure:

```
/ (repo root)
.
├── docs
│   ├── application
│   │   ├── consumer_lambda.md
│   │   └── producer_lambda.md
│   ├── architecture
│   │   ├── aws_components.md
│   │   └── overview.md
│   ├── deployment
│   │   ├── pipeline.md
│   │   └── testing.md
│   ├── guides
│   │   ├── setup_guide.md
│   │   └── troubleshooting.md
│   ├── index.md
│   └── infrastructure
│       ├── iam_roles.md
│       └── terraform_setup.md
├── Jenkinsfile
├── lambda
│   ├── consumer
│   │   ├── consumer.py
│   │   └── consumer.zip
│   └── producer
│       ├── producer.py
│       └── producer.zip
├── locals.tf
├── main.tf
├── mkdocs.yaml
├── modules
│   ├── api_gateway
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── cloudwatch
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── dynamodb
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── iam
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── lambdas
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   └── sqs
│       ├── main.tf
│       ├── outputs.tf
│       └── variables.tf
├── outputs.tf
├── Post_request.txt
├── README.md
└── versions.tf

```

### Notes on your `root/main.tf`

* Backend configured using S3 for Terraform state storage.
* Modules include: `sqs`, `dynamodb`, `iam`, `lambdas`, `api_gateway`, `cloudwatch`.

**Terraform usage**

```bash
cd library-request-system/
terraform init
terraform plan
terraform apply
```

---

# Git & GitHub Projects Strategy

### Branch Strategy

* `main`: production / approved deployments.
* `develop`: active development.
* Feature branches: `feature/<issue-number>-short-description`.

### Project Board

Kanban columns: Backlog → Ready → In Progress → In Review → Done.

---

# CI/CD Pipelines

## Jenkins Pipeline

1. Checkout
2. Terraform plan
3. terraform plan -input=false -out=tfplan.binary
4. terraform apply -input=false -auto-approve tfplan.binary
5. Clean workspace

## GitHub Actions (PR checks)

* Upload new documentation of MkDocs
* Just in the "docs" Folder

---

# Testing and Validation

## 1. Submit a request

```bash
curl -sS -X POST 'https://yorledc60d.execute-api.us-east-1.amazonaws.com/producer' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Atomic Habits",
    "author": "James Clear"
  }'
```

Expected: `202 Accepted` + `request_id`.

## 2. Check SQS Messages

`aws sqs get-queue-attributes --queue-url <url> --attribute-names ApproximateNumberOfMessages`

## 3. Validate DynamoDB

`aws dynamodb scan --table-name books-table --max-items 10`
