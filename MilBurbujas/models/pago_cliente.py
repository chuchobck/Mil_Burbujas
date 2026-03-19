# -*- coding: utf-8 -*-
"""DAO - Pago de Cliente."""
from .base_model import BaseModel


class PagoClienteModel(BaseModel):
    TABLE_NAME = "pago_cliente"
    PK_COLUMN = "pago_cliente_id"

    def get_by_cuenta(self, cuenta_cobrar_id: int) -> list[dict]:
        sql = """SELECT pc.*, u.nombre_completo AS usuario_nombre
                 FROM pago_cliente pc
                 JOIN usuario u ON pc.usuario_id = u.usuario_id
                 WHERE pc.cuenta_cobrar_id = ? AND pc.estado = 'ACT'
                 ORDER BY pc.fecha_pago"""
        return self.custom_query(sql, (cuenta_cobrar_id,))

    def get_total_pagado(self, cuenta_cobrar_id: int) -> float:
        sql = """SELECT COALESCE(SUM(monto_pago), 0) as total
                 FROM pago_cliente
                 WHERE cuenta_cobrar_id = ? AND estado = 'ACT'"""
        result = self.custom_query_one(sql, (cuenta_cobrar_id,))
        return result["total"] if result else 0.0

    def tiene_pagos(self, cuenta_cobrar_id: int) -> bool:
        sql = "SELECT 1 FROM pago_cliente WHERE cuenta_cobrar_id = ? AND estado = 'ACT' LIMIT 1"
        return self.db.fetch_one(sql, (cuenta_cobrar_id,)) is not None
