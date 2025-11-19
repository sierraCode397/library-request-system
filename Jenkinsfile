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
