
pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ["sleep"]
    args: ["9999999"]
    volumeMounts:
    - name: gcp-key
      mountPath: /kaniko/.docker/
  volumes:
  - name: gcp-key
    secret:
      secretName: gcp-service-account
      items:
        - key: .dockerconfigjson
          path: config.json
'''
        }
    }

    environment {
        // The path to your Google Artifact Registry
        REGISTRY_URL = 'us-central1-docker.pkg.dev/project-f749c631-40a8-4185-8cb/prasanth/new-build'
    }

    stages {
        stage('Checkout Source') {
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
                    --destination ${REGISTRY_URL}:latest \
                    --cache=true
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Successfully pushed image version: ${env.BUILD_NUMBER}"
        }
        failure {
            echo "Build failed. Check the Kaniko container logs."
        }
    }
}
