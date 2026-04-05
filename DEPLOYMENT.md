# REDROOM Deployment Guide

Production deployment instructions for video forensic analysis system.

## Prerequisites

- Docker 20.10+ or Container runtime compatible with OCI
- Kubernetes 1.24+ cluster (for K3s deployment)
- NVIDIA GPU with CUDA 11.8+ (optional acceleration)
- 32GB+ RAM (minimum 16GB)
- 500GB+ SSD storage (minimum)

## Docker Deployment

### Single Machine Setup

```bash
cd redroom
docker-compose up -d
```

Services:
- API: http://localhost:8002
- vLLM: http://localhost:8001 (internal)

### Verify Services

```bash
docker-compose logs api
docker-compose ps

curl http://localhost:8002/redroom/status
```

### Configuration

Edit environment variables in `docker-compose.yml`:

```yaml
environment:
  - VLLM_ENDPOINT=http://vllm:8000
  - LEDGER_DB_PATH=/var/redroom/ledger/redroom_ledger.db
  - LOG_LEVEL=INFO
```

### Data Persistence

Volumes persists in:
- `/var/lib/docker/volumes/redroom_ledger_data`
- `/var/lib/docker/volumes/vllm_models`

### GPU Support

For NVIDIA GPU acceleration, install NVIDIA Docker runtime:

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

docker-compose up -d vllm
```

Verify GPU:
```bash
docker exec redroom-vllm nvidia-smi
```

## Kubernetes Deployment

### Prerequisites

Install K3s:
```bash
curl -sfL https://get.k3s.io | sh -
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

Verify:
```bash
kubectl cluster-info
kubectl get nodes
```

### Deploy to Kubernetes

```bash
kubectl apply -f kubernetes/deployment.yaml
```

### Verify Deployment

```bash
kubectl get pods -n redroom
kubectl get svc -n redroom
kubectl logs -n redroom deployment/redroom-api
```

### Access API

Get LoadBalancer IP:
```bash
kubectl get svc -n redroom redroom-api
```

If LoadBalancer IP is pending (EXTERNAL-IP: <pending>), use NodePort:
```bash
kubectl port-forward -n redroom svc/redroom-api 8002:8002
```

API available at: http://localhost:8002

### Scale Deployment

```bash
kubectl scale deployment redroom-api --replicas=5 -n redroom
```

Deployment will auto-scale based on CPU/memory utilization (2-10 replicas).

### Monitor Resources

```bash
kubectl top nodes
kubectl top pods -n redroom
kubectl describe pod <pod-name> -n redroom
```

### Update Deployment

After code changes:

```bash
docker build -t redroom:latest .
docker push your-registry.com/redroom:latest

kubectl set image deployment/redroom-api \
  redroom-api=your-registry.com/redroom:latest -n redroom
```

## Production Hardening

### Network Security

Restrict API access with NetworkPolicy:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: redroom-network-policy
  namespace: redroom
spec:
  podSelector:
    matchLabels:
      app: redroom-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: redroom-client
    ports:
    - protocol: TCP
      port: 8002
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redroom-vllm
    ports:
    - protocol: TCP
      port: 8000
  - to:
    - namespaceSelector: {}
      port:
        protocol: TCP
        port: 53 # DNS
```

### Resource Limits

Kubernetes limits already configured in deployment.yaml:

```yaml
resources:
  requests:
    memory: "8Gi"
    cpu: "4"
  limits:
    memory: "16Gi"
    cpu: "8"
```

### Persistent Data

Configure backup for ledger:

```bash
kubectl exec -n redroom deployment/redroom-api -- \
  sqlite3 /var/redroom/ledger/redroom_ledger.db ".backup '/backups/ledger.db'"
```

### Logging

Collect logs from all pods:

```bash
kubectl logs -n redroom deployment/redroom-api --all-containers=true
kubectl logs -n redroom deployment/redroom-vllm
```

Configure log aggregation (ELK, Loki, etc.):

```bash
kubectl logs -n redroom -f deployment/redroom-api --timestamps=true
```

## Cloud Deployment

### Azure Kubernetes Service (AKS)

```bash
az aks create --resource-group myResourceGroup \
  --name redroom-aks --node-count 3

