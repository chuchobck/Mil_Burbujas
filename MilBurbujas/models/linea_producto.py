# -*- coding: utf-8 -*-
"""DAO - Línea de Producto (Catálogo)."""
from .base_model import BaseModel


class LineaProductoModel(BaseModel):
    TABLE_NAME = "linea_producto"
    PK_COLUMN = "linea_id"

    def get_by_marca(self, marca_id: int) -> list[dict]:
        return self.get_by_field("marca_id", marca_id)

    def get_con_marca(self) -> list[dict]:
        sql = """SELECT lp.*, m.nombre as marca_nombre
                 FROM linea_producto lp
                 JOIN marca m ON lp.marca_id = m.marca_id
                 WHERE lp.estado = 'ACT'
                 ORDER BY m.nombre, lp.nombre"""
        return self.custom_query(sql)
