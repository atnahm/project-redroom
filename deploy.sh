#!/bin/bash
# REDROOM deployment script
# Deploys video forensic analysis system to Kubernetes

set -e

NAMESPACE="redroom"
IMAGE_NAME="redroom"
IMAGE_TAG="latest"
REGISTRY="${DOCKER_REGISTRY:-docker.io}"

echo "REDROOM Deployment Script"
echo "========================="
echo ""

# Check prerequisites
check_requirements() {
    echo "Checking requirements..."

    if ! command -v docker &> /dev/null; then
        echo "ERROR: Docker not found"
        exit 1
    fi

    if ! command -v kubectl &> /dev/null; then
        echo "ERROR: kubectl not found"
        exit 1
    fi

    echo "OK: Docker and kubectl found"
}

# Build Docker image
build_image() {
    echo ""
    echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
    docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
    echo "OK: Image built successfully"
}

# Push to registry (optional)
push_image() {
    if [ -z "$REGISTRY" ] || [ "$REGISTRY" = "docker.io" ]; then
        echo ""
        echo "Skipping registry push (set DOCKER_REGISTRY to enable)"
        return
    fi

    echo ""
    echo "Pushing to registry: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    docker tag "${IMAGE_NAME}:${IMAGE_TAG}" \
        "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    docker push "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    echo "OK: Image pushed"
}

# Deploy to Kubernetes
deploy() {
    echo ""
    echo "Deploying to Kubernetes namespace: ${NAMESPACE}"

    # Create namespace if not exists
    kubectl create namespace "${NAMESPACE}" || true

    # Apply manifests
    kubectl apply -f kubernetes/deployment.yaml

    echo "OK: Deployment initiated"
    echo ""
    echo "Waiting for pods to be ready (timeout: 5 minutes)..."
    kubectl rollout status deployment/redroom-api -n "${NAMESPACE}" \
        --timeout=5m || true

    echo ""
    echo "Deployment Status:"
    kubectl get pods -n "${NAMESPACE}" -o wide
    kubectl get svc -n "${NAMESPACE}"
}

# Main
main() {
    check_requirements
    build_image
    push_image
    deploy

    echo ""
    echo "Deployment complete!"
    echo ""
    echo "Next steps:"
    echo "1. Check pod status: kubectl get pods -n ${NAMESPACE}"
    echo "2. View logs: kubectl logs -n ${NAMESPACE} deployment/redroom-api"
    echo "3. Port forward: kubectl port-forward -n ${NAMESPACE} svc/redroom-api 8002:8002"
    echo "4. Test API: curl http://localhost:8002/redroom/status"
}

main
