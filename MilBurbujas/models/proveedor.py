# -*- coding: utf-8 -*-
"""DAO - Proveedor."""
from .base_model import BaseModel


class ProveedorModel(BaseModel):
    TABLE_NAME = "proveedor"
    PK_COLUMN = "proveedor_id"

    def get_by_ruc(self, ruc_cedula: str) -> dict | None:
        return self.get_one_by_field("ruc_cedula", ruc_cedula)

    def get_con_saldo_pendiente(self) -> list[dict]:
        """Proveedores con deudas pendientes."""
        sql = """SELECT p.*,
                        COALESCE(SUM(cp.saldo_pendiente), 0) as total_deuda
                 FROM proveedor p
                 LEFT JOIN cuenta_pagar cp ON p.proveedor_id = cp.proveedor_id
                                          AND cp.estado = 'ACT'
                                          AND cp.estado_pago IN ('PENDIENTE', 'PARCIAL')
                 WHERE p.estado = 'ACT'
                 GROUP BY p.proveedor_id
                 ORDER BY p.razon_social"""
        return self.custom_query(sql)

    def tiene_cuentas_pendientes(self, proveedor_id: int) -> bool:
        sql = """SELECT 1 FROM cuenta_pagar
                 WHERE proveedor_id = ? AND estado = 'ACT'
                   AND estado_pago IN ('PENDIENTE', 'PARCIAL') LIMIT 1"""
        return self.db.fetch_one(sql, (proveedor_id,)) is not None

    def buscar(self, termino: str) -> list[dict]:
        sql = """SELECT * FROM proveedor
                 WHERE estado = 'ACT'
                   AND (razon_social LIKE ? OR ruc_cedula LIKE ? OR nombre_contacto LIKE ?)
                 ORDER BY razon_social"""
        like = f"%{termino}%"
        return self.custom_query(sql, (like, like, like))
