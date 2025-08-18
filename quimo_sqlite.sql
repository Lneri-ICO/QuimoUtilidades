-- Script de base de datos convertido para SQLite (versión corregida)

CREATE TABLE comprasmateriaprima (
    id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
    id_mp INTEGER NOT NULL,
    id_proveedor INTEGER NOT NULL,
    fecha_compra TEXT DEFAULT (strftime('%Y-%m-%d', 'now')) NOT NULL,
    cantidad REAL NOT NULL,
    precio_unitario REAL NOT NULL,
    tipo_moneda TEXT NOT NULL,
    total REAL,
    estatus_compra INTEGER DEFAULT 1 NOT NULL,
    comentarios TEXT,
    usuario_registro TEXT,
    FOREIGN KEY(id_mp) REFERENCES materiasprimas(id_mp),
    FOREIGN KEY(id_proveedor) REFERENCES proveedor(id_proveedor)
);

CREATE TABLE formulas (
    id_formula_mp INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    id_mp INTEGER NOT NULL,
    porcentaje REAL NOT NULL,
    FOREIGN KEY(id_mp) REFERENCES materiasprimas(id_mp),
    FOREIGN KEY(id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE materiasprimas (
    id_mp INTEGER PRIMARY KEY AUTOINCREMENT,
    proveedor INTEGER NOT NULL,
    nombre_mp TEXT NOT NULL,
    unidad_medida_mp TEXT NOT NULL,
    cantidad_comprada_mp REAL NOT NULL,
    estatus_mp INTEGER DEFAULT 1 NOT NULL,
    fecha_mp TEXT DEFAULT (strftime('%Y-%m-%d', 'now')) NOT NULL,
    costo_unitario_mp REAL NOT NULL,
    tipo_moneda TEXT NOT NULL,
    total_mp REAL NOT NULL
);

CREATE TABLE produccion (
    id_produccion INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT DEFAULT (strftime('%Y-%m-%d', 'now')) NOT NULL,
    producto_id INTEGER NOT NULL,
    dia character(1) NOT NULL,
    cantidad REAL NOT NULL,
    FOREIGN KEY(producto_id) REFERENCES productos(id_producto)
);

CREATE TABLE productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_producto TEXT NOT NULL,
    unidad_medida_producto TEXT NOT NULL,
    area_producto TEXT NOT NULL,
    cantidad_producto REAL NOT NULL,
    estatus_producto INTEGER DEFAULT 1 NOT NULL,
    fecha_producto TEXT DEFAULT (strftime('%Y-%m-%d', 'now')) NOT NULL
);

CREATE TABLE productosreventa (
    id_prev INTEGER PRIMARY KEY AUTOINCREMENT,
    proveedor INTEGER NOT NULL,
    nombre_prev TEXT NOT NULL,
    unidad_medida_prev TEXT NOT NULL,
    area_prev TEXT NOT NULL,
    cantidad_prev REAL NOT NULL,
    estatus_prev INTEGER DEFAULT 1 NOT NULL,
    FOREIGN KEY(proveedor) REFERENCES proveedor(id_proveedor)
);

CREATE TABLE proveedor (
    id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_proveedor TEXT NOT NULL,
    telefono_proveedor TEXT,
    email_proveedor TEXT
);