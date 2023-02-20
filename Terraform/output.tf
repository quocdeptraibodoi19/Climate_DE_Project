output "private_key" {
  description = "EC2 private key."
  value       = tls_private_key.custom-key.private_key_pem
  sensitive   = true
}

output "public_key" {
  description = "EC2 public key."
  value       = tls_private_key.custom-key.public_key_openssh
}

output "airflow_public_dns" {
    description = "EC2 airflow machine public DNS"
    value = aws_instance.airflow_machine.public_dns
}