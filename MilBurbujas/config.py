# -*- coding: utf-8 -*-
"""
Mil Burbujas - Configuracion Global del Sistema
Sistema de Gestion para Tienda de Productos de Belleza, Limpieza y Cosmeticos
"""
import os

# ===== RUTAS =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "milburbujas.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")

# ===== BASE DE DATOS =====
DB_SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")
DB_SEED_PATH = os.path.join(DB_DIR, "seed_data.sql")
# Datos demo desactivados para uso REAL (producción)
# DB_SEED_OPERACION_PATH = os.path.join(DB_DIR, "seed_operacion.sql")
DB_SEED_OPERACION_PATH = None

# ===== NEGOCIO =====
IVA_PORCENTAJE = 15  # IVA Ecuador 15%
MONTO_MINIMO_COMPROBANTE = 3.00  # RISE: comprobante obligatorio > $3.00
DIAS_ALERTA_CADUCIDAD_DEFAULT = 180  # 6 meses
STOCK_MINIMO_DEFAULT = 5

# ===== ESTADOS =====
ESTADO_ACTIVO = "ACT"
ESTADO_INACTIVO = "INA"

# ===== APLICACION =====
APP_NAME = "Mil Burbujas"
APP_VERSION = "1.0.0"
APP_TITLE = "{} v{} - Gestion de Tienda".format(APP_NAME, APP_VERSION)
