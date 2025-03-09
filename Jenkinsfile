pipeline {
    agent any

    environment {
        GIT_REPO = "https://github.com/Moesthetics-code/gestion_ecole.git"
        DOCKER_REGISTRY = "https://hub.docker.com/u/moesthetic"
        NEXUS_URL = "http://nexus.your-company.com/repository/school_management/"
        SONARQUBE_URL = "http://sonarqube.your-company.com"
        SONAR_TOKEN = credentials('sonarqube-token')
        K8S_NAMESPACE = "school-namespace"
        HELM_RELEASE = "school-release"
    }

    stages {

        stage('Start Services with Docker Compose') {
            steps {
                script {
                    sh 'docker-compose up -d'
                }
            }
        }

        stage('Clone Source Code') {
            steps {
                git branch: 'main', url: "${GIT_REPO}"
            }
        }

        stage('Build Backend and Frontend') {
            parallel {
                stage('Build Backend Services') {
                    steps {
                        script {
                            def services = ['gateway', 'classes', 'cours', 'etudiants', 'professeurs', 'emplois']
                            services.each { service ->
                                dir("services/${service}") {
                                    docker.build("${DOCKER_REGISTRY}/${service}:latest", "./")
                                }
                            }
                        }
                    }
                }

                stage('Build Frontend') {
                    steps {
                        dir('frontend') {
                            script {
                                // Construire le frontend avec Docker
                                docker.build("${DOCKER_REGISTRY}/school-frontend:latest", "./Dockerfile")
                            }
                        }
                    }
                }
            }
        }

        stage('Run Unit Tests') {
            parallel {
                stage('Backend Tests') {
                    steps {
                        script {
                            def services = ['classes', 'cours', 'etudiants', 'professeurs', 'emplois']
                            services.each { service ->
                                dir("services/${service}") {
                                    sh 'pytest --maxfail=1 --disable-warnings -q'
                                }
                            }
                        }
                    }
                }

                stage('Frontend Tests') {
                    steps {
                        dir('frontend') {
                            script {
                                sh 'npm test -- --maxWorkers=4'
                            }
                        }
                    }
                }
            }
        }

        stage('Run Selenium Tests') {
            steps {
                script {
                    echo ' Lancement des tests Selenium...'

                    docker.image('selenium/standalone-chrome').inside {
                        dir('services/tests') {
                            sh 'pytest --maxfail=1 --disable-warnings -q'
                        }
                    }

                }
            }
        }

        stage('Code Quality with SonarQube') {
            steps {
                script {
                    sh """
                        sonar-scanner \
                            -Dsonar.projectKey=school_management \
                            -Dsonar.sources=services,frontend \
                            -Dsonar.host.url=${SONARQUBE_URL} \
                            -Dsonar.login=${SONAR_TOKEN}
                    """
                }
            }
        }

        stage('Build Docker Image and Push to Nexus') {
            steps {
                script {
                    // Construire l'image Docker à partir du Dockerfile
                    docker.build("myapp:${BUILD_TAG}", ".")

                    // Pousser l'image Docker vers Nexus (ou un autre registre Docker)
                    docker.withRegistry("${NEXUS_URL}", 'nexus-credentials') {
                        docker.image("myapp:${BUILD_TAG}").push()
                    }
                }
            }
        }

        stage('Build and Push Docker Images') {
            parallel {
                stage('Push Backend Images') {
                    steps {
                        script {
                            def services = ['gateway', 'classes', 'cours', 'etudiants', 'professeurs', 'emplois']
                            services.each { service ->
                                docker.withRegistry("https://${DOCKER_REGISTRY}", "docker-credentials") {
                                    docker.image("${DOCKER_REGISTRY}/${service}:latest").push()
                                }
                            }
                        }
                    }
                }

                stage('Push Frontend Image') {
                    steps {
                        dir('frontend') {
                            script {
                                docker.withRegistry("https://${DOCKER_REGISTRY}", "docker-credentials") {
                                    docker.image("${DOCKER_REGISTRY}/school-frontend:latest").push()
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Déploiement des ConfigMaps
                    sh """
                        helm upgrade --install loki-config ./kubernetes/loki-config --values ./kubernetes/values.yaml
                        helm upgrade --install promtail-config ./kubernetes/promtail-config --values ./kubernetes/values.yaml
                        helm upgrade --install prometheus-config ./kubernetes/prometheus-config --values ./kubernetes/values.yaml
                        helm upgrade --install grafana-dashboard-configmap ./kubernetes/grafana-dashboard-configmap --values ./kubernetes/values.yaml
                        helm upgrade --install alertmanager-config ./kubernetes/alertmanager-config --values ./kubernetes/values.yaml
                        helm upgrade --install alert-rules ./kubernetes/alert-rules --values ./kubernetes/values.yaml
                    """

                    // Déploiement des services et des bases de données
                    sh """
                        helm upgrade --install postgres ./kubernetes/postgres --values ./kubernetes/values.yaml
                        helm upgrade --install loki ./kubernetes/loki --values ./kubernetes/values.yaml
                        helm upgrade --install promtail ./kubernetes/promtail --values ./kubernetes/values.yaml
                        helm upgrade --install prometheus ./kubernetes/prometheus --values ./kubernetes/values.yaml
                        helm upgrade --install grafana ./kubernetes/grafana --values ./kubernetes/values.yaml
                        helm upgrade --install grafana-pvc ./kubernetes/grafana-pvc --values ./kubernetes/values.yaml
                    """

                    // Déploiement des applications avec Helm en utilisant les dernières images Docker
                    sh """
                        helm upgrade --install ${HELM_RELEASE} ./kubernetes/ \
                            --namespace ${K8S_NAMESPACE} \
                            --set image.gateway=${DOCKER_REGISTRY}/gateway:latest \
                            --set image.classes=${DOCKER_REGISTRY}/classes:latest \
                            --set image.cours=${DOCKER_REGISTRY}/cours:latest \
                            --set image.etudiants=${DOCKER_REGISTRY}/etudiants:latest \
                            --set image.professeurs=${DOCKER_REGISTRY}/professeurs:latest \
                            --set image.emplois_du_temps=${DOCKER_REGISTRY}/emplois:latest \
                            --set image.frontend=${DOCKER_REGISTRY}/school-frontend:latest
                    """
                }
            }
        }

        stage('Restart Services') {
            steps {
                script {
                    def services = ['gateway', 'classes', 'cours', 'etudiants', 'professeurs', 'emplois']
                    services.each { service ->
                        sh "kubectl rollout restart deployment/${service}"
                    }
                }
            }
        }

        stage('Monitoring and Logging') {
            steps {
                script {
                    // Vérification de l'état des services (Grafana, Prometheus, Loki)
                    sh """
                        echo "🔍 Vérification des services de monitoring"
                        if curl -sSf http://grafana-service:3000/api/health; then
                            echo " Grafana est disponible"
                        else
                            echo " Grafana unreachable"
                        fi

                        if curl -sSf http://prometheus-service/api/v1/query?query=up; then
                            echo " Prometheus est disponible"
                        else
                            echo " Prometheus unreachable"
                        fi

                        if curl -sSf http://loki:3100/ready; then
                            echo " Loki est disponible"
                        else
                            echo " Loki unreachable"
                        fi
                    """

                    // Récupération des logs journaliers depuis Loki (Python app)
                    def date = new Date().format("yyyy-MM-dd")
                    sh """
                        echo " Récupération des logs journaliers depuis Loki"
                        curl -s -G --data-urlencode 'query={job="python-app", filename="/logs/log_${date}.log"}' \
                            http://loki:3100/loki/api/v1/query > logs/python-logs-${date}.txt
                    """

                    // Vérification des logs avant l'envoi
                    sh """
                        if [ -s logs/python-logs-${date}.txt ]; then
                            echo " Logs journaliers récupérés pour ${date}"
                        else
                            echo " Aucun log trouvé pour ${date}"
                        fi
                    """

                    // Envoi des logs dans Loki via API de push
                    sh """
                        echo " Envoi des logs vers Loki"
                        curl -X POST -H "Content-Type: application/json" \
                            -d @logs/python-logs-${date}.txt \
                            http://loki:3100/loki/api/v1/push
                    """
                }
            }
        }

        parameters {
            choice(name: 'DEPLOY_ENV', choices: ['dev', 'staging', 'prod'], description: 'Choisir l’environnement de déploiement')
        }

        stages {
            stage('Deploy to Environment') {
                steps {
                    script {
                        if (params.DEPLOY_ENV == "dev") {
                            echo "🚀 Déploiement en DEV sur Docker Compose"
                            sh 'docker-compose up -d'
                        } else if (params.DEPLOY_ENV == "staging") {
                            echo "🚀 Déploiement en STAGING sur Minikube"
                            sh 'kubectl apply -f kubernetes/staging/'
                        } else if (params.DEPLOY_ENV == "prod") {
                            echo "🚀 Déploiement en PROD sur Kubernetes Cloud"
                            sh 'helm upgrade --install school-prod kubernetes/prod/ --namespace prod'
                        } else {
                            error "❌ Environnement inconnu : ${params.DEPLOY_ENV}"
                        }
                    }
                }
            }
        }

    }

    post {
        always {
            echo 'Pipeline terminé, nettoyage des services Docker...'
        }
        success {
            echo ' Pipeline exécuté avec succès !'
        }
        failure {
            script {
                echo " Échec du pipeline, récupération des logs..."
                sh "kubectl logs deployment/${HELM_RELEASE}-gateway -n ${K8S_NAMESPACE} > gateway-logs.txt"
                sh "kubectl logs deployment/${HELM_RELEASE}-frontend -n ${K8S_NAMESPACE} > frontend-logs.txt"
            }
        }
    }
}