az aks get-credentials --resource-group myResourceGroup \
  --name redroom-aks

kubectl apply -f kubernetes/deployment.yaml
```

### AWS EKS

```bash
eksctl create cluster --name redroom --region us-east-1 --nodes 3

aws eks update-kubeconfig --name redroom --region us-east-1

kubectl apply -f kubernetes/deployment.yaml
```

### Google GKE

```bash
gcloud container clusters create redroom \
  --num-nodes 3 --zone us-central1-a

gcloud container clusters get-credentials redroom

kubectl apply -f kubernetes/deployment.yaml
```

## Performance Tuning

### CPU-bound Analysis

On systems without GPU, increase CPU limits:

```yaml
resources:
  requests:
    cpu: "8"
  limits:
    cpu: "16"
```

Adjust analysis timeout in config.py:
```python
ANALYSIS_TIMEOUT_SECONDS = 180  # Increase for slower systems
```

### Memory Constraints

For systems with limited RAM:

```yaml
resources:
  requests:
    memory: "4Gi"
  limits:
    memory: "8Gi"
```

Reduce vLLM model size:
```yaml
command: |
  python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2-VL-7B-Instruct \
    --max-model-len 1024  # Reduced context
```

### Storage Performance

Use SSD for ledger:

```bash
kubectl patch pvc redroom-ledger-pvc -n redroom \
  -p '{"spec":{"storageClassName":"fast-ssd"}}'
```

## Backup and Recovery

### Backup Ledger

```bash
kubectl exec -n redroom deployment/redroom-api -- \
  tar czf - /var/redroom/ledger | gzip > ledger-backup.tar.gz
```

### Restore Ledger

```bash
tar xzf ledger-backup.tar.gz -C /tmp
kubectl cp /tmp/var/redroom/ledger redroom/redroom-api-0:/var/redroom/
```

## Monitoring and Alerting

### Health Checks

All services include liveness and readiness probes. Verify:

```bash
kubectl get pod -n redroom -o wide
```

Watch for CrashLoopBackOff or Pending states.

### Metrics

Kubernetes exposes metrics at:
- `kubectl top pods -n redroom`
- `kubectl top nodes`

For Prometheus scraping:
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8002"
  prometheus.io/path: "/metrics"
```

## Troubleshooting

### Pod Not Starting

```bash
kubectl describe pod <pod-name> -n redroom
kubectl logs <pod-name> -n redroom --previous
```

### API Not Responding

```bash
kubectl port-forward svc/redroom-api 8002:8002 -n redroom
curl -v http://localhost:8002/redroom/status
```

### Memory Issues

```bash
kubectl get pod -n redroom -o jsonpath='{.items[*].spec.containers[*].resources}'
kubectl top pod -n redroom --sort-by=memory
```

### Storage Full

```bash
kubectl exec -n redroom deployment/redroom-api -- df -h
kubectl exec -n redroom deployment/redroom-api -- \
  du -sh /var/redroom/ledger/
```

## Cleanup

### Stop Services

```bash
docker-compose down  # Docker

kubectl delete namespace redroom  # Kubernetes
```

### Remove Persistent Data

```bash
docker volume rm redroom_ledger_data redroom_vllm_models  # Docker

kubectl delete pvc redroom-ledger-pvc -n redroom  # Kubernetes
```

## Version Information

- Python: 3.11
- FastAPI: 0.104.1+
- OpenCV: 4.8+
- CUDA: 11.8+ (optional)
- Kubernetes: 1.24+

## Support

For deployment issues, check:
1. Hardware meets minimum requirements
2. Container runtime has necessary permissions
3. Network connectivity between services
4. Storage has sufficient free space
5. GPU drivers installed (if using GPU)
