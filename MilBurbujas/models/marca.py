# -*- coding: utf-8 -*-
"""DAO - Marca (Catálogo)."""
from .base_model import BaseModel


class MarcaModel(BaseModel):
    TABLE_NAME = "marca"
    PK_COLUMN = "marca_id"

    def get_con_lineas(self) -> list[dict]:
        """Marcas con sus líneas de productos."""
        sql = """SELECT m.*, COUNT(lp.linea_id) as total_lineas
                 FROM marca m
                 LEFT JOIN linea_producto lp ON m.marca_id = lp.marca_id AND lp.estado = 'ACT'
                 WHERE m.estado = 'ACT'
                 GROUP BY m.marca_id
                 ORDER BY m.nombre"""
        return self.custom_query(sql)
