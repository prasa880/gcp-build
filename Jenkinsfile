pipeline {
    agent any

    environment {
        // Set your GCR repository URL
        GCR_REPO = 'us-central1-docker.pkg.dev/project-f749c631-40a8-4185-8cb/prasanth/new-build'
        // Build version (e.g., you can use a build number or timestamp)
        BUILD_VERSION = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                // Pull the code from GitHub
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    sh 'docker build -t my-app:${BUILD_VERSION} .'
                    // Tag the image for GCR
                    sh "docker tag my-app:${BUILD_VERSION} ${GCR_REPO}:${BUILD_VERSION}"
                }
            }
        }
    }
