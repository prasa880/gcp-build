pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug  # 'debug' contains a shell (sh), 'latest' does not
    command:
    - sleep
    args:
    - "999999"
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
        // Correcting the format to ensure it's a valid Artifact Registry path
        GCR_REPO = 'us-central1-docker.pkg.dev/project-f749c631-40a8-4185-8cb/prasanth/new-build'
    }

    stages {
        stage('Build & Push Image') {
            steps {
                container('kaniko') {
                    // Using env variables directly in the shell
                    sh """
                    /kaniko/executor \
                    --context ${env.WORKSPACE} \
                    --dockerfile Dockerfile \
                    --destination ${GCR_REPO}:${env.BUILD_NUMBER} \
                    --cache=true
                    """
                }
            }
        }
    }
}
