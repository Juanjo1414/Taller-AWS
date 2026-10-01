# Se importan las librerías
import time
import boto3

# Se definen el perfil, la región y los recursos (no hay contraseñas: se usa el ARN del secreto)
PERFIL = "app-redshift"
REGION = "us-east-2"
BUCKET = "taller-redshift-jjm-14992"
PREFIJO = "punto5"
WORKGROUP = "taller-wg"
BASE_DATOS = "tienda"
SECRET_ARN = "arn:aws:secretsmanager:us-east-2:052022403573:secret:redshift!taller-ns-adminrs-N2naDh"

# Se crean los clientes de S3 y de la API de datos de Redshift
sesion = boto3.Session(profile_name=PERFIL, region_name=REGION)
s3 = sesion.client("s3")
redshift_data = sesion.client("redshift-data")

# Se suben los archivos CSV a S3
for archivo in ["clientes.csv", "pedidos.csv"]:
    s3.upload_file(f"datos/{archivo}", BUCKET, f"{PREFIJO}/{archivo}")
    print(f"Subido: s3://{BUCKET}/{PREFIJO}/{archivo}")

# Se definen las instrucciones SQL en el orden en que se ejecutan
instrucciones = [
    ("Borrar tabla pedidos", "DROP TABLE IF EXISTS pedidos"),
    ("Borrar tabla clientes", "DROP TABLE IF EXISTS clientes"),
    ("Crear tabla clientes", """
        CREATE TABLE clientes (
            id_cliente INTEGER NOT NULL, nombre VARCHAR(100), ciudad VARCHAR(50),
            segmento VARCHAR(20), fecha_registro DATE, PRIMARY KEY (id_cliente)
        ) DISTSTYLE ALL"""),
    ("Crear tabla pedidos", """
        CREATE TABLE pedidos (
            id_pedido INTEGER NOT NULL, id_cliente INTEGER NOT NULL, fecha_pedido DATE,
            categoria VARCHAR(30), cantidad INTEGER, valor_total BIGINT,
            PRIMARY KEY (id_pedido), FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
        ) DISTKEY (id_cliente) SORTKEY (fecha_pedido)"""),
    ("Cargar clientes con COPY", f"""
        COPY clientes FROM 's3://{BUCKET}/{PREFIJO}/clientes.csv'
        IAM_ROLE default FORMAT AS CSV IGNOREHEADER 1 DATEFORMAT 'YYYY-MM-DD' REGION '{REGION}'"""),
    ("Cargar pedidos con COPY", f"""
        COPY pedidos FROM 's3://{BUCKET}/{PREFIJO}/pedidos.csv'
        IAM_ROLE default FORMAT AS CSV IGNOREHEADER 1 DATEFORMAT 'YYYY-MM-DD' REGION '{REGION}'"""),
    ("Verificar filas cargadas", """
        SELECT 'clientes' AS tabla, COUNT(*) AS filas FROM clientes
        UNION ALL
        SELECT 'pedidos', COUNT(*) FROM pedidos"""),
    ("Consulta 1 - Filtro: pedidos de más de $1.000.000 en el primer trimestre de 2026", """
        SELECT id_pedido, fecha_pedido, categoria, valor_total
        FROM pedidos
        WHERE valor_total > 1000000 AND fecha_pedido BETWEEN '2026-01-01' AND '2026-03-31'
        ORDER BY valor_total DESC"""),
    ("Consulta 2 - Unión: pedidos de los clientes de Medellín", """
        SELECT p.id_pedido, p.fecha_pedido, c.nombre, c.segmento, p.categoria, p.valor_total
        FROM pedidos p
        JOIN clientes c ON c.id_cliente = p.id_cliente
        WHERE c.ciudad = 'Medellín'
        ORDER BY p.fecha_pedido"""),
    ("Consulta 3 - Agregación: ventas por ciudad", """
        SELECT c.ciudad, COUNT(*) AS pedidos, SUM(p.valor_total) AS total_ventas,
               ROUND(AVG(p.valor_total::DECIMAL(14,2)))::BIGINT AS ticket_promedio
        FROM pedidos p
        JOIN clientes c ON c.id_cliente = p.id_cliente
        GROUP BY c.ciudad
        ORDER BY total_ventas DESC"""),
]

# Se ejecuta cada instrucción, se espera a que termine y se muestran sus resultados
for nombre, sql in instrucciones:
    ejecucion = redshift_data.execute_statement(
        WorkgroupName=WORKGROUP,
        Database=BASE_DATOS,
        SecretArn=SECRET_ARN,
        Sql=sql,
    )

    estado = redshift_data.describe_statement(Id=ejecucion["Id"])
    while estado["Status"] not in ("FINISHED", "FAILED", "ABORTED"):
        time.sleep(1)
        estado = redshift_data.describe_statement(Id=ejecucion["Id"])

    print(f"\n[{estado['Status']}] {nombre} ({estado['Duration'] / 1e9:.2f} s)")
    if estado["Status"] != "FINISHED":
        print("Error:", estado.get("Error"))
        raise SystemExit(1)

    if estado["HasResultSet"]:
        resultado = redshift_data.get_statement_result(Id=ejecucion["Id"])
        columnas = [columna["name"] for columna in resultado["ColumnMetadata"]]
        print(" | ".join(columnas))
        for fila in resultado["Records"]:
            print(" | ".join(str(list(campo.values())[0]) for campo in fila))