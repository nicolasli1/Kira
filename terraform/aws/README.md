# AWS Terraform Skeleton

This folder contains the initial Terraform skeleton for a real AWS deployment path.

It currently provisions:

- VPC
- public subnets
- internet gateway and public route table
- ECR repositories for API and blockchain images
- CloudWatch log groups
- Secrets Manager secret
- security groups
- ECS cluster
- Application Load Balancer and target group

It does **not** yet provision:

- ECS task definitions
- ECS services
- IAM roles and policies
- private subnets and NAT
- Route 53 and ACM
- Amazon Managed Service for Prometheus

This is intentional: the goal is to create a clear starting point without breaking the current local Terraform stack in `terraform/`.

Suggested next implementation steps:

1. add IAM roles for ECS task execution
2. add ECS task definitions for API and blockchain
3. add ECS services
4. add service discovery for the blockchain service
5. add HTTPS and domain management
