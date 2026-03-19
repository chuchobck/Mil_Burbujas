# -*- coding: utf-8 -*-
"""DAO - Ajuste de Inventario."""
from .base_model import BaseModel


class AjusteInventarioModel(BaseModel):
    TABLE_NAME = "ajuste_inventario"
    PK_COLUMN = "ajuste_id"

    def get_completos(self) -> list[dict]:
        sql = """SELECT ai.*,
                        p.nombre AS producto_nombre, p.codigo_barras AS producto_codigo,
                        pc.nombre AS producto_cambio_nombre,
                        u.nombre_completo AS usuario_nombre
                 FROM ajuste_inventario ai
                 JOIN producto p    ON ai.producto_id = p.producto_id
                 LEFT JOIN producto pc ON ai.producto_cambio_id = pc.producto_id
                 JOIN usuario u     ON ai.usuario_id = u.usuario_id
                 WHERE ai.estado = 'ACT'
                 ORDER BY ai.fecha_creacion DESC"""
        return self.custom_query(sql)

    def get_by_producto(self, producto_id: int) -> list[dict]:
        sql = """SELECT ai.*, u.nombre_completo AS usuario_nombre
                 FROM ajuste_inventario ai
                 JOIN usuario u ON ai.usuario_id = u.usuario_id
                 WHERE ai.producto_id = ? AND ai.estado = 'ACT'
                 ORDER BY ai.fecha_creacion DESC"""
        return self.custom_query(sql, (producto_id,))

    def get_by_tipo(self, tipo_ajuste: str) -> list[dict]:
        return self.get_by_field("tipo_ajuste", tipo_ajuste)

    def get_del_dia(self, fecha: str = None) -> list[dict]:
        sql = """SELECT ai.*, p.nombre AS producto_nombre
                 FROM ajuste_inventario ai
                 JOIN producto p ON ai.producto_id = p.producto_id
                 WHERE date(ai.fecha_creacion) = COALESCE(?, date('now', 'localtime'))
                   AND ai.estado = 'ACT'
                 ORDER BY ai.fecha_creacion"""
        return self.custom_query(sql, (fecha,))
