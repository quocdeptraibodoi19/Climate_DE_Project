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

output "S3_Bucket" {
    description = "The S3 bucket name"
    value = aws_s3_bucket.climate_bucket.bucket
}

output "city_db_source_host" {
  description = "RDS City Database Host"
  value = aws_db_instance.city_db.endpoint
}

output "country_db_source_host" {
  description = "RDS Country Database Host"
  value = aws_db_instance.country_db.endpoint
}

output "global_db_source_host" {
  description = "RDS Global Database Host"
  value = aws_db_instance.global_db.endpoint
}

output "rds_username" {
  description = "The username of rds"
  value = aws_db_instance.city_db.username
}

output "rds_password" {
  description = "The password of rds"
  value = aws_db_instance.city_db.password
  sensitive = true
}

output "redshift_cluster_endpoint" {
  value = aws_redshift_cluster.climate_cluster.endpoint
}

output "redshift_cluster_dns" {
  value = aws_redshift_cluster.climate_cluster.dns_name
}

output "redshift_cluster_username" {
  value = aws_redshift_cluster.climate_cluster.master_username
}

output "redshift_cluster_password" {
  value = aws_redshift_cluster.climate_cluster.master_password
  sensitive = true
}