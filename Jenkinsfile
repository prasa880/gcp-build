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
    resources:
      requests:
        cpu: "200m"
        memory: "256Mi"
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ["sleep"]
    args: ["9999999"]
    resources:
      requests:
        cpu: "500m"
        memory: "1Gi"
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["cat"]
    tty: true
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
'''
        }
    }

    environment {
        IMAGE_PATH = 'us-central1-docker.pkg.dev/project-f749c631-40a8-4185-8cb/prasanth/new-build'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Unit Tests') {
            steps {
                container('python-test') {
                    sh 'pip install pytest flask && pytest tests/'
                }
            }
        }

        stage('Build & Push') {
            steps {
                container('kaniko') {
                    sh "/kaniko/executor --context ${env.WORKSPACE} --dockerfile Dockerfile --destination ${env.IMAGE_PATH}:${env.BUILD_NUMBER} --destination ${env.IMAGE_PATH}:latest --cache=true"
                }
            }
        }

        stage('Deploy to GKE') {
            steps {
                container('kubectl') {
                    sh """
                    sed -i "s|IMAGE_TAG|${env.BUILD_NUMBER}|g" deployment.yaml
                    kubectl apply -f deployment.yaml
                    kubectl rollout status deployment/my-python-app
                    """
                }
            }
        }
    }
}
