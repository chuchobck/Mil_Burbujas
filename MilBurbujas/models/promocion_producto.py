# -*- coding: utf-8 -*-
"""DAO - Promoción-Producto (relación N:M)."""
from .base_model import BaseModel


class PromocionProductoModel(BaseModel):
    TABLE_NAME = "promocion_producto"
    PK_COLUMN = "promo_producto_id"
    HAS_ESTADO = False

    def get_by_promocion(self, promocion_id: int) -> list[dict]:
        sql = """SELECT pp.*, p.nombre AS producto_nombre, p.codigo_barras, p.stock_actual
                 FROM promocion_producto pp
                 JOIN producto p ON pp.producto_id = p.producto_id
                 WHERE pp.promocion_id = ?"""
        return self.custom_query(sql, (promocion_id,))

    def get_by_producto(self, producto_id: int) -> list[dict]:
        sql = """SELECT pp.*, pr.nombre AS promocion_nombre, pr.activa
                 FROM promocion_producto pp
                 JOIN promocion pr ON pp.promocion_id = pr.promocion_id
                 WHERE pp.producto_id = ?"""
        return self.custom_query(sql, (producto_id,))

    def delete_by_promocion(self, promocion_id: int) -> bool:
        """Elimina todos los productos de una promoción (para reconstruir)."""
        sql = "DELETE FROM promocion_producto WHERE promocion_id = ?"
        cursor = self.db.execute(sql, (promocion_id,))
        return cursor.rowcount > 0
