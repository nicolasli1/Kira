# SOC 2 Alignment

## Access Control

- CI/CD execution is centralized in GitHub Actions, which supports branch protection and approval workflows.
- Runtime access can be restricted through Docker host access and, in a cloud deployment, mapped directly to IAM roles and least-privilege service accounts.
- Application-level vendor selection is constrained by a fixed registry, reducing arbitrary downstream invocation risk.
- The architecture is compatible with RBAC at the orchestration layer if migrated from local Docker to ECS or Kubernetes.

## Data Security

- Secrets are not hardcoded into application logic. The API reads secrets from environment variables injected by Terraform as a mocked local equivalent of SSM or Secrets Manager.
- In production, the same pattern maps directly to AWS Secrets Manager or SSM Parameter Store with KMS encryption.
- TLS termination is not implemented locally, but the design expects HTTPS termination at the ingress or load balancer layer.
- Containerized services reduce configuration drift and improve reproducibility.

## Audit Logging

- Every transfer passes through a single API entrypoint, which is the audit boundary.
- Txhash verification is explicit and logged alongside transfer processing events.
- Structured JSON logs make it straightforward to forward events to a SIEM or immutable log store.
- GitHub Actions preserves deployment evidence for change management and release traceability.

## Incident Response Readiness

- Health endpoints support fast detection and recovery automation.
- Prometheus metrics enable alerting on elevated failure rates, txhash validation anomalies, or vendor latency spikes.
- CI post-deploy tests reduce the probability of shipping a broken release.
- DORA metrics provide an operational baseline for failure rate and recovery performance.

## SOC 2 Gaps and Production Next Steps

- Replace local Docker secrets with managed secrets storage and rotation.
- Enforce TLS everywhere, including service-to-service traffic where required.
- Add centralized log retention, alert routing, and on-call workflows.
- Add vulnerability scanning, SBOM generation, and image-signing to the pipeline.
- Add formal backup, disaster recovery, and evidence retention policies.
