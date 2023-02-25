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
spark_host="${spark_host}"
Spark_Con=spark://$spark_host:7077
sudo touch env
# This is just for checking
sudo echo "Spark_Con=$Spark_Con" >> env
sudo docker compose up --build -d
echo "Adding Spark connection..."
# If we go for the way to add the airflow connection in the env variable -> this will not be showned in the airflow UI
# This is the solution
sudo docker exec -it airflow_webserver airflow connections add "Spark_Con" --conn-uri $Spark_Con
