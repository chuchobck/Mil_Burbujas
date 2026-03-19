# -*- coding: utf-8 -*-
"""DAO - Pago a Proveedor."""
from .base_model import BaseModel


class PagoProveedorModel(BaseModel):
    TABLE_NAME = "pago_proveedor"
    PK_COLUMN = "pago_proveedor_id"

    def get_by_cuenta(self, cuenta_pagar_id: int) -> list[dict]:
        sql = """SELECT pp.*, u.nombre_completo AS usuario_nombre
                 FROM pago_proveedor pp
                 JOIN usuario u ON pp.usuario_id = u.usuario_id
                 WHERE pp.cuenta_pagar_id = ? AND pp.estado = 'ACT'
                 ORDER BY pp.fecha_pago"""
        return self.custom_query(sql, (cuenta_pagar_id,))

    def get_total_pagado(self, cuenta_pagar_id: int) -> float:
        sql = """SELECT COALESCE(SUM(monto_pago), 0) as total
                 FROM pago_proveedor
                 WHERE cuenta_pagar_id = ? AND estado = 'ACT'"""
        result = self.custom_query_one(sql, (cuenta_pagar_id,))
        return result["total"] if result else 0.0

    def tiene_pagos(self, cuenta_pagar_id: int) -> bool:
        sql = "SELECT 1 FROM pago_proveedor WHERE cuenta_pagar_id = ? AND estado = 'ACT' LIMIT 1"
        return self.db.fetch_one(sql, (cuenta_pagar_id,)) is not None
