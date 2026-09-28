pipeline {
    agent any

    stages {

        stage('Test') {
            steps {
                sh '''
                    if [ ! -d .venv ]; then
                        python3 -m venv .venv
                    fi

                    . .venv/bin/activate

                    python -m pip install -r app/requirements.txt

                    cd app
                    pytest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                        -t docker-3tier-app:jenkins-${BUILD_NUMBER} \
                        ./app
                '''
            }
        }
    }
}
