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

        stage('Deploy') {
            steps {
                bat 'docker rm -f studyflow-app >nul 2>&1 || echo No existing container'
                bat 'docker run -d -p 5000:5000 --name studyflow-app studyflow:latest'
            }
        }
    }
}