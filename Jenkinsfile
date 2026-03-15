
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
    resources:
      requests:
        cpu: "500m"
        memory: "1Gi"
'''
        }
    }

    environment {
        // Updated to your specific registry path
        IMAGE_PATH = 'us-central1-docker.pkg.dev/project-f749c631-40a8-4185-8cb/prasanth/new-build'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Unit Tests') {
            steps {
                container('python-test') {
                    sh '''
                    pip install pytest
                    pytest tests/
                    '''
                }
            }
        }

        stage('Build & Push') {
            steps {
                container('kaniko') {
                    // --cache=true helps speed up future builds
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
    }
}
