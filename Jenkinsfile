pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins-kaniko-sa
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ["sleep"]
    args: ["9999999"]
    resources:
      requests:
        cpu: "500m"
        memory: "1Gi"
      limits:
        cpu: "500m"
        memory: "1Gi"
'''
        }
    }

    environment {
        // Double check this path matches your GCP Console
        REGISTRY_URL = 'us-central1-docker.pkg.dev/project-f749c631-40a8-4185-8cb/prasanth/new-build'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push to GCR') {
            steps {
                container('kaniko') {
                    sh """
                    /kaniko/executor \
                    --context ${env.WORKSPACE} \
                    --dockerfile Dockerfile \
                    --destination ${REGISTRY_URL}:${env.BUILD_NUMBER} \
                    --destination ${REGISTRY_URL}:latest
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Success! Image is now in Artifact Registry."
        }
    }
}
