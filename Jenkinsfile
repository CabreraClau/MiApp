pipeline {
  agent any
  options { timestamps() }

  parameters {
    string(name: 'IMAGE_NAME', defaultValue: 'notas-api', description: 'Nombre de la imagen Docker')
    string(name: 'K8S_NAMESPACE', defaultValue: 'notas', description: 'Namespace de Kubernetes')
  }

  environment {
    FULL_IMAGE = "${params.IMAGE_NAME}:latest"  // usamos :latest para simplificar
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Start Minikube (si hace falta)') {
      steps {
        sh '''
          set -e
          minikube status >/dev/null 2>&1 || minikube start
          kubectl config use-context minikube
        '''
      }
    }

    stage('Build Docker image') {
      steps {
        sh '''
          set -e
          docker build -t ${FULL_IMAGE} .
          docker images | grep ${params.IMAGE_NAME}
        '''
      }
    }

    stage('Load image into Minikube') {
      steps {
        sh '''
          set -e
          # Carga la imagen local al registry interno de minikube
          minikube image load ${FULL_IMAGE}
        '''
      }
    }

    stage('Prepare Namespace') {
      steps {
        sh '''
          set -e
          kubectl get ns ${K8S_NAMESPACE} >/dev/null 2>&1 || kubectl create ns ${K8S_NAMESPACE}
        '''
      }
    }

    stage('Apply ConfigMap') {
      steps {
        sh '''
          set -e
          kubectl -n ${K8S_NAMESPACE} apply -f k8s/notas-config.yaml
        '''
      }
    }

    stage('Deploy App') {
      steps {
        sh '''
          set -e
          kubectl -n ${K8S_NAMESPACE} apply -f k8s/deployment.yaml

          # Esperar rollout de las 3 instancias (3 Deployments de 1 réplica)
          kubectl -n ${K8S_NAMESPACE} rollout status deployment/notas-deployment-1
          kubectl -n ${K8S_NAMESPACE} rollout status deployment/notas-deployment-2
          kubectl -n ${K8S_NAMESPACE} rollout status deployment/notas-deployment-3
        '''
      }
    }

    stage('Expose Services') {
      steps {
        sh '''
          set -e
          # Crea NodePorts si no existen
          kubectl -n ${K8S_NAMESPACE} get svc notas-svc-1 >/dev/null 2>&1 || \
            kubectl -n ${K8S_NAMESPACE} expose deployment notas-deployment-1 --type=NodePort --port=5000 --name=notas-svc-1
          kubectl -n ${K8S_NAMESPACE} get svc notas-svc-2 >/dev/null 2>&1 || \
            kubectl -n ${K8S_NAMESPACE} expose deployment notas-deployment-2 --type=NodePort --port=5000 --name=notas-svc-2
          kubectl -n ${K8S_NAMESPACE} get svc notas-svc-3 >/dev/null 2>&1 || \
            kubectl -n ${K8S_NAMESPACE} expose deployment notas-deployment-3 --type=NodePort --port=5000 --name=notas-svc-3
        '''
      }
    }

    stage('Show URLs (minikube)') {
      steps {
        sh '''
          set +e
          echo "URL instancia 1:"
          minikube service -n ${K8S_NAMESPACE} notas-svc-1 --url || true
          echo "URL instancia 2:"
          minikube service -n ${K8S_NAMESPACE} notas-svc-2 --url || true
          echo "URL instancia 3:"
          minikube service -n ${K8S_NAMESPACE} notas-svc-3 --url || true
        '''
      }
    }
  }

  post {
    always {
      sh '''
        echo "==== PODS ===="
        kubectl -n ${K8S_NAMESPACE} get pods -o wide || true
        echo "==== SERVICES ===="
        kubectl -n ${K8S_NAMESPACE} get svc || true
      '''
    }
  }
}
