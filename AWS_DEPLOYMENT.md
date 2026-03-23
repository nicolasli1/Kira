# AWS Deployment Approach

## Goal

This document describes how to deploy the current local-first payments platform to AWS in a production-oriented way while preserving the same functional flow:

1. Client calls `POST /transfer`
2. API validates `txhash` against the blockchain service
3. API routes the request to the selected vendor adapter
4. API returns the normalized transfer response

## Recommended AWS Architecture

For this project, the most pragmatic AWS target is **Amazon ECS on Fargate**.

Why:

- The application is already containerized
- The operational burden is lower than Kubernetes/EKS
- It maps cleanly to the current service boundaries
- It is a strong fit for a Platform Engineer take-home focused on infrastructure, automation, and observability

## Target Services

- `Amazon ECR`: stores container images
- `Amazon ECS on Fargate`: runs the API and blockchain mock containers
- `Application Load Balancer`: exposes the public API
- `AWS Cloud Map` or `ECS Service Connect`: internal service discovery
- `AWS Secrets Manager`: stores secrets such as `VENDOR_SHARED_SECRET`
- `Amazon CloudWatch Logs`: centralized container logs
- `CloudWatch Container Insights`: ECS and container runtime metrics
- `Amazon Managed Service for Prometheus` or self-managed Prometheus on ECS: application metrics
- `AWS CloudTrail`: infrastructure and API audit trail
- `AWS Certificate Manager` and `Route 53`: HTTPS and DNS
- `AWS WAF`: optional protection for the public API

## Environment Layout

## Networking

- One VPC
- Two public subnets for the Application Load Balancer
- Two private subnets for ECS tasks
- Security groups separating public and internal traffic
- NAT Gateway if private tasks need outbound internet access

## Compute

- One ECS cluster
- One ECS service for `payments-api`
- One ECS service for `payments-blockchain`
- Optionally, a separate ECS service for Prometheus if you do not use Amazon Managed Service for Prometheus

## Public and Internal Exposure

- `payments-api` is public through the ALB
- `payments-blockchain` is internal only
- Prometheus is internal only unless there is an explicit reason to expose it

## Request Flow in AWS

1. Client sends `POST /transfer` to the ALB HTTPS endpoint
2. ALB forwards the request to the `payments-api` ECS service
3. API resolves the blockchain service over internal discovery
4. API validates the `txhash`
5. API routes the request to the vendor adapter
6. API emits logs and metrics
7. Response is returned to the client through the ALB

## Infrastructure Mapping from the Current Repo

## Current Local Component

- Docker image: `payments-api`
- Docker image: `payments-blockchain`
- Terraform with Docker provider
- Prometheus local container
- GitHub Actions using local Docker deployment

## AWS Equivalent

- `payments-api` image -> `Amazon ECR`
- `payments-blockchain` image -> `Amazon ECR`
- Docker Terraform resources -> AWS Terraform resources
- Local Prometheus -> Amazon Managed Service for Prometheus or ECS-based Prometheus
- Local deployment job -> deploy to ECS through Terraform

## Terraform Modules to Create

If you want to evolve this repository cleanly, split AWS Terraform into modules such as:

- `network`
- `ecr`
- `ecs-cluster`
- `ecs-service-api`
- `ecs-service-blockchain`
- `alb`
- `secrets`
- `observability`
- `iam`

Example structure:

```text
terraform/aws/
  main.tf
  variables.tf
  outputs.tf
  providers.tf
  modules/
    network/
    ecr/
    alb/
    ecs-cluster/
    ecs-service-api/
    ecs-service-blockchain/
    secrets/
    observability/
    iam/
```

## Container Strategy

## Images

- Build `payments-api` and `payments-blockchain` in CI
- Tag images with commit SHA
- Push to ECR

Example image tags:

- `payments-api:<git-sha>`
- `payments-blockchain:<git-sha>`

## ECS Task Definitions

### API task

- Container port `8000`
- Environment variable for blockchain internal URL
- Secret injection from Secrets Manager
- `awslogs` log driver to CloudWatch Logs
- Health check aligned to `/health`

### Blockchain task

- Container port `8001`
- Internal-only service
- `awslogs` log driver
- Health check aligned to `/health`

## Secrets Management

Replace local mocked secrets with `AWS Secrets Manager`.

Recommended approach:

- Store `VENDOR_SHARED_SECRET` in Secrets Manager
- Inject the secret into the ECS task definition
- Restrict access with a task execution role and least privilege IAM policy

This maps directly to the current pattern, where the app reads configuration from environment variables.

## Observability in AWS

## Logs

- Send all container logs to CloudWatch Logs
- Keep the current JSON log structure from the application
- Add retention policies to log groups

## Metrics

Keep the current application metrics:

- `transfer_requests_total{vendor,outcome}`
- `vendor_request_latency_seconds{vendor}`
- `txhash_verifications_total{status}`

