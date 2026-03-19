# -*- coding: utf-8 -*-
"""DAO - Precio de Referencia (supermercados)."""
from .base_model import BaseModel


class PrecioReferenciaModel(BaseModel):
    TABLE_NAME = "precio_referencia"
    PK_COLUMN = "precio_ref_id"
    HAS_ESTADO = False

    def get_by_producto(self, producto_id: int) -> list[dict]:
        sql = """SELECT * FROM precio_referencia
                 WHERE producto_id = ?
                 ORDER BY fecha_consulta DESC"""
        return self.custom_query(sql, (producto_id,))

    def get_comparativo(self, producto_id: int) -> list[dict]:
        """Comparativo: precios de proveedores vs supermercados."""
        sql = """SELECT 'PROVEEDOR' as fuente, p.razon_social as nombre,
                        pp.precio_compra as precio, pp.fecha_ultimo_precio as fecha
                 FROM proveedor_producto pp
                 JOIN proveedor p ON pp.proveedor_id = p.proveedor_id
                 WHERE pp.producto_id = ? AND pp.estado = 'ACT'
                 UNION ALL
                 SELECT origen as fuente, nombre_comercio as nombre,
                        precio, fecha_consulta as fecha
                 FROM precio_referencia
                 WHERE producto_id = ?
                 ORDER BY precio ASC"""
        return self.custom_query(sql, (producto_id, producto_id))
