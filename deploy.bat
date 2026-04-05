@echo off
REM REDROOM deployment script for Windows
REM Deploys video forensic analysis system

setlocal enabledelayedexpansion

set NAMESPACE=redroom
set IMAGE_NAME=redroom
set IMAGE_TAG=latest
set REGISTRY=%DOCKER_REGISTRY%

if not defined REGISTRY (
    set REGISTRY=docker.io
)

echo.
echo REDROOM Deployment Script
echo =========================
echo.

REM Check prerequisites
echo Checking requirements...

where docker >nul 2>nul
if errorlevel 1 (
    echo ERROR: Docker not found
    exit /b 1
)

where kubectl >nul 2>nul
if errorlevel 1 (
    echo ERROR: kubectl not found
    exit /b 1
)

echo OK: Docker and kubectl found
echo.

REM Build Docker image
echo Building Docker image: %IMAGE_NAME%:%IMAGE_TAG%
docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
if errorlevel 1 (
    echo ERROR: Docker build failed
    exit /b 1
)
echo OK: Image built successfully
echo.

REM Deploy to Kubernetes
echo Deploying to Kubernetes namespace: %NAMESPACE%

kubectl create namespace %NAMESPACE% 2>nul
if errorlevel 1 (
    echo Namespace may already exist
)

kubectl apply -f kubernetes/deployment.yaml
if errorlevel 1 (
    echo ERROR: Kubernetes deployment failed
    exit /b 1
)

echo OK: Deployment initiated
echo.
echo Waiting for pods to be ready (timeout: 5 minutes)...
kubectl rollout status deployment/redroom-api -n %NAMESPACE% --timeout=5m

echo.
echo Deployment Status:
kubectl get pods -n %NAMESPACE% -o wide
kubectl get svc -n %NAMESPACE%

echo.
echo Deployment complete!
echo.
echo Next steps:
echo 1. Check pod status: kubectl get pods -n %NAMESPACE%
echo 2. View logs: kubectl logs -n %NAMESPACE% deployment/redroom-api
echo 3. Port forward: kubectl port-forward -n %NAMESPACE% svc/redroom-api 8002:8002
echo 4. Test API: curl http://localhost:8002/redroom/status
echo.
