pipeline {
    agent any

    environment {
        DOCKERHUB_USERNAME = 'abrar15'
    }

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

        stage('Check App Changes') {
            steps {
                script {
                    def previous = env.GIT_PREVIOUS_SUCCESSFUL_COMMIT
                    def current = env.GIT_COMMIT

                    if (!previous) {
                        env.APP_CHANGED = 'true'
                        echo "No previous successful build found."
                    } else {
                        def result = sh(
                            script: "git diff --quiet ${previous} ${current} -- app/",
                            returnStatus: true
                        )

                        if (result == 1) {
                            env.APP_CHANGED = 'true'
                            echo "Changes detected in app/"
                        } else if (result == 0) {
                            env.APP_CHANGED = 'false'
                            echo "No changes detected in app/"
                        } else {
                            error("git diff failed")
                        }
                    }

                    echo "APP_CHANGED = ${env.APP_CHANGED}"
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression {
                    env.APP_CHANGED == 'true'
                }
            }

            steps {
                sh '''
                    docker build \
                        -t docker-3tier-app:jenkins-${BUILD_NUMBER} \
                        ./app
                '''
            }
        }

        stage('Push to Docker Hub') {
            when {
                expression {
                    env.APP_CHANGED == 'true'
                }
            }

            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login \
                            -u "$DOCKERHUB_USERNAME" \
                            --password-stdin

                        docker tag \
                            docker-3tier-app:jenkins-${BUILD_NUMBER} \
                            "$DOCKERHUB_USERNAME/docker-3tier-app:jenkins-${BUILD_NUMBER}"

                        docker push \
                            "$DOCKERHUB_USERNAME/docker-3tier-app:jenkins-${BUILD_NUMBER}"

                        docker logout
                    '''
                }
            }
        }

        stage('Update Kubernetes') {
            when {
                expression {
                    env.APP_CHANGED == 'true'
                }
            }

            steps {
                sh '''
                    echo "=== UPDATE KUBERNETES DEPLOYMENT ==="

                    kubectl set image deployment/app \
                        app="$DOCKERHUB_USERNAME/docker-3tier-app:jenkins-${BUILD_NUMBER}"

                    echo "=== WAIT FOR ROLLOUT ==="

                    kubectl rollout status deployment/app
                '''
            }
        }
    }
}
