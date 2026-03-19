# -*- coding: utf-8 -*-
"""Script temporal para verificar la carga del catálogo."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DB_PATH
from database.connection import DatabaseConnection

db = DatabaseConnection()

if not os.path.exists(DB_PATH):
    print("[INFO] Creando base de datos con catalogo completo...")
    result = db.init_database()
    print("[OK] BD creada." if result else "[ERROR] Fallo al crear BD.")
else:
    print("[INFO] BD ya existe.")

# Verificar categorias padre
cats_padre = db.fetch_all("SELECT categoria_id, nombre FROM categoria WHERE nivel = 0 ORDER BY categoria_id")
print("\n=== CATEGORIAS PADRE ({}) ===".format(len(cats_padre)))
for c in cats_padre:
    hijas = db.fetch_all("SELECT nombre FROM categoria WHERE categoria_padre_id = ? ORDER BY nombre", (c["categoria_id"],))
    print("\n  {:2d}. {}".format(c["categoria_id"], c["nombre"]))
    for h in hijas:
        print("      > {}".format(h["nombre"]))

total = db.fetch_one("SELECT COUNT(*) as t FROM categoria")
print("\nTotal categorias: {} ({} padres + {} subcategorias)".format(
    total["t"], len(cats_padre), total["t"] - len(cats_padre)))

# Usuarios
users = db.fetch_all("SELECT nombre_completo, email, rol FROM usuario ORDER BY usuario_id")
print("\n=== USUARIOS ({}) ===".format(len(users)))
for u in users:
    print("  {} | {} | {}".format(u["nombre_completo"], u["email"], u["rol"]))

# Unidades
unidades = db.fetch_all("SELECT nombre, abreviatura FROM unidad_medida ORDER BY nombre")
print("\n=== UNIDADES ({}) ===".format(len(unidades)))
for u in unidades:
    print("  {} ({})".format(u["nombre"], u["abreviatura"]))

db.close()
print("\n[OK] Verificacion completa.")
