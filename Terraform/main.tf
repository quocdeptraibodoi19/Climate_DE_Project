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
resource "aws_instance" "airflow_machine" {
    ami = data.aws_ami.ubuntu.id
    instance_type = var.ec2_instance_type
    key_name = aws_key_pair.climate-key-pair.key_name
    cpu_core_count = 3
    cpu_threads_per_core = 2
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
    user_data = file("airflow_setup.sh")
}

