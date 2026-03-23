output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id,
  ]
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "api_ecr_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "blockchain_ecr_repository_url" {
  value = aws_ecr_repository.blockchain.repository_url
}

output "alb_dns_name" {
  value = aws_lb.api.dns_name
}

output "vendor_shared_secret_arn" {
  value     = aws_secretsmanager_secret.vendor_shared_secret.arn
  sensitive = true
}
