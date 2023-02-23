#!/bin/bash
echo "____________________________WORKER SPARK SETUP________________________________"
# Install the java and spark to the machine 
cd /home/ubuntu
sudo apt-get update
sudo apt-get install -y openjdk-8-jdk
sudo wget https://dlcdn.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz
sudo tar xvfz spark-3.3.2-bin-hadoop3.tgz
sudo echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' >> ~/.bashrc
sudo echo 'export SPARK_HOME=/home/ubuntu/spark-3.3.2-bin-hadoop3' >> ~/.bashrc
sudo echo 'export PATH=$PATH:$JAVA_HOME/bin' >> ~/.bashrc
source ~/.bashrc
cd ./spark-3.3.2-bin-hadoop3/conf
sudo cp spark-env.sh.template spark-env.sh
sudo echo "SPARK_LOCAL_IP=${terraform -chdir=./Terraform output -raw spark_worker_private_ip}" >> spark-env.sh
sudo echo "SPARK_WORKER_HOST=${terraform -chdir=./Terraform output -raw spark_worker_public_dns}" >> spark-env.sh
cd ..
echo "spark://${terraform -chdir=./Terraform output -raw spark_master_public_dns}:7077" | ./sbin/start-worker.sh
 