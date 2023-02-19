variable "region" {
  description = "The region of the whole AWS web services"
  type = string
  default = "ap-northeast-1"
}

variable "ec2_instance_type" {
    description = "The instance type of the EC2 machines"
    type = string
    default = "t3.medium"
}

variable "airlfow_machine_name"{
    description = "The instance type of the EC2 machine to host airflow application"
    type = string
    default = "airflow-node"
}
