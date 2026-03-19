# -*- coding: utf-8 -*-
"""DAO - Venta (cabecera)."""
from .base_model import BaseModel


class VentaModel(BaseModel):
    TABLE_NAME = "venta"
    PK_COLUMN = "venta_id"
    HAS_ESTADO = True

    def get_completas(self, only_active: bool = True) -> list[dict]:
        estado_filter = "AND v.estado = 'COMPLETADA'" if only_active else ""
        sql = f"""SELECT v.*,
                         COALESCE(c.nombres || ' ' || c.apellidos, 'Consumidor Final') AS cliente_nombre,
                         u.nombre_completo AS usuario_nombre
                  FROM venta v
                  LEFT JOIN cliente c ON v.cliente_id = c.cliente_id
                  JOIN usuario u      ON v.usuario_id = u.usuario_id
                  {estado_filter}
                  ORDER BY v.fecha_venta DESC"""
        return self.custom_query(sql)

    def get_del_dia(self, fecha: str = None) -> list[dict]:
        """Ventas del día (para cierre de caja)."""
        sql = """SELECT v.*,
                        COALESCE(c.nombres || ' ' || c.apellidos, 'Consumidor Final') AS cliente_nombre
                 FROM venta v
                 LEFT JOIN cliente c ON v.cliente_id = c.cliente_id
                 WHERE date(v.fecha_venta) = COALESCE(?, date('now', 'localtime'))
                   AND v.estado = 'COMPLETADA'
                 ORDER BY v.fecha_venta"""
        return self.custom_query(sql, (fecha,))

    def get_by_periodo(self, fecha_inicio: str, fecha_fin: str) -> list[dict]:
        sql = """SELECT v.*, COALESCE(c.nombres || ' ' || c.apellidos, 'Consumidor Final') AS cliente_nombre
                 FROM venta v
                 LEFT JOIN cliente c ON v.cliente_id = c.cliente_id
                 WHERE date(v.fecha_venta) BETWEEN ? AND ? AND v.estado = 'COMPLETADA'
                 ORDER BY v.fecha_venta DESC"""
        return self.custom_query(sql, (fecha_inicio, fecha_fin))

    def get_total_periodo(self, fecha_inicio: str, fecha_fin: str) -> float:
        sql = """SELECT COALESCE(SUM(total), 0) as total
                 FROM venta
                 WHERE date(fecha_venta) BETWEEN ? AND ? AND estado = 'COMPLETADA'"""
        result = self.custom_query_one(sql, (fecha_inicio, fecha_fin))
        return result["total"] if result else 0.0

    def get_totales_dia(self, fecha: str = None) -> dict:
        """Totales del día por método de pago (para cierre de caja)."""
        sql = """SELECT
                    COALESCE(SUM(CASE WHEN metodo_pago = 'EFECTIVO' THEN total ELSE 0 END), 0) as total_efectivo,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'TRANSFERENCIA' THEN total ELSE 0 END), 0) as total_transferencia,
                    COALESCE(SUM(CASE WHEN es_credito = 1 THEN total ELSE 0 END), 0) as total_credito,
                    COALESCE(SUM(total), 0) as total_general,
                    COUNT(*) as cantidad_ventas
                 FROM venta
                 WHERE date(fecha_venta) = COALESCE(?, date('now', 'localtime'))
                   AND estado = 'COMPLETADA'"""
        return self.custom_query_one(sql, (fecha,))

    def deactivate(self, record_id: int) -> bool:
        return self.update(record_id, {"estado": "ANULADA"})
