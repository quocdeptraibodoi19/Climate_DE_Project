variable "region" {
  description = "The region of the whole AWS web services"
  type = string
  default = "ap-northeast-1"
}

variable "airflow_ec2_instance_type" {
    description = "The instance type of the EC2 machines to create the Airflow"
    type = string
    default = "m4.xlarge"
}

variable "spark_ec2_instance_type" {
    description = "The instance type of the EC2 machines to create Spark Cluster"
    type = string
    default = "t3.medium"
}

variable "airlfow_machine_name"{
    description = "The instance type of the EC2 machine to host airflow application"
    type = string
    default = "airflow-node"
}

variable "master_spark_machine_name" {
    description = "The instance type of the EC2 machine to host master node of the spark cluster"
    type = string
    default = "master-spark-node"
}

variable "worker_spark_machine_name" {
    description = "The instance type of the EC2 machine to host worker node of spark cluster"
    type = string
    default = "worker-spark-node"
}