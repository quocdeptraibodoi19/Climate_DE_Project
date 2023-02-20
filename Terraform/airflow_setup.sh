#!/bin/bash

echo "-------------------------START SETUP---------------------------"
sudo apt-get -y update
sudo snap install docker
echo 'Clone git repo to EC2'
cd /home/ubuntu && git clone "https://github.com/quocdeptraibodoi19/Climate_DE_Project.git" 
sudo chmod 777 ./Climate_DE_Project
cd Climate_DE_Project
sudo mkdir -p logs dags
mv ./ETL_Process/Airflow_Custom_Operators.py ./dags
mv ./ETL_Process/airflow_S3_load_Script.py ./dags
mv ./ETL_Process/Spark_integrate_script.py ./dags
mv ./ETL_Process/Spark_process_script.py ./dags
sudo apt-get -y install docker-compose
docker-compose up

