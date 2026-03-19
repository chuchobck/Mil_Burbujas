# -*- coding: utf-8 -*-
"""
Mil Burbujas - Respaldo y Restauración de Base de Datos
Copia el archivo .db a una ruta externa (USB, disco, carpeta).
"""
import shutil
import os
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH, BACKUP_DIR


def crear_respaldo(destino: str = None) -> str:
    """Crea una copia de la base de datos.

    Args:
        destino: Ruta donde guardar el respaldo. Si es None, usa BACKUP_DIR.

    Returns:
        Ruta completa del archivo de respaldo creado.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"No se encontró la base de datos en {DB_PATH}")

    carpeta = destino or BACKUP_DIR
    os.makedirs(carpeta, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_respaldo = f"milburbujas_backup_{timestamp}.db"
    ruta_respaldo = os.path.join(carpeta, nombre_respaldo)

    shutil.copy2(DB_PATH, ruta_respaldo)
    print(f"[OK] Respaldo creado: {ruta_respaldo}")
    return ruta_respaldo


def restaurar_respaldo(ruta_respaldo: str) -> bool:
    """Restaura la base de datos desde un respaldo.

    Args:
        ruta_respaldo: Ruta del archivo .db de respaldo.

    Returns:
        True si la restauración fue exitosa.
    """
    if not os.path.exists(ruta_respaldo):
        raise FileNotFoundError(f"No se encontró el archivo de respaldo: {ruta_respaldo}")

    # Crear respaldo del archivo actual antes de sobrescribir
    if os.path.exists(DB_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        respaldo_previo = DB_PATH.replace(".db", f"_pre_restore_{timestamp}.db")
        shutil.copy2(DB_PATH, respaldo_previo)
        print(f"[INFO] Respaldo previo a restauración: {respaldo_previo}")

    shutil.copy2(ruta_respaldo, DB_PATH)
    print(f"[OK] Base de datos restaurada desde: {ruta_respaldo}")
    return True


def listar_respaldos(carpeta: str = None) -> list[dict]:
    """Lista los respaldos disponibles.

    Returns:
        Lista de diccionarios con nombre, ruta, tamaño y fecha.
    """
    directorio = carpeta or BACKUP_DIR
    if not os.path.exists(directorio):
        return []

    respaldos = []
    for archivo in sorted(os.listdir(directorio), reverse=True):
        if archivo.endswith(".db") and archivo.startswith("milburbujas_backup_"):
            ruta = os.path.join(directorio, archivo)
            info = os.stat(ruta)
            respaldos.append({
                "nombre": archivo,
                "ruta": ruta,
                "tamano_mb": round(info.st_size / (1024 * 1024), 2),
                "fecha": datetime.fromtimestamp(info.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })
    return respaldos
