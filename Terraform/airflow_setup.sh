#!/bin/bash

echo "-------------------------START SETUP---------------------------"
sudo apt-get -y install \
ca-certificates \
curl \
gnupg \
lsb-release

sudo apt -y install unzip

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get -y update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin openjdk-8-jdk
sudo chmod 666 /var/run/docker.sock
echo 'Clone git repo to EC2'
cd /home/ubuntu && git clone "https://github.com/quocdeptraibodoi19/Climate_DE_Project.git" 
sudo chmod 777 ./Climate_DE_Project
cd Climate_DE_Project
sudo mkdir -p logs dags
sudo chmod 777 ./logs
sudo chmod 777 ./dags
mv ./ETL_Process/Airflow_Custom_Operators.py ./dags
mv ./ETL_Process/airflow_S3_load_Script.py ./dags
mv ./ETL_Process/Spark_integrate_script.py ./dags
mv ./ETL_Process/Spark_process_script.py ./dags

spark_host="${spark_host}"
Spark_Con=spark://$spark_host:7077

rds_username="${rds_username}"
rds_password="${rds_password}"

rds_city_hostname="${rds_city_hostname}"
MySQL_Con_City=mysql://$rds_username:$rds_password@$rds_city_hostname/"${rds_city_schema}"

rds_country_hostname="${rds_country_hostname}"
MySQL_Con_Country=mysql://$rds_username:$rds_password@$rds_country_hostname/"${rds_country_schema}"

rds_global_hostname="${rds_global_hostname}"
MySQL_Con_Global=mysql://$rds_username:$rds_password@$rds_global_hostname/"${rds_global_schema}"

aws_access_key="${aws_access_key}"
aws_secret_key="${aws_secret_key}"
s3_bucket_name="${s3_bucket_name}"
S3_Con=s3://$aws_access_key:$aws_access_key?region_name=ap-northeast-1

local_host_name=$(curl -s http://169.254.169.254/latest/meta-data/local-hostname)

sudo touch env
# This is just for checking
sudo echo "Spark_Con=$Spark_Con" >> env
sudo echo "MySQL_Con_City=$MySQL_Con_City" >> env
sudo echo "MySQL_Con_Country=$MySQL_Con_Country" >> env
sudo echo "MySQL_Con_Global=$MySQL_Con_Global" >> env
sudo echo "S3_Con=$S3_Con" >> env
sudo echo "local_host_name=$local_host_name" >> env

# sudo docker compose --env-file env up --build -d
# If we go for the way to add the airflow connection in the env variable -> this will not be showned in the airflow UI
# This is the solution
