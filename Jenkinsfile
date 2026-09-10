pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat 'python -m pytest -q'
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker build -t studyflow:latest .'
            }
        }
    }
}

// Jenkins automatic trigger test