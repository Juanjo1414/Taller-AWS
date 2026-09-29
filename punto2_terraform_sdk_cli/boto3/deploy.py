import boto3

PROFILE = "user_cli"
REGION = "us-east-2"

session = boto3.Session(
    profile_name=PROFILE,
    region_name=REGION
)

ec2 = session.client("ec2")
rds = session.client("rds")
s3 = session.client("s3")
sts = session.client("sts")

account_id = sts.get_caller_identity()["Account"]

# --------------------------------------------------
# 1. VPC
# --------------------------------------------------

print("Creando VPC...")

vpc = ec2.create_vpc(
    CidrBlock="10.1.0.0/16",
    TagSpecifications=[
        {
            "ResourceType": "vpc",
            "Tags": [
                {"Key": "Name", "Value": "taller-punto2-boto3-vpc"}
            ]
        }
    ]
)

vpc_id = vpc["Vpc"]["VpcId"]

ec2.get_waiter("vpc_available").wait(VpcIds=[vpc_id])

print(f"VPC creada: {vpc_id}")


# --------------------------------------------------
# 2. Subnets
# --------------------------------------------------

zones = ec2.describe_availability_zones(
    Filters=[{"Name": "state", "Values": ["available"]}]
)

az1 = zones["AvailabilityZones"][0]["ZoneName"]
az2 = zones["AvailabilityZones"][1]["ZoneName"]

subnet1 = ec2.create_subnet(
    VpcId=vpc_id,
    CidrBlock="10.1.1.0/24",
    AvailabilityZone=az1,
    TagSpecifications=[
        {
            "ResourceType": "subnet",
            "Tags": [
                {"Key": "Name", "Value": "taller-boto3-subnet-1"}
            ]
        }
    ]
)

subnet1_id = subnet1["Subnet"]["SubnetId"]

subnet2 = ec2.create_subnet(
    VpcId=vpc_id,
    CidrBlock="10.1.2.0/24",
    AvailabilityZone=az2,
    TagSpecifications=[
        {
            "ResourceType": "subnet",
            "Tags": [
                {"Key": "Name", "Value": "taller-boto3-subnet-2"}
            ]
        }
    ]
)

subnet2_id = subnet2["Subnet"]["SubnetId"]

print(f"Subnet 1: {subnet1_id}")
print(f"Subnet 2: {subnet2_id}")


# --------------------------------------------------
# 3. Security Group
# --------------------------------------------------

sg = ec2.create_security_group(
    GroupName="taller-boto3-sg",
    Description="Security Group Punto 2 Boto3",
    VpcId=vpc_id
)

sg_id = sg["GroupId"]

ec2.create_tags(
    Resources=[sg_id],
    Tags=[
        {"Key": "Name", "Value": "taller-boto3-sg"}
    ]
)

print(f"Security Group creado: {sg_id}")


# --------------------------------------------------
# 4. S3
# --------------------------------------------------

bucket_name = f"taller-aws-p2-{account_id}-boto3"

print(f"Creando bucket {bucket_name}...")

s3.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={
        "LocationConstraint": REGION
    }
)

print(f"Bucket creado: {bucket_name}")


# --------------------------------------------------
# 5. Buscar Amazon Linux 2023
# --------------------------------------------------

images = ec2.describe_images(
    Owners=["amazon"],
    Filters=[
        {
            "Name": "name",
            "Values": ["al2023-ami-2023.*-x86_64"]
        },
        {
            "Name": "virtualization-type",
            "Values": ["hvm"]
        }
    ]
)

images_sorted = sorted(
    images["Images"],
    key=lambda x: x["CreationDate"],
    reverse=True
)

ami_id = images_sorted[0]["ImageId"]

print(f"AMI seleccionada: {ami_id}")


# --------------------------------------------------
# 6. EC2
# --------------------------------------------------

print("Creando EC2...")

instances = ec2.run_instances(
    ImageId=ami_id,
    InstanceType="t3.micro",
    MinCount=1,
    MaxCount=1,
    SubnetId=subnet1_id,
    SecurityGroupIds=[sg_id],
    TagSpecifications=[
        {
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": "taller-punto2-boto3-ec2"}
            ]
        }
    ]
)

instance_id = instances["Instances"][0]["InstanceId"]

ec2.get_waiter("instance_running").wait(
    InstanceIds=[instance_id]
)

print(f"EC2 creada: {instance_id}")


# --------------------------------------------------
# 7. DB Subnet Group
# --------------------------------------------------

db_subnet_group = "taller-punto2-boto3-db-subnet"

rds.create_db_subnet_group(
    DBSubnetGroupName=db_subnet_group,
    DBSubnetGroupDescription="DB subnet group Punto 2 Boto3",
    SubnetIds=[
        subnet1_id,
        subnet2_id
    ]
)

print("DB Subnet Group creado")


# --------------------------------------------------
# 8. RDS MySQL
# --------------------------------------------------

db_identifier = "taller-punto2-boto3-rds"

print("Creando RDS... Esto puede tardar varios minutos.")

rds.create_db_instance(
    DBInstanceIdentifier=db_identifier,
    DBInstanceClass="db.t3.micro",
    Engine="mysql",
    AllocatedStorage=20,
    StorageType="gp3",

    MasterUsername="adminaws",

    # AWS Secrets Manager administra la contraseña
    ManageMasterUserPassword=True,

    DBSubnetGroupName=db_subnet_group,
    VpcSecurityGroupIds=[sg_id],

    PubliclyAccessible=False,
    BackupRetentionPeriod=0,
    DeletionProtection=False,

    Tags=[
        {
            "Key": "Name",
            "Value": "taller-punto2-boto3-rds"
        }
    ]
)

rds.get_waiter("db_instance_available").wait(
    DBInstanceIdentifier=db_identifier
)

print("RDS creada correctamente")


# --------------------------------------------------
# 9. Verificar secreto administrado por RDS
# --------------------------------------------------

response = rds.describe_db_instances(
    DBInstanceIdentifier=db_identifier
)

db = response["DBInstances"][0]

print("\n--- RESUMEN DEL DESPLIEGUE ---")
print(f"VPC: {vpc_id}")
print(f"Subnet 1: {subnet1_id}")
print(f"Subnet 2: {subnet2_id}")
print(f"Security Group: {sg_id}")
print(f"S3: {bucket_name}")
print(f"EC2: {instance_id}")
print(f"RDS: {db_identifier}")

if "MasterUserSecret" in db:
    print(
        "Secret ARN:",
        db["MasterUserSecret"].get("SecretArn")
    )

print("\nDespliegue Boto3 completado.")
