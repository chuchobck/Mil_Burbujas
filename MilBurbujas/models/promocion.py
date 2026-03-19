# -*- coding: utf-8 -*-
"""DAO - Promoción."""
from .base_model import BaseModel


class PromocionModel(BaseModel):
    TABLE_NAME = "promocion"
    PK_COLUMN = "promocion_id"

    def get_activas(self) -> list[dict]:
        """Promociones activas y vigentes hoy."""
        sql = """SELECT * FROM promocion
                 WHERE estado = 'ACT' AND activa = 1
                   AND date(fecha_inicio) <= date('now', 'localtime')
                   AND date(fecha_fin) >= date('now', 'localtime')
                 ORDER BY fecha_fin"""
        return self.custom_query(sql)

    def get_con_productos(self, promocion_id: int) -> list[dict]:
        """Productos incluidos en una promoción."""
        sql = """SELECT pp.*, p.nombre AS producto_nombre, p.codigo_barras,
                        p.precio_venta AS precio_normal, p.precio_referencia_compra AS costo
                 FROM promocion_producto pp
                 JOIN producto p ON pp.producto_id = p.producto_id
                 WHERE pp.promocion_id = ?
                 ORDER BY p.nombre"""
        return self.custom_query(sql, (promocion_id,))

    def get_promocion_producto(self, producto_id: int) -> dict | None:
        """Busca si un producto tiene una promoción activa vigente."""
        sql = """SELECT pr.*, pp.cantidad_en_kit, pp.precio_individual_kit
                 FROM promocion pr
                 JOIN promocion_producto pp ON pr.promocion_id = pp.promocion_id
                 WHERE pp.producto_id = ?
                   AND pr.estado = 'ACT' AND pr.activa = 1
                   AND date(pr.fecha_inicio) <= date('now', 'localtime')
                   AND date(pr.fecha_fin) >= date('now', 'localtime')
                 LIMIT 1"""
        return self.custom_query_one(sql, (producto_id,))
