-- Consulta inicial
SELECT *
FROM "taller_punto6_db"."taller_aws_punto6_sgf"
LIMIT 10;

-- Consulta con filtro
SELECT *
FROM "taller_punto6_db"."taller_aws_punto6_sgf"
WHERE ciudad = 'Medellin';

-- Consulta con agrupación
SELECT categoria,
       SUM(cantidad) AS total_unidades
FROM "taller_punto6_db"."taller_aws_punto6_sgf"
GROUP BY categoria
ORDER BY total_unidades DESC;

-- Verificación del total de registros
SELECT COUNT(*) AS total_registros
FROM "taller_punto6_db"."taller_aws_punto6_sgf";

-- Verificación de los registros agregados
SELECT *
FROM "taller_punto6_db"."taller_aws_punto6_sgf"
WHERE id > 20
ORDER BY id;
