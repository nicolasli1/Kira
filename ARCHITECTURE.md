# Architecture

## Overview

The solution is a local-first payments platform skeleton designed around four concerns:

1. `payments-api`: receives `POST /transfer`, validates the `txhash`, routes to a vendor adapter, and emits metrics/logs.
2. `mock-blockchain`: isolated mock service used for txhash confirmation.
3. `Prometheus`: collects metrics from the API.
4. `Terraform + GitHub Actions`: provisions the stack and enforces deployment tests.

## Request Flow

1. Client submits:

```json
{
  "amount": 100,
  "vendor": "vendorA",
  "txhash": "0x123..."
}
```

2. The API calls the blockchain mock service on `GET /tx/{txhash}`.
3. If the txhash is not confirmed, the API returns `404` with `txhash not found`.
4. If confirmed, the API resolves the vendor implementation from the registry.
5. The selected vendor mock returns a vendor-specific payload.
6. The API returns a normalized response with txhash status and vendor response.

## Extensible Vendor Design

The vendor architecture uses a registry plus adapter classes:

- Shared contract: [app/vendors/base.py](/workspaces/test/app/vendors/base.py)
- Active vendor adapters: [app/vendors/vendor_a.py](/workspaces/test/app/vendors/vendor_a.py), [app/vendors/vendor_b.py](/workspaces/test/app/vendors/vendor_b.py)
- Registration point: [app/vendor_registry.py](/workspaces/test/app/vendor_registry.py)

To add `vendorC`, only two changes are required:

1. Implement the adapter class.
2. Register it in the vendor registry.

The request handler and infrastructure do not need redesign because they depend on the abstract vendor contract, not on vendor-specific branching logic.

An example future adapter already exists in [app/vendors/vendor_c.py](/workspaces/test/app/vendors/vendor_c.py).

## Infrastructure Design

Terraform provisions the local runtime with the Docker provider:

- Compute: Docker containers for API, blockchain mock, and Prometheus.
- Networking: isolated Docker network `payments-network`.
- Secrets: sensitive Terraform variable `vendor_shared_secret` injected into the API container as a mocked local secret-management pattern.
- Health model: API and blockchain services expose `/health`.

The CI pipeline intentionally uses raw `docker build` and `docker run` commands instead of Docker Compose, matching the requested delivery style.

## Observability

The API exposes Prometheus metrics at `/metrics`:

- `transfer_requests_total{vendor,outcome}`
- `vendor_request_latency_seconds{vendor}`
- `txhash_verifications_total{status}`

This supports:

- Requests per vendor
- Latency per vendor
- Success and failure rates
- Txhash confirmation counts

Application logs are JSON-formatted and designed for ingestion into a centralized log platform in a production deployment.

## DORA Metrics Approach

GitHub Actions is the control point for deployment telemetry:

- Deployment frequency: count successful workflow runs that reach the deployment step.
- Lead time for changes: derive from commit timestamp to deployment completion timestamp.
- Change failure rate: ratio of failed deployment-test runs to total deployment attempts.
- MTTR: time from a failed deployment run to the next successful recovery run.

The workflow publishes a `dora-metrics.json` artifact as a simple evidence trail. In a production system, the same workflow events would be shipped to CloudWatch, Datadog, or a warehouse for dashboards and alerting.

## Automation

The CI/CD pipeline performs:

1. Unit tests
2. Container builds
3. Local deployment with `docker run`
4. Post-deploy API validation
5. DORA artifact generation

Any failed deployment test fails the pipeline, which matches the requirement that deployment fails if smoke tests fail.
