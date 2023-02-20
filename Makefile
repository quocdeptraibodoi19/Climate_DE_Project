init:
	terraform -chdir=./Terraform init

up:
	terraform -chdir=./Terraform apply

down:
	rm private_key.pem && terraform -chdir=./Terraform destroy 

inspect-airflow:
	terraform -chdir=./Terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -i "private_key.pem" ubuntu@$$(terraform -chdir=./Terraform output -raw airflow_public_dns) 