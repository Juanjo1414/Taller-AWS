-- Punto 5 - Amazon Redshift Serverless
-- Base de datos: tienda | Workgroup: taller-wg | Región: us-east-2
-- Las instrucciones se ejecutan desde redshift_carga_consultas.py mediante la API de datos de Redshift.

-- Creación de tablas
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS clientes;

-- Tabla de dimensión pequeña: se replica en todos los nodos (DISTSTYLE ALL)
CREATE TABLE clientes (
    id_cliente      INTEGER      NOT NULL,
    nombre          VARCHAR(100),
    ciudad          VARCHAR(50),
    segmento        VARCHAR(20),
    fecha_registro  DATE,
    PRIMARY KEY (id_cliente)
)
DISTSTYLE ALL;

-- Tabla de hechos: se distribuye por cliente y se ordena por fecha
CREATE TABLE pedidos (
    id_pedido     INTEGER      NOT NULL,
    id_cliente    INTEGER      NOT NULL,
    fecha_pedido  DATE,
    categoria     VARCHAR(30),
    cantidad      INTEGER,
    valor_total   BIGINT,
    PRIMARY KEY (id_pedido),
    FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
)
DISTKEY (id_cliente)
SORTKEY (fecha_pedido);

-- Carga desde S3 con el rol IAM predeterminado del namespace
COPY clientes
FROM 's3://taller-redshift-jjm-14992/punto5/clientes.csv'
IAM_ROLE default
FORMAT AS CSV
IGNOREHEADER 1
DATEFORMAT 'YYYY-MM-DD'
REGION 'us-east-2';

COPY pedidos
FROM 's3://taller-redshift-jjm-14992/punto5/pedidos.csv'
IAM_ROLE default
FORMAT AS CSV
IGNOREHEADER 1
DATEFORMAT 'YYYY-MM-DD'
REGION 'us-east-2';

-- Verificación de la carga
SELECT 'clientes' AS tabla, COUNT(*) AS filas FROM clientes
UNION ALL
SELECT 'pedidos', COUNT(*) FROM pedidos;

-- Consulta 1 - Filtro: pedidos de más de $1.000.000 en el primer trimestre de 2026
SELECT id_pedido, fecha_pedido, categoria, valor_total
FROM pedidos
WHERE valor_total > 1000000
  AND fecha_pedido BETWEEN '2026-01-01' AND '2026-03-31'
ORDER BY valor_total DESC;

-- Consulta 2 - Unión: pedidos de los clientes de Medellín con sus datos
SELECT p.id_pedido, p.fecha_pedido, c.nombre, c.segmento, p.categoria, p.valor_total
FROM pedidos p
JOIN clientes c ON c.id_cliente = p.id_cliente
WHERE c.ciudad = 'Medellín'
ORDER BY p.fecha_pedido;

-- Consulta 3 - Agregación: ventas por ciudad
SELECT c.ciudad,
       COUNT(*) AS pedidos,
       SUM(p.valor_total) AS total_ventas,
       ROUND(AVG(p.valor_total::DECIMAL(14,2)))::BIGINT AS ticket_promedio
FROM pedidos p
JOIN clientes c ON c.id_cliente = p.id_cliente
GROUP BY c.ciudad
ORDER BY total_ventas DESC;
