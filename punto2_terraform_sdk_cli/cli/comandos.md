# Comandos AWS CLI - Punto 2

## Perfil utilizado

```bash
aws sts get-caller-identity --profile user_cli

## Crear VPC

VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.2.0.0/16 \
  --region us-east-2 \
  --profile user_cli \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=taller-punto2-cli-vpc}]' \
  --query 'Vpc.VpcId' \
  --output text)

  ## Obtener zonas de disponibilidad

  AZ1=$(aws ec2 describe-availability-zones \
  --region us-east-2 \
  --profile user_cli \
  --query 'AvailabilityZones[0].ZoneName' \
  --output text)

AZ2=$(aws ec2 describe-availability-zones \
  --region us-east-2 \
  --profile user_cli \
  --query 'AvailabilityZones[1].ZoneName' \
  --output text)

## Crear subredes

SUBNET1_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.2.1.0/24 \
  --availability-zone $AZ1 \
  --region us-east-2 \
  --profile user_cli \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=taller-cli-subnet-1}]' \
  --query 'Subnet.SubnetId' \
  --output text)

SUBNET2_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.2.2.0/24 \
  --availability-zone $AZ2 \
  --region us-east-2 \
  --profile user_cli \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=taller-cli-subnet-2}]' \
  --query 'Subnet.SubnetId' \
  --output text)

  ## Crear Security Group

  SG_ID=$(aws ec2 create-security-group \
  --group-name taller-cli-sg \
  --description "Security Group Punto 2 CLI" \
  --vpc-id $VPC_ID \
  --region us-east-2 \
  --profile user_cli \
  --query 'GroupId' \
  --output text)

aws ec2 create-tags \
  --resources $SG_ID \
  --tags Key=Name,Value=taller-cli-sg \
  --region us-east-2 \
  --profile user_cli

## Crear bucket S3

ACCOUNT_ID=$(aws sts get-caller-identity \
  --profile user_cli \
  --query Account \
  --output text)

BUCKET_NAME="taller-aws-p2-${ACCOUNT_ID}-cli"

aws s3api create-bucket \
  --bucket $BUCKET_NAME \
  --region us-east-2 \
  --create-bucket-configuration LocationConstraint=us-east-2 \
  --profile user_cli

## Crear EC2

AMI_ID=$(aws ec2 describe-images \
  --owners amazon \
  --region us-east-2 \
  --profile user_cli \
  --filters \
    "Name=name,Values=al2023-ami-2023.*-x86_64" \
    "Name=virtualization-type,Values=hvm" \
  --query 'Images | sort_by(@,&CreationDate)[-1].ImageId' \
  --output text)

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.micro \
  --subnet-id $SUBNET1_ID \
  --security-group-ids $SG_ID \
  --region us-east-2 \
  --profile user_cli \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=taller-punto2-cli-ec2}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

aws ec2 wait instance-running \
  --instance-ids $INSTANCE_ID \
  --region us-east-2 \
  --profile user_cli

## Crear DB Subnet Group

DB_SUBNET_GROUP="taller-punto2-cli-db-subnet"

aws rds create-db-subnet-group \
  --db-subnet-group-name $DB_SUBNET_GROUP \
  --db-subnet-group-description "DB Subnet Group Punto 2 CLI" \
  --subnet-ids $SUBNET1_ID $SUBNET2_ID \
  --region us-east-2 \
  --profile user_cli

## Crear RDS con contraseña administrada por Secrets Manager

DB_IDENTIFIER="taller-punto2-cli-rds"

aws rds create-db-instance \
  --db-instance-identifier $DB_IDENTIFIER \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --allocated-storage 20 \
  --storage-type gp3 \
  --master-username adminaws \
  --manage-master-user-password \
  --db-subnet-group-name $DB_SUBNET_GROUP \
  --vpc-security-group-ids $SG_ID \
  --no-publicly-accessible \
  --backup-retention-period 0 \
  --no-deletion-protection \
  --region us-east-2 \
  --profile user_cli

aws rds wait db-instance-available \
  --db-instance-identifier $DB_IDENTIFIER \
  --region us-east-2 \
  --profile user_cli


## Eliminación

aws rds delete-db-instance \
  --db-instance-identifier $DB_IDENTIFIER \
  --skip-final-snapshot \
  --delete-automated-backups \
  --region us-east-2 \
  --profile user_cli

aws rds wait db-instance-deleted \
  --db-instance-identifier $DB_IDENTIFIER \
  --region us-east-2 \
  --profile user_cli

aws rds delete-db-subnet-group \
  --db-subnet-group-name $DB_SUBNET_GROUP \
  --region us-east-2 \
  --profile user_cli

aws ec2 terminate-instances \
  --instance-ids $INSTANCE_ID \
  --region us-east-2 \
  --profile user_cli

aws ec2 wait instance-terminated \
  --instance-ids $INSTANCE_ID \
  --region us-east-2 \
  --profile user_cli

aws ec2 delete-security-group \
  --group-id $SG_ID \
  --region us-east-2 \
  --profile user_cli

aws ec2 delete-subnet \
  --subnet-id $SUBNET1_ID \
  --region us-east-2 \
  --profile user_cli

aws ec2 delete-subnet \
  --subnet-id $SUBNET2_ID \
  --region us-east-2 \
  --profile user_cli

aws ec2 delete-vpc \
  --vpc-id $VPC_ID \
  --region us-east-2 \
  --profile user_cli

aws s3 rb s3://$BUCKET_NAME \
  --force \
  --profile user_cli