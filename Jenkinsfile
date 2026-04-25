pipeline {
    agent any

    environment {
        IMAGE_TAG    = "${env.GIT_COMMIT?.take(7) ?: 'latest'}"
        COMPOSE_FILE = 'docker-compose.yml'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Lint') {
            steps {
                sh 'docker run --rm -i hadolint/hadolint < backend/Dockerfile || true'
                sh 'docker run --rm -i hadolint/hadolint < nginx/Dockerfile   || true'
            }
        }
        stage('Build Images') {
            steps { sh "docker compose -f ${COMPOSE_FILE} build --no-cache" }
        }
        stage('Start Services') {
            steps {
                sh "docker compose -f ${COMPOSE_FILE} up -d"
                sh 'sleep 15'
            }
        }
        stage('Health Check') {
            steps {
                sh '''
                    status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
                    [ "$status" = "200" ] || { docker compose logs; exit 1; }
                    echo "Health check passed: HTTP $status"
                '''
            }
        }
        stage('Smoke Test') {
            steps {
                sh '''
                    curl -s http://localhost:8080/api/tasks | grep -q '"tasks"' || exit 1
                    curl -sf -X POST http://localhost:8080/api/tasks \
                         -H "Content-Type: application/json" \
                         -d '{"title":"CI smoke task","description":"Created by Jenkins"}' \
                         | grep -q '"id"' || exit 1
                    echo "Smoke tests passed."
                '''
            }
        }
    }

    post {
        always  { sh "docker compose -f ${COMPOSE_FILE} down -v || true" }
        failure { sh "docker compose -f ${COMPOSE_FILE} logs || true" }
    }
}
