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
sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
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
sudo echo "export Spark_Con=spark://${aws_instance.master_spark_machine.public_dns}:7077" >> /home/ubuntu/.bashrc
source /home/ubuntu/.bashrc
sudo docker compose up
