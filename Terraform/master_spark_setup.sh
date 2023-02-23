echo "____________________________MASTER SPARK SETUP________________________________"
# Install the java and spark to the machine 
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
# sudo echo "SPARK_LOCAL_IP=${output.spark_master_private_ip}" >> spark-env.sh
# sudo echo "SPARK_MASTER_HOST=${output.spark_master_public_dns}" >> spark-env.sh
# sudo echo "SPARK_WORKER_HOST=${output.spark_master_public_dns}" >> spark-env.sh
# cd ..
# ./sbin/start-master.sh
# echo "spark://${output.spark_master_public_dns}:7077" | ./sbin/start-worker.sh
