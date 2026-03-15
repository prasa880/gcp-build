pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins-kaniko-sa
  containers:
  - name: python-test
    image: python:3.12-slim
    command: ["cat"]
    tty: true
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ["sleep"]
    args: ["9999999"]
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["cat"]
    tty: true
'''
        }
    }

    environment {
        // Change this if your repository path changes
        IMAGE_PATH = 'us-central1-docker.pkg.dev/project-f749c631-40a8-4185-8cb/prasanth/new-build'
    }

    stages {
        stage('Checkout') {
            steps {
                // Pulls your code from GitHub
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                container('python-test') {
                    sh '''
                    pip install pytest flask
                    pytest tests/
                    '''
                }
            }
        }

        stage('Build & Push') {
            steps {
                container('kaniko') {
                    // Builds using the Dockerfile and pushes to Google Artifact Registry
                    sh """
                    /kaniko/executor \
                    --context ${env.WORKSPACE} \
                    --dockerfile Dockerfile \
                    --destination ${env.IMAGE_PATH}:${env.BUILD_NUMBER} \
                    --destination ${env.IMAGE_PATH}:latest \
                    --cache=true
                    """
                }
            }
        }

        stage('Deploy to GKE') {
            steps {
                container('kubectl') {
                    sh """
                    # Update the YAML with the new image tag we just built
                    sed -i "s|IMAGE_TAG|${env.BUILD_NUMBER}|g" deployment.yaml
                    
                    # Apply the deployment to your GKE cluster
                    kubectl apply -f deployment.yaml
                    
                    # Wait for the pods to be ready
                    kubectl rollout status deployment/my-python-app
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Successfully built and deployed version ${env.BUILD_NUMBER}"
        }
        failure {
            echo "Pipeline failed. Check logs for Unit Test or Kaniko errors."
        }
    }
}
