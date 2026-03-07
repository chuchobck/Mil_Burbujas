# -*- coding: utf-8 -*-
"""DAO - Cuenta por Cobrar (Fiados)."""
from .base_model import BaseModel


class CuentaCobrarModel(BaseModel):
    TABLE_NAME = "cuenta_cobrar"
    PK_COLUMN = "cuenta_cobrar_id"

    def get_completas(self) -> list[dict]:
        sql = """SELECT cc.*, c.nombres || ' ' || c.apellidos AS cliente_nombre,
                        c.telefono AS cliente_telefono, c.frecuencia_pago
                 FROM cuenta_cobrar cc
                 JOIN cliente c ON cc.cliente_id = c.cliente_id
                 WHERE cc.estado = 'ACT'
                 ORDER BY cc.fecha_vencimiento"""
        return self.custom_query(sql)

    def get_pendientes_por_cliente(self, cliente_id: int) -> list[dict]:
        sql = """SELECT * FROM cuenta_cobrar
                 WHERE cliente_id = ? AND estado = 'ACT'
                   AND estado_pago IN ('PENDIENTE', 'PARCIAL', 'VENCIDO')
                 ORDER BY fecha_vencimiento"""
        return self.custom_query(sql, (cliente_id,))

    def get_vencidas(self) -> list[dict]:
        sql = """SELECT cc.*, c.nombres || ' ' || c.apellidos AS cliente_nombre
                 FROM cuenta_cobrar cc
                 JOIN cliente c ON cc.cliente_id = c.cliente_id
                 WHERE cc.estado = 'ACT'
                   AND cc.estado_pago IN ('PENDIENTE', 'PARCIAL', 'VENCIDO')
                   AND date(cc.fecha_vencimiento) < date('now', 'localtime')
                 ORDER BY cc.fecha_vencimiento"""
        return self.custom_query(sql)

    def get_by_venta(self, venta_id: int) -> dict | None:
        return self.get_one_by_field("venta_id", venta_id)

    def get_total_pendiente(self) -> float:
        sql = """SELECT COALESCE(SUM(saldo_pendiente), 0) as total
                 FROM cuenta_cobrar
                 WHERE estado = 'ACT' AND estado_pago IN ('PENDIENTE', 'PARCIAL', 'VENCIDO')"""
        result = self.custom_query_one(sql)
        return result["total"] if result else 0.0
