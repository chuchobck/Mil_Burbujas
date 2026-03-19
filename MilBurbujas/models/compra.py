# -*- coding: utf-8 -*-
"""DAO - Compra (cabecera)."""
from .base_model import BaseModel


class CompraModel(BaseModel):
    TABLE_NAME = "compra"
    PK_COLUMN = "compra_id"
    HAS_ESTADO = True

    def get_by_factura_proveedor(self, numero_factura: str, proveedor_id: int) -> dict | None:
        sql = "SELECT * FROM compra WHERE numero_factura = ? AND proveedor_id = ?"
        return self.custom_query_one(sql, (numero_factura, proveedor_id))

    def get_completas(self, only_active: bool = True) -> list[dict]:
        """Compras con nombre de proveedor."""
        estado_filter = "AND c.estado != 'ANULADA'" if only_active else ""
        sql = f"""SELECT c.*, p.razon_social AS proveedor_nombre, u.nombre_completo AS usuario_nombre
                  FROM compra c
                  JOIN proveedor p ON c.proveedor_id = p.proveedor_id
                  JOIN usuario u   ON c.usuario_id = u.usuario_id
                  {estado_filter}
                  ORDER BY c.fecha_compra DESC"""
        return self.custom_query(sql)

    def get_by_proveedor(self, proveedor_id: int) -> list[dict]:
        sql = """SELECT * FROM compra
                 WHERE proveedor_id = ? AND estado != 'ANULADA'
                 ORDER BY fecha_compra DESC"""
        return self.custom_query(sql, (proveedor_id,))

    def get_by_periodo(self, fecha_inicio: str, fecha_fin: str) -> list[dict]:
        sql = """SELECT c.*, p.razon_social AS proveedor_nombre
                 FROM compra c
                 JOIN proveedor p ON c.proveedor_id = p.proveedor_id
                 WHERE c.fecha_compra BETWEEN ? AND ? AND c.estado != 'ANULADA'
                 ORDER BY c.fecha_compra DESC"""
        return self.custom_query(sql, (fecha_inicio, fecha_fin))

    def get_total_periodo(self, fecha_inicio: str, fecha_fin: str) -> float:
        sql = """SELECT COALESCE(SUM(total), 0) as total
                 FROM compra
                 WHERE fecha_compra BETWEEN ? AND ? AND estado != 'ANULADA'"""
        result = self.custom_query_one(sql, (fecha_inicio, fecha_fin))
        return result["total"] if result else 0.0

    def deactivate(self, record_id: int) -> bool:
        return self.update(record_id, {"estado": "ANULADA"})

    def get_total_contado_dia(self, fecha: str) -> float:
        """Total de compras al contado del dia (efectivo que sale de caja)."""
        sql = """SELECT COALESCE(SUM(total), 0) as total
                 FROM compra
                 WHERE fecha_compra = ? AND estado != 'ANULADA'
                   AND tipo_pago = 'CONTADO'"""
        result = self.custom_query_one(sql, (fecha,))
        return result["total"] if result else 0.0
