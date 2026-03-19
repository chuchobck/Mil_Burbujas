# -*- coding: utf-8 -*-
"""DAO - Cliente."""
from .base_model import BaseModel


class ClienteModel(BaseModel):
    TABLE_NAME = "cliente"
    PK_COLUMN = "cliente_id"

    def get_by_cedula(self, cedula: str) -> dict | None:
        return self.get_one_by_field("cedula", cedula)

    def get_con_credito(self) -> list[dict]:
        """Clientes habilitados para crédito."""
        sql = """SELECT * FROM cliente
                 WHERE habilitado_credito = 1 AND estado = 'ACT'
                 ORDER BY apellidos, nombres"""
        return self.custom_query(sql)

    def get_con_saldo_pendiente(self) -> list[dict]:
        """Clientes que deben dinero."""
        sql = """SELECT * FROM cliente
                 WHERE saldo_pendiente > 0 AND estado = 'ACT'
                 ORDER BY saldo_pendiente DESC"""
        return self.custom_query(sql)

    def tiene_saldo_pendiente(self, cliente_id: int) -> bool:
        sql = "SELECT 1 FROM cliente WHERE cliente_id = ? AND saldo_pendiente > 0 LIMIT 1"
        return self.db.fetch_one(sql, (cliente_id,)) is not None

    def actualizar_saldo(self, cliente_id: int, nuevo_saldo: float) -> bool:
        return self.update_in_transaction(cliente_id, {"saldo_pendiente": nuevo_saldo})

    def buscar(self, termino: str) -> list[dict]:
        sql = """SELECT * FROM cliente
                 WHERE estado = 'ACT'
                   AND (nombres LIKE ? OR apellidos LIKE ? OR cedula LIKE ?)
                 ORDER BY apellidos, nombres"""
        like = f"%{termino}%"
        return self.custom_query(sql, (like, like, like))
