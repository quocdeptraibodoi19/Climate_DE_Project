#!/bin/bash
echo "____________________________MASTER SPARK SETUP________________________________"
# Install the java and spark to the machine 
cd /home/ubuntu
MASTER_SPARK_PUBLIC_DNS=$(sudo cat /home/ubuntu/public_dns.txt)
sudo apt-get update
sudo apt-get install -y openjdk-8-jdk
sudo wget https://dlcdn.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz
sudo tar xvfz spark-3.3.2-bin-hadoop3.tgz
sudo echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' >> /home/ubuntu/.bashrc
sudo echo 'export SPARK_HOME=/home/ubuntu/spark-3.3.2-bin-hadoop3' >> /home/ubuntu/.bashrc
sudo echo 'export PATH=$PATH:$JAVA_HOME/bin' >> /home/ubuntu/.bashrc
source /home/ubuntu/.bashrc
cd ./spark-3.3.2-bin-hadoop3/conf
sudo cp spark-env.sh.template spark-env.sh
sudo su
sudo echo "export SPARK_LOCAL_IP=${aws_instance.master_spark_machine.private_ip}" >> spark-env.sh
sudo echo "export SPARK_MASTER_HOST=$MASTER_SPARK_PUBLIC_DNS" >> spark-env.sh
sudo echo "export SPARK_WORKER_HOST=${aws_instance.master_spark_machine.public_dns}" >> spark-env.sh
cd ..
./sbin/start-master.sh
echo "spark://${aws_instance.master_spark_machine.public_dns}:7077" | ./sbin/start-worker.sh