Recommended options:

### Option A: Amazon Managed Service for Prometheus

- Best for production-readiness
- Keeps a Prometheus-compatible model
- Avoids managing a Prometheus server directly

### Option B: Prometheus container on ECS

- Closer to the current repo
- Easier migration from local Docker
- More operational overhead than AMP

## Alerts

Suggested alerts:

- High API 5xx rate
- High transfer failure rate
- High txhash verification failure rate
- Increased vendor latency
- ECS task restarts
- ALB unhealthy targets

## DORA Metrics in AWS

The current repo already generates a DORA artifact in CI. In AWS, extend that approach like this:

- `Deployment frequency`: count successful production deployments
- `Lead time`: commit timestamp to successful ECS deployment
- `Change failure rate`: ratio of failed deploys or failed smoke tests to total deploys
- `MTTR`: time from failed deployment or incident to next successful recovery deployment

Implementation options:

- Keep GitHub Actions as the source of deployment truth
- Store deployment metadata in S3, CloudWatch, or a warehouse
- Correlate commit SHA, deploy timestamp, and workflow result

## CI/CD Pipeline for AWS

The GitHub Actions workflow should evolve into these stages:

1. `terraform-check`
2. `app-tests`
3. `build-and-push-images`
4. `deploy-dev`
5. `post-deploy-smoke-tests`
6. `collect-dora-evidence`
7. `destroy-ephemeral` or `promote-prod`

## Example AWS CI/CD Flow

1. Run `pytest`
2. Run `terraform fmt -check`, `validate`, and `plan`
3. Build Docker images
4. Authenticate to AWS and push images to ECR
5. Pass image tags into Terraform
6. Run `terraform apply`
7. Wait for ECS service health and ALB health
8. Run smoke tests against the ALB URL
9. Validate metrics and logs
10. Publish DORA and runtime artifacts

## Smoke Tests to Keep

These checks should stay in the pipeline:

- valid `txhash` with `vendorA` returns `success`
- invalid `txhash` returns `404`
- `vendorB` returns `pending`
- unsupported vendor returns `400`
- `/health` returns `200`
- `/metrics` exposes key metrics

## Security and SOC 2 Alignment in AWS

## Access Control

- IAM roles for GitHub deployment identity and ECS tasks
- Least-privilege policies
- Protected branches and required approvals in GitHub
- Separate roles for deploy, runtime, and read-only observability

## Data Security

- HTTPS with ACM certificates and ALB
- Secrets in Secrets Manager
- KMS encryption for secrets, logs, and relevant storage
- Private subnets for ECS tasks

## Audit Logging

- CloudTrail for API-level and infrastructure-level actions
- CloudWatch Logs for application events
- Deployment artifacts from GitHub Actions

## Incident Response Readiness

- ECS health checks and auto-replacement of unhealthy tasks
- CloudWatch alarms
- Runbooks for rollback and restart
- Deployment smoke tests before considering the release healthy

## Recommended Rollout Strategy

## Phase 1

- Move images to ECR
- Deploy API and blockchain to ECS Fargate
- Add ALB and Secrets Manager
- Send logs to CloudWatch

## Phase 2

- Add managed Prometheus or production-grade metrics pipeline
- Add alarms and dashboards
- Separate `dev` and `prod` environments

## Phase 3

- Add blue/green or canary deployment strategy
- Add WAF and tighter security controls
- Add vulnerability scanning, SBOM, and image-signing

## Why ECS Fargate Instead of EKS

For this use case, ECS Fargate is usually the better tradeoff:

- less cluster management
- faster delivery
- simpler IAM and operational model
- enough flexibility for a small service-oriented platform

EKS would make more sense if:

- you already run Kubernetes organization-wide
- you need advanced multi-service platform patterns
- you need stronger portability across clusters/providers

## Suggested Next Step for This Repo

The most practical next step is:

1. create a new AWS Terraform stack under `terraform/aws`
2. create ECR repositories
3. push the current images from GitHub Actions
4. deploy both services to ECS Fargate
5. expose only the API through an ALB
6. move the shared secret to Secrets Manager
7. keep the same smoke tests, but point them to the ALB URL

## Official AWS References

- ECS Fargate: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started-fargate.html
- ECS service discovery: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html
- ECS secrets from Secrets Manager: https://docs.aws.amazon.com/AmazonECS/latest/userguide/secrets-envvar-secrets-manager.html
- ECS logs to CloudWatch: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_awslogs.html
- Application Load Balancer: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancer-getting-started.html
- Amazon ECR: https://docs.aws.amazon.com/AmazonECR/latest/userguide/Registries.html
- CloudWatch Container Insights for ECS: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/deploy-container-insights-ECS-cluster.html
- Amazon Managed Service for Prometheus: https://docs.aws.amazon.com/prometheus/latest/userguide/what-is-Amazon-Managed-Service-Prometheus.html
- AWS CloudTrail: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html
