init:
	terraform -chdir=./Terraform init

up:
	terraform -chdir=./Terraform apply

down:
	 terraform -chdir=./Terraform destroy 

ssh-airflow:
	terraform -chdir=./Terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o "IdentitiesOnly yes" -i "private_key.pem" ubuntu@$$(terraform -chdir=./Terraform output -raw airflow_public_dns) && rm private_key.pem

ssh-master-spark:
		terraform -chdir=./Terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o "IdentitiesOnly yes" -i "private_key.pem" ubuntu@$$(terraform -chdir=./Terraform output -raw spark_master_public_dns) && rm private_key.pem

ssh-worker-spark:
		terraform -chdir=./Terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o "IdentitiesOnly yes" -i "private_key.pem" ubuntu@$$(terraform -chdir=./Terraform output -raw spark_worker_public_dns) && rm private_key.pem

cloud-airflow:
	terraform -chdir=./Terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o "IdentitiesOnly yes" -i "private_key.pem" ubuntu@$$(terraform -chdir=./Terraform output -raw airflow_public_dns) -N -f -L 8082:$$(terraform -chdir=./Terraform output -raw airflow_public_dns):8080 && rm private_key.pem

cloud-spark:
	terraform -chdir=./Terraform output -raw private_key > private_key.pem && chmod 600 private_key.pem && ssh -o "IdentitiesOnly yes" -i "private_key.pem" ubuntu@$$(terraform -chdir=./Terraform output -raw spark_master_public_dns) -N -f -L 8083:$$(terraform -chdir=./Terraform output -raw spark_master_public_dns):8080 && rm private_key.pem
