# -*- coding: utf-8 -*-
"""DAO - Categoría (Catálogo)."""
from .base_model import BaseModel


class CategoriaModel(BaseModel):
    TABLE_NAME = "categoria"
    PK_COLUMN = "categoria_id"

    def get_raices(self) -> list[dict]:
        """Obtiene categorías de nivel 0 (raíz)."""
        sql = "SELECT * FROM categoria WHERE nivel = 0 AND estado = 'ACT' ORDER BY nombre"
        return self.custom_query(sql)

    def get_hijas(self, categoria_padre_id: int) -> list[dict]:
        """Obtiene subcategorías de una categoría padre."""
        return self.get_by_field("categoria_padre_id", categoria_padre_id)

    def get_con_conteo_productos(self) -> list[dict]:
        """Categorías con cantidad de productos activos."""
        sql = """SELECT c.*, COUNT(p.producto_id) as total_productos
                 FROM categoria c
                 LEFT JOIN producto p ON c.categoria_id = p.categoria_id AND p.estado = 'ACT'
                 WHERE c.estado = 'ACT'
                 GROUP BY c.categoria_id
                 ORDER BY c.nombre"""
        return self.custom_query(sql)

    def tiene_productos_activos(self, categoria_id: int) -> bool:
        sql = "SELECT 1 FROM producto WHERE categoria_id = ? AND estado = 'ACT' LIMIT 1"
        return self.db.fetch_one(sql, (categoria_id,)) is not None
