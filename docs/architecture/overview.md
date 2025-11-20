# Project Overview

## Introduction

This project implements a fully serverless, event‑driven architecture on AWS using Terraform. It is designed to demonstrate modern cloud patterns such as decoupling, asynchronous messaging, least‑privilege IAM, and scalable data persistence.

The system follows a simple but powerful workflow:

1. A client interacts with **API Gateway**.
2. API Gateway triggers the **Producer Lambda**, which sends messages to **SQS**.
3. The **Consumer Lambda** processes messages from SQS and stores them in **DynamoDB**.
4. **CloudWatch** provides monitoring and logging.

---

## Core Objectives

* Use Terraform to provision AWS resources in a modular and reusable structure.
* Demonstrate event‑driven communication using SQS.
* Provide a secure and scalable compute layer with AWS Lambda.
* Persist data using DynamoDB.
* Expose public endpoints through API Gateway.
* Ensure observability with CloudWatch logs and metrics.

---

## High-Level Architecture

The architecture consists of the following components:

### **API Layer**

* **API Gateway** routes HTTP requests to the Lambda producer function.

### **Compute Layer**

* **Producer Lambda** receives input from the API and sends messages to SQS.
* **Consumer Lambda** reads from SQS and writes data to DynamoDB.

### **Messaging Layer**

* **Amazon SQS** acts as a buffer between producer and consumer.
* A **Dead Letter Queue (DLQ)** stores failed messages for debugging.

### **Data Layer**

* **DynamoDB** stores book-related records in a scalable NoSQL table.

### **Security & IAM**

* IAM roles follow least-privilege access.
* Each Lambda gets only the permissions it needs.

### **Monitoring Layer**

* **CloudWatch Logs** for both Lambda functions.
* 14-day log retention for cost optimization.

---

## Terraform Structure

The project is divided into modules:

* `modules/sqs`
* `modules/dynamodb`
* `modules/iam`
* `modules/lambdas`
* `modules/api_gateway`
* `modules/cloudwatch`

Each module encapsulates creation, configuration, and outputs for its AWS resource.

The root `main.tf` orchestrates the entire architecture.

---

## Benefits of This Architecture

* **Scalable:** Lambdas and SQS handle load automatically.
* **Decoupled:** Producer and consumer run independently.
* **Serverless:** No servers to manage.
* **Cost-efficient:** Pay-per-use model.
* **Modular IaC:** Easy to maintain, extend, and reuse.

---

## Summary

This project demonstrates a clean, production-ready event‑driven architecture on AWS using Terraform. It shows how to combine serverless compute, message queues, and NoSQL storage while maintaining observability, security, and modularity.
