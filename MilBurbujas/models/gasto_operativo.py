# -*- coding: utf-8 -*-
"""DAO - Gasto Operativo (Financiero)."""
from .base_model import BaseModel


class GastoOperativoModel(BaseModel):
    TABLE_NAME = "gasto_operativo"
    PK_COLUMN = "gasto_id"

    def get_by_periodo(self, fecha_inicio: str, fecha_fin: str) -> list[dict]:
        sql = """SELECT go.*, u.nombre_completo AS usuario_nombre
                 FROM gasto_operativo go
                 JOIN usuario u ON go.usuario_id = u.usuario_id
                 WHERE go.fecha_gasto BETWEEN ? AND ? AND go.estado = 'ACT'
                 ORDER BY go.fecha_gasto DESC"""
        return self.custom_query(sql, (fecha_inicio, fecha_fin))

    def get_total_periodo(self, fecha_inicio: str, fecha_fin: str) -> float:
        sql = """SELECT COALESCE(SUM(monto), 0) as total
                 FROM gasto_operativo
                 WHERE fecha_gasto BETWEEN ? AND ? AND estado = 'ACT'"""
        result = self.custom_query_one(sql, (fecha_inicio, fecha_fin))
        return result["total"] if result else 0.0

    def get_del_dia(self, fecha: str = None) -> list[dict]:
        sql = """SELECT * FROM gasto_operativo
                 WHERE fecha_gasto = COALESCE(?, date('now', 'localtime'))
                   AND estado = 'ACT'
                 ORDER BY gasto_id"""
        return self.custom_query(sql, (fecha,))

    def get_total_dia(self, fecha: str = None) -> float:
        sql = """SELECT COALESCE(SUM(monto), 0) as total
                 FROM gasto_operativo
                 WHERE fecha_gasto = COALESCE(?, date('now', 'localtime'))
                   AND estado = 'ACT'"""
        result = self.custom_query_one(sql, (fecha,))
        return result["total"] if result else 0.0

    def get_por_tipo(self, fecha_inicio: str, fecha_fin: str) -> list[dict]:
        """Gastos agrupados por tipo en un período."""
        sql = """SELECT tipo_gasto, SUM(monto) as total, COUNT(*) as cantidad
                 FROM gasto_operativo
                 WHERE fecha_gasto BETWEEN ? AND ? AND estado = 'ACT'
                 GROUP BY tipo_gasto
                 ORDER BY total DESC"""
        return self.custom_query(sql, (fecha_inicio, fecha_fin))
