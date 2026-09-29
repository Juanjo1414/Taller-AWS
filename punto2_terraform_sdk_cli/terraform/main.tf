# Identidad AWS actual
data "aws_caller_identity" "current" {}

# Zonas de disponibilidad disponibles en Ohio
data "aws_availability_zones" "available" {
  state = "available"
}

# -------------------------
# VPC
# -------------------------

resource "aws_vpc" "taller" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "taller-punto2-vpc"
  }
}

# Subnet para EC2
resource "aws_subnet" "subnet_1" {
  vpc_id                  = aws_vpc.taller.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false

  tags = {
    Name = "taller-punto2-subnet-1"
  }
}

# Segunda subnet requerida por RDS
resource "aws_subnet" "subnet_2" {
  vpc_id            = aws_vpc.taller.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name = "taller-punto2-subnet-2"
  }
}

# -------------------------
# Security Group
# -------------------------

resource "aws_security_group" "taller" {
  name        = "taller-punto2-sg"
  description = "Security group para EC2 y RDS del taller"
  vpc_id      = aws_vpc.taller.id

  tags = {
    Name = "taller-punto2-sg"
  }
}

# -------------------------
# S3
# -------------------------

resource "aws_s3_bucket" "taller" {
  bucket = "taller-aws-p2-${data.aws_caller_identity.current.account_id}-tf"

  tags = {
    Name = "Taller AWS Punto 2"
  }
}

# -------------------------
# EC2
# -------------------------

data "aws_ami" "amazon_linux" {
  most_recent = true

  owners = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "taller" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.subnet_1.id
  vpc_security_group_ids = [aws_security_group.taller.id]

  tags = {
    Name = "taller-punto2-ec2"
  }
}

# -------------------------
# RDS
# -------------------------

resource "aws_db_subnet_group" "taller" {
  name = "taller-punto2-db-subnet-group"

  subnet_ids = [
    aws_subnet.subnet_1.id,
    aws_subnet.subnet_2.id
  ]

  tags = {
    Name = "taller-punto2-db-subnet-group"
  }
}

resource "aws_db_instance" "taller" {
  identifier = "taller-punto2-rds"

  engine         = "mysql"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = "talleraws"
  username = "adminaws"

  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.taller.name
  vpc_security_group_ids = [aws_security_group.taller.id]

  publicly_accessible = false
  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name = "taller-punto2-rds"
  }
}
