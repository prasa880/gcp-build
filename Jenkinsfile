
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
    image: python:3.9-slim
    command: ["cat"]
    tty: true
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ["sleep"]
    args: ["9999999"]
'''
        }
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Unit Tests') {
            steps {
                container('python-test') {
                    sh '''
                    pip install -r requirements.txt
                    pip install pytest
                    pytest tests/  --junitxml=results.xml
                    '''
                }
            }
            post {
                always {
                    // This creates a nice "Test Result" tab in Jenkins
                    junit 'results.xml'
                }
            }
        }

        stage('Build & Push (Kaniko)') {
            // Only runs if 'Unit Tests' passes
            steps {
                container('kaniko') {
                    sh "/kaniko/executor --context ${env.WORKSPACE} --dockerfile Dockerfile --destination ${REGISTRY_URL}:${env.BUILD_NUMBER}"
                }
            }
        }
    }
}
