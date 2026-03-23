# Payments API Platform Engineer Take-Home

This repository contains a local-first implementation of a cross-border payments platform skeleton for `USDC -> COP` transfers.

## Stack

- API: FastAPI
- Infra as Code: Terraform
- Containers: Docker
- CI/CD: GitHub Actions
- Observability: Prometheus + structured logs

## Quick Start

```bash
docker build -t payments-api:local -f Dockerfile .
docker build -t payments-blockchain:local -f Dockerfile.blockchain .
docker network create payments-network || true
docker run -d --rm --name payments-blockchain --network payments-network -p 8001:8001 payments-blockchain:local
docker run -d --rm --name payments-api --network payments-network -p 8000:8000 \
  -e BLOCKCHAIN_SERVICE_URL=http://payments-blockchain:8001 \
  -e VENDOR_SHARED_SECRET=mocked-secret \
  payments-api:local
curl -X POST http://localhost:8000/transfer \
  -H "Content-Type: application/json" \
  -d '{"amount":100,"vendor":"vendorA","txhash":"0xabc123confirmed"}'
```

## Test

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r app/requirements.txt
pytest app/tests -q
./scripts/post_deploy_test.sh
```

## Terraform

Terraform provisions the local container stack through the Docker provider:

```bash
cd terraform
terraform init
terraform apply -auto-approve
```

## Docs

- [ARCHITECTURE.md](/workspaces/test/ARCHITECTURE.md)
- [SOC2.md](/workspaces/test/SOC2.md)
