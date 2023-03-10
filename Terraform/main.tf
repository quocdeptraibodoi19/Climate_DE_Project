terraform {
    required_providers{
        aws = {
            source = "hashicorp/aws"
            version = "~> 4.0"
        }
    } 
    required_version = ">= 1.2.0" 
}

# This requires you to have AWS CLI installed in your system 
# Without it, you have to specify the access key or token in the file or stuff like that
provider "aws" {
    region = var.region
    profile = "default"
}

data "aws_ami" "ubuntu"{
    most_recent = true
    filter  {
        name = "name"
        values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-20230208"]
    }
    filter {
        name = "virtualization-type"
        values = ["hvm"]
    }
    filter {
        name = "root-device-type"
        values = ["ebs"]
    }
    owners =  ["099720109477"]
}

# Create the key pair for your ec2 instances
# Notice: This private key is directly stored in the state file in the current Terraform directory.
resource "tls_private_key" "custom-key" {
    algorithm = "RSA"
    rsa_bits = 4096
}

resource "aws_key_pair" "climate-key-pair" {
    key_name = "climate-key-pair"
    public_key = tls_private_key.custom-key.public_key_openssh
}

# Security group
# The difference between Name in tag and name argument is that name outside the tag specify
# the identifier of the security group (which has to be different)
# name in the tag specifies the further information of the security group
resource "aws_security_group" "climate_security_group" {
    description = "This security group is used to grant access the set of our ec2 machines"
    name = "climate_security_group"
    ingress {
        description = "All trafic can access this for the learning goal (inbound rule)"
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
    
    egress {
        description =  "Accept all traffic (outbound rule)"
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
    tags = {
      Name = "climate_security_group"
    }
}

# Create role policy

# Retrieve the ec2 assume role from the the aws_iam_policy_document source
# One aws service needs to be granted access in order to manipulate things on other aws services
# This assume service is required for trusted entity (ec2, lamda, aws account,...) to assume 
# or have the permissions to access other 
# In this case this is ec2
data "aws_iam_policy_document" "ec2_instance_assume_role_policy" {
    statement {
        actions = ["sts:AssumeRole"]
        principals {
            type = "Service"
            identifiers = ["ec2.amazonaws.com"]
        }
    }
}

# I just want to create this by my own but we can still not do this
data "aws_iam_policy_document" "AWS_RDS_full_access_role_policy" {
    version = "2012-10-17"
    statement {
        actions = [
                "rds:*",
                "application-autoscaling:DeleteScalingPolicy",
                "application-autoscaling:DeregisterScalableTarget",
                "application-autoscaling:DescribeScalableTargets",
                "application-autoscaling:DescribeScalingActivities",
                "application-autoscaling:DescribeScalingPolicies",
                "application-autoscaling:PutScalingPolicy",
                "application-autoscaling:RegisterScalableTarget",
                "cloudwatch:DescribeAlarms",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:PutMetricAlarm",
                "cloudwatch:DeleteAlarms",
                "ec2:DescribeAccountAttributes",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeCoipPools",
                "ec2:DescribeInternetGateways",
                "ec2:DescribeLocalGatewayRouteTablePermissions",
                "ec2:DescribeLocalGatewayRouteTables",
                "ec2:DescribeLocalGatewayRouteTableVpcAssociations",
                "ec2:DescribeLocalGateways",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSubnets",
                "ec2:DescribeVpcAttribute",
                "ec2:DescribeVpcs",
                "ec2:GetCoipPoolUsage",
                "sns:ListSubscriptions",
                "sns:ListTopics",
                "sns:Publish",
                "logs:DescribeLogStreams",
                "logs:GetLogEvents",
                "outposts:GetOutpostInstanceTypes",
                "devops-guru:GetResourceCollection"
            ]
            resources = ["*"]
    }
    statement {
        actions = ["pi:*"]
        resources = ["arn:aws:pi:*:*:metrics/rds/*"]
    }
    statement {
        actions = ["iam:CreateServiceLinkedRole"]
        resources = ["*"]
        condition {
            test = "StringLike"
            variable = "iam:AWSServiceName"
            values = ["rds.amazonaws.com","rds.application-autoscaling.amazonaws.com"]
        }
    }
}

resource "aws_iam_policy" "AWS_RDS_full_access_role_policy" {
    name = "AWS_RDS_full_access_role_policy"
    policy = data.aws_iam_policy_document.AWS_RDS_full_access_role_policy.json
}

resource "aws_iam_role" "role" {
    name = "climate_role"
    assume_role_policy = data.aws_iam_policy_document.ec2_instance_assume_role_policy.json
    managed_policy_arns = [
        aws_iam_policy.AWS_RDS_full_access_role_policy.arn,
        "arn:aws:iam::aws:policy/AmazonS3FullAccess",
        "arn:aws:iam::aws:policy/AmazonRedshiftFullAccess"
    ]
}

#Create aws role
resource "aws_iam_instance_profile" "climate_iam_profile" {
    name = "climate_iam_profile"
    role = aws_iam_role.role.name
}

# Create IAM user
resource "aws_iam_user" "climate_temperature_user" {
    name = "climate_temperature_user"
}

resource "aws_iam_access_key" "climate_access_key" {
    user = aws_iam_user.climate_temperature_user.name
}

resource "aws_iam_user_policy_attachment" "ec2" {
    user = aws_iam_user.climate_temperature_user.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
}

resource "aws_iam_user_policy_attachment" "rds" {
    user = aws_iam_user.climate_temperature_user.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

resource "aws_iam_user_policy_attachment" "redshift" {
    user = aws_iam_user.climate_temperature_user.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonRedshiftFullAccess"
}

resource "aws_iam_user_policy_attachment" "s3" {
    user = aws_iam_user.climate_temperature_user.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# Create the s3 bucket - a storage region
resource "aws_s3_bucket" "climate_bucket" {
    bucket = "temperature-project-bucket1"
    acl = "private"
    force_destroy = true
}

resource "aws_s3_object" "holistic_country_object" {
    bucket = aws_s3_bucket.climate_bucket.bucket
    key = "Holistics_Country_Format/HolisticsCountryFormat_UTF8.csv"
    source = "../Data_Sources/HolisticsCountryFormat_UTF8.csv"
    content_type = "text/csv"
}

# Create the redshift cluster and its database:
resource "aws_redshift_cluster" "climate_cluster" {
    cluster_identifier = "climate-cluster"
    database_name = "climate_temperature_db"
    master_username = "awsuser"
    master_password = "Quoc12345678"
    node_type = "dc2.large"
    cluster_type = "multi-node"
    number_of_nodes = 1
    publicly_accessible = true
    port = 5439
    skip_final_snapshot = true
    iam_roles = [ 
                    "arn:aws:iam::046931263575:role/service-role/AmazonRedshift-CommandsAccessRole-20230212T005741",
                    "arn:aws:iam::046931263575:role/aws-service-role/redshift.amazonaws.com/AWSServiceRoleForRedshift"
                ]
}

resource "aws_redshiftdata_statement" "climate_redshift_setup" {
    cluster_identifier = aws_redshift_cluster.climate_cluster.cluster_identifier
    database = aws_redshift_cluster.climate_cluster.database_name
    db_user = aws_redshift_cluster.climate_cluster.master_username
    sql = file("aws_redshift_setup.sql")
}

# Create the data sources (MySQL RDS Databases) 
resource "aws_db_instance" "city_db" {
    allocated_storage = 20
    identifier = "db-temperature-by-city1"
    engine = "mysql"
    engine_version = "8.0.28"
    instance_class = "db.t3.micro"
    username = "admin"
    password = "12345678"
    max_allocated_storage = 1000
    publicly_accessible = true
    delete_automated_backups = true
    network_type = "IPV4"
    ca_cert_identifier = "rds-ca-2019"
    skip_final_snapshot = true
    final_snapshot_identifier = null
}

resource "aws_db_instance" "country_db" {
    allocated_storage = 20
    identifier = "db-temperature-by-country1"
    engine = "mysql"
    engine_version = "8.0.28"
    instance_class = "db.t3.micro"
    username = "admin"
    password = "12345678"
    max_allocated_storage = 1000
    publicly_accessible = true
    delete_automated_backups = true
    network_type = "IPV4"
    ca_cert_identifier = "rds-ca-2019"
    skip_final_snapshot = true
    final_snapshot_identifier = null
}

resource "aws_db_instance" "global_db" {
    allocated_storage = 20
    identifier = "db-temperature-global1"
    engine = "mysql"
    engine_version = "8.0.28"
    instance_class = "db.t3.micro"
    username = "admin"
    password = "12345678"
    max_allocated_storage = 1000
    publicly_accessible = true
    delete_automated_backups = true
    network_type = "IPV4"
    ca_cert_identifier = "rds-ca-2019"
    skip_final_snapshot = true
    final_snapshot_identifier = null
}

# Create the Spark Cluster from 2 EC2 machines
# For the master node
resource "aws_instance" "master_spark_machine" {
    ami =  data.aws_ami.ubuntu.id
    instance_type = var.spark_ec2_instance_type
    key_name =  aws_key_pair.climate-key-pair.key_name
    tags = {
        Name = var.master_spark_machine_name
    }
    security_groups = [aws_security_group.climate_security_group.name]
    root_block_device {
        delete_on_termination = true
        volume_size = 30
        volume_type = "gp2"
    }
    iam_instance_profile = aws_iam_instance_profile.climate_iam_profile.name
    user_data = file("master_spark_setup.sh")
}

locals {
    spark_master_public_dns = aws_instance.master_spark_machine.public_dns
    spark_host = aws_instance.master_spark_machine.public_dns
    rds_username = aws_db_instance.city_db.username
    rds_password = aws_db_instance.city_db.password
    rds_city_hostname = aws_db_instance.city_db.endpoint
    rds_city_schema = "db_temperature_by_city"
    rds_country_hostname = aws_db_instance.country_db.endpoint
    rds_country_schema = "db_temperature_by_country"
    rds_global_hostname = aws_db_instance.global_db.endpoint
    rds_global_schema = "db_temperature_global"
    aws_access_key = aws_iam_access_key.climate_access_key.id
    aws_secret_key = aws_iam_access_key.climate_access_key.secret
    s3_bucket_name = aws_s3_bucket.climate_bucket.bucket
    redshift_cluster_username = aws_redshift_cluster.climate_cluster.master_username
    redshift_cluster_password = aws_redshift_cluster.climate_cluster.master_password
    redshift_cluster_endpoint = aws_redshift_cluster.climate_cluster.endpoint
    redshift_cluster_database = aws_redshift_cluster.climate_cluster.database_name
}

# For the worker node
resource "aws_instance" "worker_spark_machine" {
    ami =  data.aws_ami.ubuntu.id
    instance_type = var.spark_ec2_instance_type
    key_name =  aws_key_pair.climate-key-pair.key_name
    tags = {
        Name = var.worker_spark_machine_name
    }
    security_groups = [aws_security_group.climate_security_group.name]
    root_block_device {
        delete_on_termination = true
        volume_size = 30
        volume_type = "gp2"
    }
    iam_instance_profile = aws_iam_instance_profile.climate_iam_profile.name
    user_data = base64encode(templatefile("worker_spark_setup.sh",{
        spark_master_public_dns = local.spark_master_public_dns
    }))
    depends_on = [
        aws_instance.master_spark_machine
    ]
}

# Create the AWS EC2 instance
resource "aws_instance" "airflow_machine" {
    ami = data.aws_ami.ubuntu.id
    instance_type = var.airflow_ec2_instance_type
    key_name = aws_key_pair.climate-key-pair.key_name
    tags = {
        Name = var.airlfow_machine_name
    }
    security_groups = [aws_security_group.climate_security_group.name]
    root_block_device {
        delete_on_termination = true
        volume_size = 30
        volume_type = "gp2"

    }
    iam_instance_profile = aws_iam_instance_profile.climate_iam_profile.name
    user_data = base64encode(templatefile("airflow_setup.sh",{
        spark_host = local.spark_host,
        rds_username = local.rds_username,
        rds_password = local.rds_password,
        rds_city_hostname = local.rds_city_hostname,
        rds_country_hostname = local.rds_country_hostname,
        rds_global_hostname = local.rds_global_hostname,
        rds_city_schema = local.rds_city_schema,
        rds_country_schema = local.rds_country_schema,
        rds_global_schema = local.rds_global_schema,
        aws_access_key = local.aws_access_key,
        aws_secret_key = local.aws_secret_key,
        s3_bucket_name = local.s3_bucket_name,
        redshift_cluster_endpoint = local.redshift_cluster_endpoint,
        redshift_cluster_password = local.redshift_cluster_password,
        redshift_cluster_username = local.redshift_cluster_username,
        redshift_cluster_database = local.redshift_cluster_database,
    }))
    depends_on = [
        aws_instance.master_spark_machine,
        aws_instance.worker_spark_machine,
        aws_s3_bucket.climate_bucket,
        aws_db_instance.city_db,
        aws_db_instance.country_db,
        aws_db_instance.global_db,
        aws_redshift_cluster.climate_cluster,
    ]
}
