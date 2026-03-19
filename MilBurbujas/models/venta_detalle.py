# -*- coding: utf-8 -*-
"""DAO - Venta Detalle."""
from .base_model import BaseModel


class VentaDetalleModel(BaseModel):
    TABLE_NAME = "venta_detalle"
    PK_COLUMN = "venta_detalle_id"
    HAS_ESTADO = False

    def get_by_venta(self, venta_id: int) -> list[dict]:
        sql = """SELECT vd.*, p.nombre AS producto_nombre, p.codigo_barras AS producto_codigo
                 FROM venta_detalle vd
                 JOIN producto p ON vd.producto_id = p.producto_id
                 WHERE vd.venta_id = ?
                 ORDER BY vd.venta_detalle_id"""
        return self.custom_query(sql, (venta_id,))

    def get_by_producto(self, producto_id: int) -> list[dict]:
        """Historial de ventas de un producto."""
        sql = """SELECT vd.*, v.numero_comprobante, v.fecha_venta
                 FROM venta_detalle vd
                 JOIN venta v ON vd.venta_id = v.venta_id
                 WHERE vd.producto_id = ? AND v.estado = 'COMPLETADA'
                 ORDER BY v.fecha_venta DESC"""
        return self.custom_query(sql, (producto_id,))

    def get_mas_vendidos(self, limite: int = 10) -> list[dict]:
        """Top productos más vendidos."""
        sql = """SELECT p.producto_id, p.nombre, p.codigo_barras,
                        SUM(vd.cantidad) as total_vendido,
                        SUM(vd.subtotal) as total_ingreso
                 FROM venta_detalle vd
                 JOIN producto p ON vd.producto_id = p.producto_id
                 JOIN venta v    ON vd.venta_id = v.venta_id
                 WHERE v.estado = 'COMPLETADA'
                 GROUP BY p.producto_id
                 ORDER BY total_vendido DESC
                 LIMIT ?"""
        return self.custom_query(sql, (limite,))
