// ==============================
// CREACIÓN DE VÉRTICES
// ==============================

// Personas
CREATE (:Persona {id: 1, nombre: 'Ana'});
CREATE (:Persona {id: 2, nombre: 'Carlos'});
CREATE (:Persona {id: 3, nombre: 'Laura'});
CREATE (:Persona {id: 4, nombre: 'Miguel'});
CREATE (:Persona {id: 5, nombre: 'Sofia'});
CREATE (:Persona {id: 6, nombre: 'Daniel'});

// Empresas
CREATE (:Empresa {id: 101, nombre: 'TechCorp'});
CREATE (:Empresa {id: 102, nombre: 'DataWorks'});

// Ciudades
CREATE (:Ciudad {id: 201, nombre: 'Medellin'});
CREATE (:Ciudad {id: 202, nombre: 'Bogota'});


// ==============================
// CREACIÓN DE RELACIONES
// ==============================

// TRABAJA_EN
MATCH (p:Persona {nombre:'Ana'}), (e:Empresa {nombre:'TechCorp'})
CREATE (p)-[:TRABAJA_EN]->(e);

MATCH (p:Persona {nombre:'Carlos'}), (e:Empresa {nombre:'TechCorp'})
CREATE (p)-[:TRABAJA_EN]->(e);

MATCH (p:Persona {nombre:'Laura'}), (e:Empresa {nombre:'DataWorks'})
CREATE (p)-[:TRABAJA_EN]->(e);

MATCH (p:Persona {nombre:'Miguel'}), (e:Empresa {nombre:'DataWorks'})
CREATE (p)-[:TRABAJA_EN]->(e);

MATCH (p:Persona {nombre:'Sofia'}), (e:Empresa {nombre:'TechCorp'})
CREATE (p)-[:TRABAJA_EN]->(e);

MATCH (p:Persona {nombre:'Daniel'}), (e:Empresa {nombre:'DataWorks'})
CREATE (p)-[:TRABAJA_EN]->(e);


// VIVE_EN
MATCH (p:Persona {nombre:'Ana'}), (c:Ciudad {nombre:'Medellin'})
CREATE (p)-[:VIVE_EN]->(c);

MATCH (p:Persona {nombre:'Carlos'}), (c:Ciudad {nombre:'Bogota'})
CREATE (p)-[:VIVE_EN]->(c);

MATCH (p:Persona {nombre:'Laura'}), (c:Ciudad {nombre:'Medellin'})
CREATE (p)-[:VIVE_EN]->(c);

MATCH (p:Persona {nombre:'Miguel'}), (c:Ciudad {nombre:'Bogota'})
CREATE (p)-[:VIVE_EN]->(c);

MATCH (p:Persona {nombre:'Sofia'}), (c:Ciudad {nombre:'Medellin'})
CREATE (p)-[:VIVE_EN]->(c);

MATCH (p:Persona {nombre:'Daniel'}), (c:Ciudad {nombre:'Bogota'})
CREATE (p)-[:VIVE_EN]->(c);


// CONOCE_A
MATCH (a:Persona {nombre:'Ana'}), (b:Persona {nombre:'Carlos'})
CREATE (a)-[:CONOCE_A]->(b);

MATCH (a:Persona {nombre:'Ana'}), (b:Persona {nombre:'Laura'})
CREATE (a)-[:CONOCE_A]->(b);

MATCH (a:Persona {nombre:'Carlos'}), (b:Persona {nombre:'Miguel'})
CREATE (a)-[:CONOCE_A]->(b);

MATCH (a:Persona {nombre:'Laura'}), (b:Persona {nombre:'Sofia'})
CREATE (a)-[:CONOCE_A]->(b);

MATCH (a:Persona {nombre:'Miguel'}), (b:Persona {nombre:'Daniel'})
CREATE (a)-[:CONOCE_A]->(b);

MATCH (a:Persona {nombre:'Sofia'}), (b:Persona {nombre:'Daniel'})
CREATE (a)-[:CONOCE_A]->(b);


// ==============================
// CONSULTA 1
// Personas que trabajan en TechCorp
// ==============================

MATCH (p:Persona)-[:TRABAJA_EN]->(e:Empresa {nombre:'TechCorp'})
RETURN p.nombre, e.nombre;


// ==============================
// CONSULTA 2
// Personas que viven en Medellin
// ==============================

MATCH (p:Persona)-[:VIVE_EN]->(c:Ciudad {nombre:'Medellin'})
RETURN p.nombre, c.nombre;


// ==============================
// CONSULTA 3
// Recorrido de dos niveles de conocidos
// ==============================

MATCH (p1:Persona {nombre:'Ana'})-[:CONOCE_A]->(p2:Persona)-[:CONOCE_A]->(p3:Persona)
RETURN p1.nombre, p2.nombre, p3.nombre;
