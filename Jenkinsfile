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

	stage('Push to Docker Hub') {
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
            steps {
                sh ''' 
                    echo "=== UPDATE KUBERNETES DEPLOYMENT ==="

                    kubectl set image deployment/app \
                    app=docker-3tier-app:jenkins-${BUILD_NUMBER}
                     
                    echo "=== WAIT FOR ROLLOUT ==="

                    kubectl rollout status deployment/app
                '''
            }
        }
    }
}
