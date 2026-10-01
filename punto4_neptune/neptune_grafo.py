import boto3
import json

# ==========================================
# CONFIGURACIÓN
# ==========================================

REGION = "us-east-2"
PROFILE = "user_cli"

ENDPOINT = (
    "https://taller-neptune-punto4-instance."
    "c34ug8q4agsj.us-east-2.neptune.amazonaws.com:8182"
)

session = boto3.Session(
    profile_name=PROFILE,
    region_name=REGION
)

client = session.client(
    "neptunedata",
    endpoint_url=ENDPOINT
)


def ejecutar(query):
    response = client.execute_open_cypher_query(
        openCypherQuery=query
    )
    return response["results"]


# ==========================================
# 1. CREAR LOS 10 VÉRTICES
# ==========================================

vertices = [
    "MERGE (:Persona {id: 1, nombre: 'Ana'})",
    "MERGE (:Persona {id: 2, nombre: 'Carlos'})",
    "MERGE (:Persona {id: 3, nombre: 'Laura'})",
    "MERGE (:Persona {id: 4, nombre: 'Miguel'})",
    "MERGE (:Persona {id: 5, nombre: 'Sofia'})",
    "MERGE (:Persona {id: 6, nombre: 'Daniel'})",

    "MERGE (:Empresa {id: 101, nombre: 'TechCorp'})",
    "MERGE (:Empresa {id: 102, nombre: 'DataWorks'})",

    "MERGE (:Ciudad {id: 201, nombre: 'Medellin'})",
    "MERGE (:Ciudad {id: 202, nombre: 'Bogota'})"
]

print("Creando vertices...")

for query in vertices:
    ejecutar(query)

print("10 vertices creados correctamente.")


# ==========================================
# 2. CREAR LAS 18 RELACIONES
# ==========================================

relaciones = [

    # TRABAJA_EN
    """
    MATCH (p:Persona {nombre:'Ana'}),
          (e:Empresa {nombre:'TechCorp'})
    MERGE (p)-[:TRABAJA_EN]->(e)
    """,

    """
    MATCH (p:Persona {nombre:'Carlos'}),
          (e:Empresa {nombre:'TechCorp'})
    MERGE (p)-[:TRABAJA_EN]->(e)
    """,

    """
    MATCH (p:Persona {nombre:'Laura'}),
          (e:Empresa {nombre:'DataWorks'})
    MERGE (p)-[:TRABAJA_EN]->(e)
    """,

    """
    MATCH (p:Persona {nombre:'Miguel'}),
          (e:Empresa {nombre:'DataWorks'})
    MERGE (p)-[:TRABAJA_EN]->(e)
    """,

    """
    MATCH (p:Persona {nombre:'Sofia'}),
          (e:Empresa {nombre:'TechCorp'})
    MERGE (p)-[:TRABAJA_EN]->(e)
    """,

    """
    MATCH (p:Persona {nombre:'Daniel'}),
          (e:Empresa {nombre:'DataWorks'})
    MERGE (p)-[:TRABAJA_EN]->(e)
    """,

    # VIVE_EN
    """
    MATCH (p:Persona {nombre:'Ana'}),
          (c:Ciudad {nombre:'Medellin'})
    MERGE (p)-[:VIVE_EN]->(c)
    """,

    """
    MATCH (p:Persona {nombre:'Carlos'}),
          (c:Ciudad {nombre:'Bogota'})
    MERGE (p)-[:VIVE_EN]->(c)
    """,

    """
    MATCH (p:Persona {nombre:'Laura'}),
          (c:Ciudad {nombre:'Medellin'})
    MERGE (p)-[:VIVE_EN]->(c)
    """,

    """
    MATCH (p:Persona {nombre:'Miguel'}),
          (c:Ciudad {nombre:'Bogota'})
    MERGE (p)-[:VIVE_EN]->(c)
    """,

    """
    MATCH (p:Persona {nombre:'Sofia'}),
          (c:Ciudad {nombre:'Medellin'})
    MERGE (p)-[:VIVE_EN]->(c)
    """,

    """
    MATCH (p:Persona {nombre:'Daniel'}),
          (c:Ciudad {nombre:'Bogota'})
    MERGE (p)-[:VIVE_EN]->(c)
    """,

    # CONOCE_A
    """
    MATCH (a:Persona {nombre:'Ana'}),
          (b:Persona {nombre:'Carlos'})
    MERGE (a)-[:CONOCE_A]->(b)
    """,

    """
    MATCH (a:Persona {nombre:'Ana'}),
          (b:Persona {nombre:'Laura'})
    MERGE (a)-[:CONOCE_A]->(b)
    """,

    """
    MATCH (a:Persona {nombre:'Carlos'}),
          (b:Persona {nombre:'Miguel'})
    MERGE (a)-[:CONOCE_A]->(b)
    """,

    """
    MATCH (a:Persona {nombre:'Laura'}),
          (b:Persona {nombre:'Sofia'})
    MERGE (a)-[:CONOCE_A]->(b)
    """,

    """
    MATCH (a:Persona {nombre:'Miguel'}),
          (b:Persona {nombre:'Daniel'})
    MERGE (a)-[:CONOCE_A]->(b)
    """,

    """
    MATCH (a:Persona {nombre:'Sofia'}),
          (b:Persona {nombre:'Daniel'})
    MERGE (a)-[:CONOCE_A]->(b)
    """
]

print("Creando relaciones...")

for query in relaciones:
    ejecutar(query)

print("18 relaciones creadas correctamente.")


# ==========================================
# 3. CONSULTAS
# ==========================================

print("\n--- CONSULTA 1 ---")
print("Personas que trabajan en TechCorp")

resultado1 = ejecutar("""
MATCH (p:Persona)-[:TRABAJA_EN]->(e:Empresa {nombre:'TechCorp'})
RETURN p.nombre AS persona,
       e.nombre AS empresa
""")

print(json.dumps(resultado1, indent=2))


print("\n--- CONSULTA 2 ---")
print("Personas que viven en Medellin")

resultado2 = ejecutar("""
MATCH (p:Persona)-[:VIVE_EN]->(c:Ciudad {nombre:'Medellin'})
RETURN p.nombre AS persona,
       c.nombre AS ciudad
""")

print(json.dumps(resultado2, indent=2))


print("\n--- CONSULTA 3 ---")
print("Recorrido de dos niveles desde Ana")

resultado3 = ejecutar("""
MATCH
(a:Persona {nombre:'Ana'})
-[:CONOCE_A]->
(b:Persona)
-[:CONOCE_A]->
(c:Persona)
RETURN
a.nombre AS origen,
b.nombre AS contacto1,
c.nombre AS contacto2
""")

print(json.dumps(resultado3, indent=2))


# ==========================================
# VERIFICACIÓN
# ==========================================

print("\n--- VERIFICACION ---")

conteo = ejecutar("""
MATCH (n)
OPTIONAL MATCH ()-[r]->()
RETURN
count(DISTINCT n) AS vertices,
count(DISTINCT r) AS relaciones
""")

print(json.dumps(conteo, indent=2))