terraform {
  required_version = ">= 1.6.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

variable "vendor_shared_secret" {
  description = "Mocked local secret injected into the API container."
  type        = string
  sensitive   = true
  default     = "mocked-secret"
}

resource "docker_network" "payments" {
  name = "payments-network"
}

resource "docker_image" "api" {
  name = "payments-api:local"

  build {
    context    = "${path.module}/.."
    dockerfile = "${path.module}/../Dockerfile"
  }
}

resource "docker_image" "blockchain" {
  name = "payments-blockchain:local"

  build {
    context    = "${path.module}/.."
    dockerfile = "${path.module}/../Dockerfile.blockchain"
  }
}

resource "docker_container" "blockchain" {
  name  = "payments-blockchain"
  image = docker_image.blockchain.image_id

  ports {
    internal = 8001
    external = 8001
  }

  networks_advanced {
    name = docker_network.payments.name
  }
}

resource "docker_container" "api" {
  name  = "payments-api"
  image = docker_image.api.image_id

  env = [
    "BLOCKCHAIN_SERVICE_URL=http://payments-blockchain:8001",
    "VENDOR_SHARED_SECRET=${var.vendor_shared_secret}",
  ]

  ports {
    internal = 8000
    external = 8000
  }

  networks_advanced {
    name = docker_network.payments.name
    aliases = ["payments-api"]
  }

  depends_on = [docker_container.blockchain]
}

resource "docker_container" "prometheus" {
  name  = "payments-prometheus"
  image = "prom/prometheus:v3.5.0"

  command = [
    "--config.file=/etc/prometheus/prometheus.yml",
  ]

  ports {
    internal = 9090
    external = 9090
  }

  upload {
    content = file("${path.module}/../monitoring/prometheus.yml")
    file    = "/etc/prometheus/prometheus.yml"
  }

  networks_advanced {
    name = docker_network.payments.name
  }

  depends_on = [docker_container.api]
}
