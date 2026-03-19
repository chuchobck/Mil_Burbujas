# -*- coding: utf-8 -*-
"""Migrar tabla usuario para aceptar rol CAJERO e insertar usuario cajero."""
import sqlite3
import hashlib

conn = sqlite3.connect("database/milburbujas.db")
c = conn.cursor()
c.execute("PRAGMA foreign_keys=OFF")
c.execute("BEGIN")

# Renombrar tabla vieja
c.execute("ALTER TABLE usuario RENAME TO usuario_old")

# Crear nueva con CAJERO en CHECK
c.execute("""
CREATE TABLE usuario (
    usuario_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    contrasena_hash TEXT    NOT NULL,
    rol             TEXT    NOT NULL DEFAULT 'ADMIN' CHECK (rol IN ('ADMIN', 'CAJERO', 'OPERADOR')),
    estado          TEXT    NOT NULL DEFAULT 'ACT'   CHECK (estado IN ('ACT', 'INA')),
    fecha_creacion  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    ultimo_acceso   TEXT
)
""")

# Copiar datos
c.execute("INSERT INTO usuario SELECT * FROM usuario_old")
c.execute("DROP TABLE usuario_old")

# Insertar cajero
h = hashlib.sha256(b"cajero123").hexdigest()
c.execute(
    "INSERT OR IGNORE INTO usuario (nombre_completo, email, contrasena_hash, rol, estado) "
    "VALUES (?, ?, ?, ?, ?)",
    ("Cajero", "cajero@milburbujas.local", h, "CAJERO", "ACT"),
)

conn.commit()

c.execute("SELECT usuario_id, nombre_completo, email, rol, estado FROM usuario")
for r in c.fetchall():
    print(r)

conn.close()
print("Migracion completada OK")
