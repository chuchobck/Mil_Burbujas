# -*- coding: utf-8 -*-
"""
Mil Burbujas - Conexión a Base de Datos SQLite
Singleton con soporte para transacciones.
"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH, DB_SCHEMA_PATH, DB_SEED_PATH, DB_DIR
try:
    from config import DB_SEED_OPERACION_PATH
except ImportError:
    DB_SEED_OPERACION_PATH = None


class DatabaseConnection:
    """Singleton para conexión SQLite con transacciones."""

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """Obtiene la conexión activa o crea una nueva."""
        if self._connection is None:
            os.makedirs(DB_DIR, exist_ok=True)
            self._connection = sqlite3.connect(DB_PATH)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute("PRAGMA journal_mode = WAL")
        return self._connection

    def close(self):
        """Cierra la conexión."""
        if self._connection:
            self._connection.close()
            self._connection = None

    # ----- OPERACIONES BÁSICAS -----

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Ejecuta una sentencia SQL con autocommit."""
        conn = self.get_connection()
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor

    def execute_many(self, sql: str, params_list: list) -> sqlite3.Cursor:
        """Ejecuta una sentencia con múltiples sets de parámetros."""
        conn = self.get_connection()
        cursor = conn.executemany(sql, params_list)
        conn.commit()
        return cursor

    def fetch_one(self, sql: str, params: tuple = ()) -> dict | None:
        """Ejecuta y retorna una fila como diccionario."""
        conn = self.get_connection()
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, sql: str, params: tuple = ()) -> list[dict]:
        """Ejecuta y retorna todas las filas como lista de diccionarios."""
        conn = self.get_connection()
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    # ----- TRANSACCIONES -----

    def begin_transaction(self):
        """Inicia una transacción explícita."""
        conn = self.get_connection()
        conn.execute("BEGIN")

    def commit(self):
        """Confirma la transacción actual."""
        conn = self.get_connection()
        conn.commit()

    def rollback(self):
        """Revierte la transacción actual."""
        conn = self.get_connection()
        conn.rollback()

    def transaction(self):
        """Context manager para transacciones atómicas.

        Uso:
            with db.transaction():
                db.execute_in_transaction(...)
                db.execute_in_transaction(...)
        """
        return TransactionContext(self)

    def execute_in_transaction(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Ejecuta SQL DENTRO de una transacción (sin commit automático)."""
        conn = self.get_connection()
        return conn.execute(sql, params)

    def fetch_one_in_transaction(self, sql: str, params: tuple = ()) -> dict | None:
        """Fetch one DENTRO de una transacción."""
        conn = self.get_connection()
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all_in_transaction(self, sql: str, params: tuple = ()) -> list[dict]:
        """Fetch all DENTRO de una transacción."""
        conn = self.get_connection()
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    # ----- INICIALIZACIÓN -----

    def init_database(self):
        """Crea las tablas (schema) y carga datos iniciales (seed)."""
        conn = self.get_connection()

        # Desactivar FKs durante la carga masiva para evitar problemas de orden
        conn.execute("PRAGMA foreign_keys = OFF")

        # Crear tablas
        if os.path.exists(DB_SCHEMA_PATH):
            with open(DB_SCHEMA_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            print("[OK] Schema creado correctamente.")
        else:
            print(f"[ERROR] No se encontró {DB_SCHEMA_PATH}")
            return False

        # Cargar datos iniciales
        if os.path.exists(DB_SEED_PATH):
            with open(DB_SEED_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            print("[OK] Datos iniciales cargados.")
        else:
            print("[INFO] No se encontró seed_data.sql, se omite.")

        # Reactivar FKs
        conn.execute("PRAGMA foreign_keys = ON")

        return True

    def get_table_count(self) -> int:
        """Retorna la cantidad de tablas creadas."""
        result = self.fetch_one(
            "SELECT COUNT(*) as total FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return result["total"] if result else 0

    def get_tables(self) -> list[str]:
        """Retorna la lista de nombres de tablas."""
        rows = self.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        return [row["name"] for row in rows]


class TransactionContext:
    """Context manager para transacciones atómicas."""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def __enter__(self):
        self.db.begin_transaction()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
            return False  # Re-lanza la excepción
        self.db.commit()
        return True
