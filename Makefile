init:
	terraform -chdir=./Terraform init

up:
	terraform -chdir=./Terraform apply

down:
	 terraform -chdir=./Terraform destroy 

inspect-airflow:
	terraform -chdir=./Terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o "IdentitiesOnly yes" -i "private_key.pem" ubuntu@$$(terraform -chdir=./Terraform output -raw airflow_public_dns) && rm private_key.pem

Cloud-airflow:
	terraform -chdir=./Terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o "IdentitiesOnly yes" -i "private_key.pem" ubuntu@$$(terraform -chdir=./Terraform output -raw airflow_public_dns) -N -f -L 8082:$$(terraform -chdir=./Terraform output -raw airflow_public_dns):8080 && rm private_key.pem  