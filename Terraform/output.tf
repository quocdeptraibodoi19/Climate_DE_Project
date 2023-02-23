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

output "spark_master_public_dns" {
  description = "EC2 spark master machine public DNS"
  value = aws_instance.master_spark_machine.public_dns
}

output "spark_master_private_ip" {
  description = "EC2 spark master machine private IP"
  value = aws_instance.master_spark_machine.private_ip
}

output "spark_worker_public_dns" {
  description = "EC2 spark worker machine public DNS"
  value = aws_instance.worker_spark_machine.public_dns
}

output "spark_worker_private_ip" {
  description = "EC2 spark worker machine private IP"
  value = aws_instance.worker_spark_machine.private_ip
}
