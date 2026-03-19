# -*- coding: utf-8 -*-
"""DAO - Cuenta por Pagar (deuda a proveedores)."""
from .base_model import BaseModel


class CuentaPagarModel(BaseModel):
    TABLE_NAME = "cuenta_pagar"
    PK_COLUMN = "cuenta_pagar_id"

    def get_completas(self) -> list[dict]:
        sql = """SELECT cp.*, p.razon_social AS proveedor_nombre,
                        c.numero_factura
                 FROM cuenta_pagar cp
                 JOIN proveedor p ON cp.proveedor_id = p.proveedor_id
                 JOIN compra c    ON cp.compra_id = c.compra_id
                 WHERE cp.estado = 'ACT'
                 ORDER BY cp.fecha_vencimiento"""
        return self.custom_query(sql)

    def get_pendientes_por_proveedor(self, proveedor_id: int) -> list[dict]:
        sql = """SELECT * FROM cuenta_pagar
                 WHERE proveedor_id = ? AND estado = 'ACT'
                   AND estado_pago IN ('PENDIENTE', 'PARCIAL', 'VENCIDO')
                 ORDER BY fecha_vencimiento"""
        return self.custom_query(sql, (proveedor_id,))

    def get_vencidas(self) -> list[dict]:
        sql = """SELECT cp.*, p.razon_social AS proveedor_nombre
                 FROM cuenta_pagar cp
                 JOIN proveedor p ON cp.proveedor_id = p.proveedor_id
                 WHERE cp.estado = 'ACT'
                   AND cp.estado_pago IN ('PENDIENTE', 'PARCIAL', 'VENCIDO')
                   AND date(cp.fecha_vencimiento) < date('now', 'localtime')
                 ORDER BY cp.fecha_vencimiento"""
        return self.custom_query(sql)

    def get_by_compra(self, compra_id: int) -> dict | None:
        return self.get_one_by_field("compra_id", compra_id)

    def get_total_pendiente(self) -> float:
        sql = """SELECT COALESCE(SUM(saldo_pendiente), 0) as total
                 FROM cuenta_pagar
                 WHERE estado = 'ACT' AND estado_pago IN ('PENDIENTE', 'PARCIAL', 'VENCIDO')"""
        result = self.custom_query_one(sql)
        return result["total"] if result else 0.0
