# Se importan las librerías
import json
import boto3
from botocore.exceptions import ClientError

# Se definen el perfil, la región y el nombre del secreto (no hay contraseñas en el código)
PERFIL = "lector-secreto"
REGION = "us-east-2"
NOMBRE_SECRETO = "taller-aws/punto1/credenciales-prueba"

# Se crea el cliente de Secrets Manager usando las credenciales del perfil
sesion = boto3.Session(profile_name=PERFIL, region_name=REGION)
cliente = sesion.client("secretsmanager")

# Se recupera la versión actual del secreto (etiqueta AWSCURRENT)
try:
    respuesta = cliente.get_secret_value(SecretId=NOMBRE_SECRETO)
except ClientError as error:
    print("No se pudo leer el secreto:", error.response["Error"]["Code"])
    raise SystemExit(1)

# Se convierte el contenido del secreto a diccionario
secreto = json.loads(respuesta["SecretString"])

# Se muestran los datos sin exponer la contraseña completa
contrasena = secreto["password"]
print("Usuario:", secreto["username"])
print("Contraseña:", contrasena[:2] + "*" * (len(contrasena) - 2))
print("VersionId:", respuesta["VersionId"])
print("Etapas de la versión:", respuesta["VersionStages"])
print("Fecha de la versión:", respuesta["CreatedDate"])