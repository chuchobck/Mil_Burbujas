# -*- coding: utf-8 -*-
"""
Mil Burbujas - Modelo Base (DAO Genérico)
Proporciona operaciones CRUD reutilizables para todos los modelos.
Cada modelo concreto hereda de BaseModel y define su tabla/PK.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import DatabaseConnection


class BaseModel:
    """DAO genérico con CRUD completo.

    Cada modelo hijo define:
        TABLE_NAME: str     - nombre de la tabla
        PK_COLUMN: str      - nombre de la columna PK
        HAS_ESTADO: bool    - si usa eliminación lógica (ACT/INA)
    """

    TABLE_NAME: str = ""
    PK_COLUMN: str = ""
    HAS_ESTADO: bool = True

    def __init__(self):
        self.db = DatabaseConnection()

    # ── CREATE ──

    def insert(self, data: dict) -> int:
        """Inserta un registro y retorna el ID generado."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {self.TABLE_NAME} ({columns}) VALUES ({placeholders})"
        cursor = self.db.execute(sql, tuple(data.values()))
        return cursor.lastrowid

    def insert_in_transaction(self, data: dict) -> int:
        """Inserta DENTRO de una transacción (sin commit)."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {self.TABLE_NAME} ({columns}) VALUES ({placeholders})"
        cursor = self.db.execute_in_transaction(sql, tuple(data.values()))
        return cursor.lastrowid

    # ── READ ──

    def get_by_id(self, record_id: int) -> dict | None:
        """Obtiene un registro por su PK."""
        sql = f"SELECT * FROM {self.TABLE_NAME} WHERE {self.PK_COLUMN} = ?"
        return self.db.fetch_one(sql, (record_id,))

    def get_all(self, only_active: bool = True) -> list[dict]:
        """Obtiene todos los registros. Si only_active, filtra por estado=ACT."""
        if self.HAS_ESTADO and only_active:
            sql = f"SELECT * FROM {self.TABLE_NAME} WHERE estado = 'ACT' ORDER BY {self.PK_COLUMN}"
        else:
            sql = f"SELECT * FROM {self.TABLE_NAME} ORDER BY {self.PK_COLUMN}"
        return self.db.fetch_all(sql)

    def get_by_field(self, field: str, value, only_active: bool = True) -> list[dict]:
        """Busca registros por un campo específico."""
        if self.HAS_ESTADO and only_active:
            sql = f"SELECT * FROM {self.TABLE_NAME} WHERE {field} = ? AND estado = 'ACT'"
        else:
            sql = f"SELECT * FROM {self.TABLE_NAME} WHERE {field} = ?"
        return self.db.fetch_all(sql, (value,))

    def get_one_by_field(self, field: str, value) -> dict | None:
        """Obtiene UN registro por un campo específico."""
        sql = f"SELECT * FROM {self.TABLE_NAME} WHERE {field} = ?"
        return self.db.fetch_one(sql, (value,))

    def search(self, field: str, term: str, only_active: bool = True) -> list[dict]:
        """Búsqueda parcial (LIKE) en un campo de texto."""
        if self.HAS_ESTADO and only_active:
            sql = f"SELECT * FROM {self.TABLE_NAME} WHERE {field} LIKE ? AND estado = 'ACT'"
        else:
            sql = f"SELECT * FROM {self.TABLE_NAME} WHERE {field} LIKE ?"
        return self.db.fetch_all(sql, (f"%{term}%",))

    def count(self, only_active: bool = True) -> int:
        """Cuenta registros."""
        if self.HAS_ESTADO and only_active:
            sql = f"SELECT COUNT(*) as total FROM {self.TABLE_NAME} WHERE estado = 'ACT'"
        else:
            sql = f"SELECT COUNT(*) as total FROM {self.TABLE_NAME}"
        result = self.db.fetch_one(sql)
        return result["total"] if result else 0

    def exists(self, record_id: int) -> bool:
        """Verifica si un registro existe por PK."""
        result = self.get_by_id(record_id)
        return result is not None

    def exists_by_field(self, field: str, value) -> bool:
        """Verifica si existe un registro con el valor dado en el campo."""
        sql = f"SELECT 1 FROM {self.TABLE_NAME} WHERE {field} = ? LIMIT 1"
        return self.db.fetch_one(sql, (value,)) is not None

    # ── UPDATE ──

    def update(self, record_id: int, data: dict) -> bool:
        """Actualiza un registro por su PK."""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {self.TABLE_NAME} SET {set_clause} WHERE {self.PK_COLUMN} = ?"
        values = tuple(data.values()) + (record_id,)
        cursor = self.db.execute(sql, values)
        return cursor.rowcount > 0

    def update_in_transaction(self, record_id: int, data: dict) -> bool:
        """Actualiza DENTRO de una transacción (sin commit)."""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {self.TABLE_NAME} SET {set_clause} WHERE {self.PK_COLUMN} = ?"
        values = tuple(data.values()) + (record_id,)
        cursor = self.db.execute_in_transaction(sql, values)
        return cursor.rowcount > 0

    # ── DELETE (lógico) ──

    def deactivate(self, record_id: int) -> bool:
        """Eliminación lógica: cambia estado a INA."""
        if not self.HAS_ESTADO:
            raise NotImplementedError(f"{self.TABLE_NAME} no soporta eliminación lógica")
        return self.update(record_id, {"estado": "INA"})

    def activate(self, record_id: int) -> bool:
        """Reactiva un registro: cambia estado a ACT."""
        if not self.HAS_ESTADO:
            raise NotImplementedError(f"{self.TABLE_NAME} no soporta activación")
        return self.update(record_id, {"estado": "ACT"})

    # ── UTILIDADES ──

    def custom_query(self, sql: str, params: tuple = ()) -> list[dict]:
        """Ejecuta una consulta SQL personalizada."""
        return self.db.fetch_all(sql, params)

    def custom_query_one(self, sql: str, params: tuple = ()) -> dict | None:
        """Ejecuta una consulta SQL personalizada, retorna un registro."""
        return self.db.fetch_one(sql, params)
