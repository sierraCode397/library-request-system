pipeline {
    agent { label 'worker-agents-main' }

    options {
        // Keep max 10 builds, and only 5 with archived artifacts like HTML
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
    }

    stages {
        stage('Determine Event Type') {
            steps {
                script {
                    if (env.CHANGE_ID) {
                        // 1) Any PR build (this includes “PRHead” and “PRMerge” if you built both).
                        echo "🔀 Pull Request build: #${env.CHANGE_ID}"
                        echo "   Source branch: ${env.CHANGE_BRANCH}"
                        echo "   Target branch: ${env.CHANGE_TARGET}"
                        echo "   PR Title: ${env.CHANGE_TITLE}"
                        echo "   PR Author: ${env.CHANGE_AUTHOR}"
                    } else {
                        // 2) Branch build: either a direct git push, or an actual PR-merge into that branch
                        def branchName = env.BRANCH_NAME
                        def isMerge = sh(
                            script: "git rev-parse HEAD^2 >/dev/null 2>&1 && echo true || echo false",
                            returnStdout: true
                        ).trim()

                        if (isMerge == 'true') {
                            echo "⚙️ Build triggered by a MERGE commit on branch '${branchName}'"
                            echo "   (Likely the result of merging a PR into ${branchName}.)"
                        } else {
                            def commitSha = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                            echo "📥 Build triggered by a regular PUSH to branch '${branchName}'"
                            echo "   Commit: ${commitSha}"
                        }
                    }
                }
            }
        }

        stage('Test Webhook: Checkout Branch') {
            steps {
                echo "Webhook triggered for a push event!"
                echo "Build Number: #${env.BUILD_NUMBER}"
                echo "Running on Agent: ${env.NODE_NAME}"
                echo "Workspace: ${env.WORKSPACE}"

                // The 'checkout scm' step automatically checks out the correct commit
                // from the branch that triggered the build (in this case, 'main' branch
                // due to the push event and job configuration).
                echo "Attempting to checkout the pushed commit from the 'main' branch..."
                checkout scm

                echo "--- Checkout SCM complete. Current commit details: ---"
                sh 'git rev-parse HEAD' // Shows the SHA of the checked-out commit
                sh 'git log -1 --pretty="Commit: %h%nBranch: %D%nAuthor: %an <%ae>%nDate: %ad%nSubject: %s"' // Shows commit details including branch info

                echo "--- Files in workspace: ---"
                sh 'ls -la'
            }
        }
    }

    post {
        always {
            echo "Pipeline finished. Cleaning workspace..."
            // Cleaning the workspace is good practice
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