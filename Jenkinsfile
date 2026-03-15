pipeline {
  agent {
  kubernetes {
    yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:latest
    command:
    - sleep
    args:
    - "999999"
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
'''
  }
}

    environment {
        GCR_REPO = 'us-central1-docker.pkg.dev/project-f749c631-40a8-4185-8cb/prasanth/new-build'
        BUILD_VERSION = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push Image') {
            steps {
                container('kaniko') {
                    sh """
                    /kaniko/executor \
                    --context `pwd` \
                    --destination ${GCR_REPO}:${BUILD_VERSION}
                    """
                }
            }
        }
    }
}
