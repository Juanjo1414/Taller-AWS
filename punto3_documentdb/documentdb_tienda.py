# Se importan las librerías
import json
import boto3
from pymongo import MongoClient

# Se definen el perfil, la región, el nombre del secreto y el certificado TLS
PERFIL = "app-docdb"
REGION = "us-east-2"
NOMBRE_SECRETO = "rds!cluster-9d7acc96-9050-4a72-9d68-834df82fbe06"
RUTA_CA = "global-bundle.pem"

# Se recuperan el usuario y la contraseña desde Secrets Manager
sesion = boto3.Session(profile_name=PERFIL, region_name=REGION)
cliente_secretos = sesion.client("secretsmanager")
respuesta = cliente_secretos.get_secret_value(SecretId=NOMBRE_SECRETO)
secreto = json.loads(respuesta["SecretString"])

# Se conecta a DocumentDB a través del túnel SSH abierto en localhost:27017
cliente = MongoClient(
    host="localhost",
    port=27017,
    username=secreto["username"],
    password=secreto["password"],
    tls=True,
    tlsCAFile=RUTA_CA,
    tlsAllowInvalidHostnames=True,
    directConnection=True,
    retryWrites=False,
    serverSelectionTimeoutMS=10000,
)
print("Ping:", cliente.admin.command("ping"))

# Se crea la base de datos y la colección (se limpia para poder repetir la ejecución)
bd = cliente["tienda"]
productos = bd["productos"]
productos.drop()

# Se insertan los documentos
documentos = [
    {"nombre": "Portátil Lenovo", "categoria": "Tecnología", "precio": 3200000, "stock": 8, "ciudad": "Medellín"},
    {"nombre": "Mouse inalámbrico", "categoria": "Tecnología", "precio": 85000, "stock": 40, "ciudad": "Bogotá"},
    {"nombre": "Monitor 27 pulgadas", "categoria": "Tecnología", "precio": 1100000, "stock": 12, "ciudad": "Medellín"},
    {"nombre": "Silla ergonómica", "categoria": "Oficina", "precio": 950000, "stock": 5, "ciudad": "Cali"},
    {"nombre": "Escritorio en L", "categoria": "Oficina", "precio": 780000, "stock": 3, "ciudad": "Medellín"},
    {"nombre": "Lámpara LED", "categoria": "Oficina", "precio": 120000, "stock": 25, "ciudad": "Bogotá"},
    {"nombre": "Café de Antioquia 500 g", "categoria": "Alimentos", "precio": 32000, "stock": 60, "ciudad": "Medellín"},
    {"nombre": "Chocolate de mesa", "categoria": "Alimentos", "precio": 9500, "stock": 80, "ciudad": "Cali"},
    {"nombre": "Audífonos Bluetooth", "categoria": "Tecnología", "precio": 250000, "stock": 18, "ciudad": "Cali"},
    {"nombre": "Termo de acero", "categoria": "Hogar", "precio": 65000, "stock": 30, "ciudad": "Bogotá"},
]
resultado = productos.insert_many(documentos)
print("Documentos insertados:", len(resultado.inserted_ids))

# Consulta 1: búsqueda con filtro (tecnología con precio mayor a 200.000)
print("\nConsulta 1 - Tecnología con precio > 200.000:")
for doc in productos.find({"categoria": "Tecnología", "precio": {"$gt": 200000}}, {"_id": 0, "nombre": 1, "precio": 1}):
    print(doc)

# Consulta 2: ordenación (productos de Medellín del más caro al más barato)
print("\nConsulta 2 - Productos de Medellín ordenados por precio descendente:")
for doc in productos.find({"ciudad": "Medellín"}, {"_id": 0, "nombre": 1, "precio": 1}).sort("precio", -1):
    print(doc)

# Consulta 3: agregación (por categoría: cantidad de productos, stock total y precio promedio)
print("\nConsulta 3 - Resumen por categoría:")
pipeline = [
    {"$group": {
        "_id": "$categoria",
        "cantidad_productos": {"$sum": 1},
        "stock_total": {"$sum": "$stock"},
        "precio_promedio": {"$avg": "$precio"},
    }},
    {"$sort": {"stock_total": -1}},
]
for doc in productos.aggregate(pipeline):
    print(doc["_id"], "| productos:", doc["cantidad_productos"], "| stock:", doc["stock_total"], "| precio promedio:", round(doc["precio_promedio"]))

# Se cierra la conexión
cliente.close()