pipeline {
    agent { label 'worker-agents-main' }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
    }
    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
    }
    stages {
        stage('Test Webhook: Checkout Branch') {
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
        stage('Determine Event Type') {
            steps {
                withCredentials([aws(accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY', credentialsId: 'aws-credentials-id')]) {
                    sh '''
                        aws ec2 describe-instances
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
            echo " Webhook test pipeline SUCCEEDED."
        }
        failure {
            echo " Webhook test pipeline FAILED. Check Jenkins logs and webhook configuration."
        }
    }
}