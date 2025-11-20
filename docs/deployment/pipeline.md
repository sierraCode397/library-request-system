# Deployment Pipeline

This document describes the deployment workflows used in the project, including **GitHub Actions** for documentation deployment and **Jenkins** for infrastructure deployment using Terraform.

---

# GitHub Actions: MkDocs Deployment to Vercel

This workflow deploys the documentation site to Vercel **only when documentation-related files change**.

## **Workflow Trigger**

Runs on:

* Push to `main` or `develop`
* Pull requests affecting documentation
* Manual execution (`workflow_dispatch`)

## **Key Features**

* Automatically detects changes in:
  `docs/**`, `mkdocs.yml`, `mkdocs.yaml`, `README.md`
* Builds MkDocs site
* Deploys site to Vercel using the Vercel CLI
* Cleans up old GitHub Actions artifacts
* Sets commit status to success or failure

## **Workflow Definition**

```yaml
name: Deploy MkDocs to Vercel (only on docs changes)

permissions:
  contents: read
  statuses: write

on:
  push:
    branches: ["main", "develop"]
    paths:
      - "docs/**"
      - "mkdocs.yml"
      - "mkdocs.yaml"
      - "README.md"
  pull_request:
    paths:
      - "docs/**"
      - "mkdocs.yml"
      - "mkdocs.yaml"
      - "README.md"
  workflow_dispatch:
```

### **Jobs Overview**

#### **1. cleanup-artifacts**

Deletes old GitHub Action artifacts, keeping only the latest **5**.

#### **2. build-and-deploy**

Steps:

1. Checkout repository
2. Setup Python 3.11
3. Install MkDocs + Material theme
4. Build static site (`mkdocs build`)
5. Install Vercel CLI
6. Deploy the site if the `site/` folder exists
7. Set commit status (success or failure)

---

# Jenkins Pipeline: Terraform Deployment

This Jenkins pipeline manages the AWS infrastructure using Terraform.

## **Pipeline Trigger & Agent**

Runs on Jenkins agent labeled: `worker-agents-main`.
Includes log cleanup: keep last 10 builds.

## **Environment Variables**

* `AWS_DEFAULT_REGION = us-east-1`

## **Stages Overview**

### **1. Checkout Branch**

* Triggered by webhook push event
* Checks out the repository
* Prints workspace details

### **2. Terraform Init**

Initializes Terraform using AWS credentials stored in Jenkins credentials manager.

### **3. Terraform Plan**

Generates a plan and outputs to `tfplan.binary`.

### **4. Terraform Apply**

Executed **only when the branch is `main`**.
Applies the plan using:

```bash
terraform apply -input=false -auto-approve tfplan.binary
```

## **Post Actions**

* **always:** clean workspace
* **success:** notify success
* **failure:** notify failure

## **Jenkinsfile**

```groovy
pipeline {
    agent { label 'worker-agents-main' }
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
    }
    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
    }
    stages {
        stage('Checkout Branch') {
            steps {
                echo "Webhook triggered for a push event!"
                echo "Build Number: #${env.BUILD_NUMBER}"
                echo "Running on Agent: ${env.NODE_NAME}"
                echo "Workspace: ${env.WORKSPACE}"
                checkout scm
                echo "--- Files in workspace: ---"
                sh 'ls -la'
            }
        }
        stage('Terraform Init') {
            steps {
                withCredentials([aws(accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY', credentialsId: 'AWS-Access-Keys')]) {
                    sh '''
                        set -e
                        terraform init -input=false
                    '''
                }
            }
        }
        stage('Terraform Plan') {
            steps {
                withCredentials([aws(accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY', credentialsId: 'AWS-Access-Keys')]) {
                    sh '''
                        set -e
                        terraform plan -input=false -out=tfplan.binary
                    '''
                }
            }
        }
        stage('Terraform Apply') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([aws(accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY', credentialsId: 'AWS-Access-Keys')]) {
                    sh '''
                        set -e
                        terraform apply -input=false -auto-approve tfplan.binary
                    '''
                }
            }
        }
    }
    post {
        always {
            echo "Pipeline finished. Cleaning workspace..."
            cleanWs()
        }
        success {
            echo "Webhook test pipeline SUCCEEDED."
        }
        failure {
            echo "Webhook test pipeline FAILED. Check Jenkins logs and webhook configuration."
        }
    }
}
```
