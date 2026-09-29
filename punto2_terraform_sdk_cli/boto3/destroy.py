import boto3
from botocore.exceptions import ClientError

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

BUCKET_NAME = f"taller-aws-p2-{account_id}-boto3"
DB_IDENTIFIER = "taller-punto2-boto3-rds"
DB_SUBNET_GROUP = "taller-punto2-boto3-db-subnet"


# --------------------------------------------------
# 1. Eliminar RDS
# --------------------------------------------------

print("Eliminando RDS...")

try:
    rds.delete_db_instance(
        DBInstanceIdentifier=DB_IDENTIFIER,
        SkipFinalSnapshot=True,
        DeleteAutomatedBackups=True
    )

    rds.get_waiter("db_instance_deleted").wait(
        DBInstanceIdentifier=DB_IDENTIFIER
    )

    print("RDS eliminada correctamente")

except ClientError as e:
    print(f"RDS: {e.response['Error']['Code']}")


# --------------------------------------------------
# 2. Eliminar DB Subnet Group
# --------------------------------------------------

try:
    rds.delete_db_subnet_group(
        DBSubnetGroupName=DB_SUBNET_GROUP
    )
    print("DB Subnet Group eliminado")
except ClientError as e:
    print(f"DB Subnet Group: {e.response['Error']['Code']}")


# --------------------------------------------------
# 3. Buscar VPC creada por Boto3
# --------------------------------------------------

vpcs = ec2.describe_vpcs(
    Filters=[
        {
            "Name": "tag:Name",
            "Values": ["taller-punto2-boto3-vpc"]
        }
    ]
)["Vpcs"]

if vpcs:
    vpc_id = vpcs[0]["VpcId"]

    # ----------------------------------------------
    # 4. Terminar EC2
    # ----------------------------------------------

    instances = ec2.describe_instances(
        Filters=[
            {
                "Name": "tag:Name",
                "Values": ["taller-punto2-boto3-ec2"]
            },
            {
                "Name": "instance-state-name",
                "Values": ["pending", "running", "stopping", "stopped"]
            }
        ]
    )

    instance_ids = []

    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            instance_ids.append(instance["InstanceId"])

    if instance_ids:
        print(f"Terminando EC2: {instance_ids}")

        ec2.terminate_instances(
            InstanceIds=instance_ids
        )

        ec2.get_waiter("instance_terminated").wait(
            InstanceIds=instance_ids
        )

        print("EC2 eliminada correctamente")


    # ----------------------------------------------
    # 5. Eliminar Security Group
    # ----------------------------------------------

    security_groups = ec2.describe_security_groups(
        Filters=[
            {
                "Name": "group-name",
                "Values": ["taller-boto3-sg"]
            },
            {
                "Name": "vpc-id",
                "Values": [vpc_id]
            }
        ]
    )["SecurityGroups"]

    for sg in security_groups:
        ec2.delete_security_group(
            GroupId=sg["GroupId"]
        )
        print(f"Security Group eliminado: {sg['GroupId']}")


    # ----------------------------------------------
    # 6. Eliminar subnets
    # ----------------------------------------------

    subnets = ec2.describe_subnets(
        Filters=[
            {
                "Name": "vpc-id",
                "Values": [vpc_id]
            }
        ]
    )["Subnets"]

    for subnet in subnets:
        ec2.delete_subnet(
            SubnetId=subnet["SubnetId"]
        )
        print(f"Subnet eliminada: {subnet['SubnetId']}")


    # ----------------------------------------------
    # 7. Eliminar VPC
    # ----------------------------------------------

    ec2.delete_vpc(
        VpcId=vpc_id
    )

    print(f"VPC eliminada: {vpc_id}")


# --------------------------------------------------
# 8. Vaciar y eliminar S3
# --------------------------------------------------

print("Eliminando bucket S3...")

try:
    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME
    )

    if "Contents" in response:
        objects = [
            {"Key": obj["Key"]}
            for obj in response["Contents"]
        ]

        s3.delete_objects(
            Bucket=BUCKET_NAME,
            Delete={"Objects": objects}
        )

    s3.delete_bucket(
        Bucket=BUCKET_NAME
    )

    print(f"Bucket eliminado: {BUCKET_NAME}")

except ClientError as e:
    print(f"S3: {e.response['Error']['Code']}")


print("\n--- ELIMINACIÓN COMPLETADA ---")
print("Recursos del despliegue Boto3 eliminados correctamente.")
